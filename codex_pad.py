import struct
import bleak
import asyncio
import threading
from collections import deque

__version__ = "2.0.0"

BUTTON_UP = 1 << 0
BUTTON_DOWN = 1 << 1
BUTTON_LEFT = 1 << 2
BUTTON_RIGHT = 1 << 3
BUTTON_SQUARE_X = 1 << 4
BUTTON_TRIANGLE_Y = 1 << 5
BUTTON_CROSS_A = 1 << 6
BUTTON_CIRCLE_B = 1 << 7
BUTTON_L1 = 1 << 8
BUTTON_L2 = 1 << 9
BUTTON_L3 = 1 << 10
BUTTON_R1 = 1 << 11
BUTTON_R2 = 1 << 12
BUTTON_R3 = 1 << 13
BUTTON_SELECT = 1 << 14
BUTTON_START = 1 << 15
BUTTON_HOME = 1 << 16

# 摇杆轴索引常量
AXIS_LEFT_STICK_X = 0
AXIS_LEFT_STICK_Y = 1
AXIS_RIGHT_STICK_X = 2
AXIS_RIGHT_STICK_Y = 3

AXIS_CENTER = 0x80  # 摇杆中心值

_GAP_SERVICE_UUID = "00001800-0000-1000-8000-00805f9b34fb"
_GAP_DEVICE_NAME_UUID = "00002a00-0000-1000-8000-00805f9b34fb"

_INPUTS_SERVICE_UUID = "0000ffa0-0000-1000-8000-00805f9b34fb"
_INPUTS_CHARACTERISTIC_UUID = "0000ffa1-0000-1000-8000-00805f9b34fb"

_DEVICE_INFO_SERVICE_UUID = "0000180a-0000-1000-8000-00805f9b34fb"
_MODEL_NUMBER_STRING_UUID = "00002a24-0000-1000-8000-00805f9b34fb"
_SERIAL_NUMBER_STRING_UUID = "00002a25-0000-1000-8000-00805f9b34fb"
_FIRMWARE_REVISION_STRING_UUID = "00002a26-0000-1000-8000-00805f9b34fb"
_MANUFACTURER_NAME_STRING_UUID = "00002a29-0000-1000-8000-00805f9b34fb"

_MANUFACTURER_HEADER = "CodexPad".encode("utf-8")

_BUTTON_STATE_UNPACK_FMT = "I"
_FIRMWARE_VERSION_UNPACK_FMT = "BBB"
_MANUFACTURER_HEADER_UNPACK_FMT = "B" * len(_MANUFACTURER_HEADER)

_MANUFACTURER_FIRMWARE_VERSION_LENGTH = len(_FIRMWARE_VERSION_UNPACK_FMT)
_MANUFACTURER_DATA_LENGTH = len(_MANUFACTURER_HEADER) + _MANUFACTURER_FIRMWARE_VERSION_LENGTH + 4 + 1
_MANUFACTURER_DATA_UNPACK_FMT = "<" + _MANUFACTURER_HEADER_UNPACK_FMT + _FIRMWARE_VERSION_UNPACK_FMT + _BUTTON_STATE_UNPACK_FMT + "B"

_AXIS_VALUE_UNPACK_FMT = "BBBB"
_INPUTS_UNPACK_FMT = "<" + _BUTTON_STATE_UNPACK_FMT + _AXIS_VALUE_UNPACK_FMT
_INPUTS_DATA_LENGTH = 8


class CodexPadNotFoundError(Exception):
    pass

def _validate_address(address: str):
    parts = address.split(':')
    if len(parts) != 6:
        raise ValueError(f"address must be in format 'XX:XX:XX:XX:XX:XX', got '{address}'")

    for part in parts:
        if len(part) != 2:
            raise ValueError(f"address: '{part}' is not a 2-char hex byte")
        for c in part:
            if c not in '0123456789ABCDEFabcdef':
                raise ValueError(f"address: '{address}' contains non-hex char '{c}'")

class CodexPadClient:

    class InputState:

        def __init__(self):
            self.button_mask = 0
            self.axes = [AXIS_CENTER, AXIS_CENTER, AXIS_CENTER, AXIS_CENTER]

        def parse_and_set(self, data: bytes):
            if not data or len(data) != _INPUTS_DATA_LENGTH:
                return
            [
                self.button_mask,
                self.axes[AXIS_LEFT_STICK_X],
                self.axes[AXIS_LEFT_STICK_Y],
                self.axes[AXIS_RIGHT_STICK_X],
                self.axes[AXIS_RIGHT_STICK_Y],
            ] = struct.unpack(_INPUTS_UNPACK_FMT, data)

        def assign(self, other):
            self.button_mask = other.button_mask
            self.axes = other.axes[:]

    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(
            target=self._loop.run_forever,
            name="CodexPadClientLoop",
            daemon=True
        )
        self._loop_thread.start()

        self._remote_model_number = None
        self._remote_device_name = None
        self._remote_firmware_version = None
        self._client = None
        self._inputs_characteristic = None
        self._input_queue = deque(maxlen=5)
        self._lock = threading.Lock()
        self._prev_inputs = CodexPadClient.InputState()
        self._current_inputs = CodexPadClient.InputState()

    def _run_coro(self, coro):
        """
        在 BLE 线程的 loop 中运行协程，并阻塞等待结果
        """
        if self._loop is None:
            raise RuntimeError("Event loop not started")

        fut = asyncio.run_coroutine_threadsafe(coro, self._loop)

        return fut.result()  # 阻塞，直到完成

    async def _reset(self):
        self._remote_model_number = None
        self._remote_device_name = None
        self._remote_firmware_version = None
        if self._client:
            await self._client.disconnect()
        self._client = None
        self._inputs_characteristic = None
        self._prev_inputs = CodexPadClient.InputState()
        self._current_inputs = CodexPadClient.InputState()
        with self._lock:
            self._input_queue.clear()


    def _on_notify(self, _, data: bytearray):
        with self._lock:
            self._input_queue.append(data)

    async def _connect_by_button_mask(self, button_mask, scan_timeout, connect_timeout):
        result_device = None
        scanner = bleak.BleakScanner()
        devices = await scanner.discover(timeout=scan_timeout, return_adv=True)
        for address, (device, adv_data) in devices.items():
            if not device.name or not device.name.startswith("CodexPad-"):
                continue

            # print(f"address: {address}, device: {device}, adv_data: {adv_data}")

            if not adv_data or not adv_data.manufacturer_data:
                continue

            if not 0xFFFF in adv_data.manufacturer_data:
                continue

            manufacturer_data = adv_data.manufacturer_data[0xFFFF]

            if len(manufacturer_data) < _MANUFACTURER_DATA_LENGTH:
                continue

            unpacked = struct.unpack(_MANUFACTURER_DATA_UNPACK_FMT, manufacturer_data[:_MANUFACTURER_DATA_LENGTH])

            header_bytes = bytes(unpacked[: len(_MANUFACTURER_HEADER)])

            if header_bytes != _MANUFACTURER_HEADER:
                continue

            firmware_version = bytes(unpacked[len(_MANUFACTURER_HEADER) : len(_MANUFACTURER_HEADER) + _MANUFACTURER_FIRMWARE_VERSION_LENGTH])

            current_button_mask = unpacked[len(_MANUFACTURER_HEADER) + _MANUFACTURER_FIRMWARE_VERSION_LENGTH]

            if current_button_mask != button_mask:
                continue

            button_mask_duration_seconds = unpacked[-1]

            if firmware_version[0] > 1 and button_mask_duration_seconds < 1:
                continue

            if result_device is None or device.rssi > result_device.rssi:
                result_device = device

        if not result_device:
            raise CodexPadNotFoundError(f"No CodexPad device found with button mask 0x{button_mask:08X}")

        await self._connect(bleak.BleakClient(result_device, timeout=connect_timeout))

    def connect_by_button_mask(self, button_mask, scan_timeout=1, connect_timeout=30):
        if not isinstance(button_mask, int):
            raise TypeError(f"button_mask must be int, got {type(button_mask).__name__}")

        return self._run_coro(self._connect_by_button_mask(button_mask, scan_timeout, connect_timeout))

    def connect_by_address(self, address, timeout):
        if not isinstance(address, str):
            raise TypeError(f"address must be str, got {type(address).__name__}")
        _validate_address(address)
        return self._run_coro(self._connect(bleak.BleakClient(address_or_ble_device=address, timeout=timeout)))

    async def _connect(self, client):
        await self._reset()
        try:
            await client.connect()
            self._client = client

            characteristic = self._client.services.get_characteristic(_GAP_DEVICE_NAME_UUID)
            self._remote_device_name = (await self._client.read_gatt_char(characteristic)).decode("utf-8")

            characteristic = self._client.services.get_characteristic(_MODEL_NUMBER_STRING_UUID)
            self._remote_model_number = (await self._client.read_gatt_char(characteristic)).decode("utf-8")

            characteristic = self._client.services.get_characteristic(_FIRMWARE_REVISION_STRING_UUID)
            firmware_bytes = await self._client.read_gatt_char(characteristic)
            self._remote_firmware_version = struct.unpack(_FIRMWARE_VERSION_UNPACK_FMT, firmware_bytes)

            characteristic = self._client.services.get_characteristic(_INPUTS_CHARACTERISTIC_UUID)

            await self._client.start_notify(characteristic, callback=self._on_notify)

        except Exception as e:
            await self._reset()
            raise e

    def disconnect(self):
        self._run_coro(self._reset())

    @property
    def remote_device_name(self):
        return self._remote_device_name

    @property
    def remote_model_number(self):
        return self._remote_model_number

    @property
    def remote_firmware_version(self):
        return self._remote_firmware_version

    @property
    def remote_firmware_version_major(self):
        return self._remote_firmware_version[0]

    @property
    def remote_firmware_version_minor(self):
        return self._remote_firmware_version[1]

    @property
    def remote_firmware_version_patch(self):
        return self._remote_firmware_version[2]

    @property
    def remote_address(self):
        return self._client.address

    @property
    def is_connected(self):
        return self._client and self._client.is_connected

    def update(self):
        self._prev_inputs.assign(self._current_inputs)

        if not self.is_connected:
            self._current_inputs = CodexPadClient.InputState()
            return

        with self._lock:
            if len(self._input_queue) > 0:
                self._current_inputs.parse_and_set(self._input_queue.popleft())

    def pressed(self, button):
        return ((self._prev_inputs.button_mask & button) == 0) and ((self._current_inputs.button_mask & button) != 0)

    def released(self, button):
        return ((self._prev_inputs.button_mask & button) != 0) and ((self._current_inputs.button_mask & button) == 0)

    def holding(self, button):
        return ((self._prev_inputs.button_mask & button) != 0) and ((self._current_inputs.button_mask & button) != 0)

    def down(self, button):
        return (self._current_inputs.button_mask & button) == button

    @property
    def button_mask(self) -> int:
        return self._current_inputs.button_mask

    def axis_value(self, axis):
        return self._current_inputs.axes[axis]

    @property
    def axes(self):
        return tuple(self._current_inputs.axes)

    def _has_axis_value_changed_significantly(self, prev_value, current_value, threshold):
        return prev_value != current_value and (current_value == 0 or current_value == 255 or abs(current_value - prev_value) >= threshold)

    def has_axis_value_changed(self, axis, threshold):
        return self._has_axis_value_changed_significantly(self._prev_inputs.axes[axis], self._current_inputs.axes[axis], threshold)
