import codex_pad
import asyncio
import bleak
import time

_BLUETOOTH_DEVICE_ADDRESS = "16:00:00:00:02:72"


def button_to_string(button):
    """将按钮常量转换为可读的字符串名称"""
    """Convert button constant to readable string name"""
    return {
        codex_pad.BUTTON_UP: "Up",
        codex_pad.BUTTON_DOWN: "Down",
        codex_pad.BUTTON_LEFT: "Left",
        codex_pad.BUTTON_RIGHT: "Right",
        codex_pad.BUTTON_SQUARE_X: "Square(X)",
        codex_pad.BUTTON_TRIANGLE_Y: "Triangle(Y)",
        codex_pad.BUTTON_CROSS_A: "Cross(A)",
        codex_pad.BUTTON_CIRCLE_B: "Circle(B)",
        codex_pad.BUTTON_L1: "L1",
        codex_pad.BUTTON_L2: "L2",
        codex_pad.BUTTON_L3: "L3",
        codex_pad.BUTTON_R1: "R1",
        codex_pad.BUTTON_R2: "R2",
        codex_pad.BUTTON_R3: "R3",
        codex_pad.BUTTON_SELECT: "Select",
        codex_pad.BUTTON_START: "Start",
        codex_pad.BUTTON_HOME: "Home",
    }[button]


codex_pad_client = codex_pad.CodexPadClient()

# Connect to the CodexPad device
# 连接到 CodexPad 设备
def connect(bluetooth_device_address):
    while True:
        try:
            print(f"Connecting to {bluetooth_device_address}")
            codex_pad_client.connect(bluetooth_device_address, timeout=30.0)
            print(f"Remote device name: {codex_pad_client.remote_device_name}")
            print(f"Remote model number: {codex_pad_client.remote_model_number}")
            print(
                f"Remote firmware version: {codex_pad_client.remote_firmware_version_major}.{codex_pad_client.remote_firmware_version_minor}.{codex_pad_client.remote_firmware_version_patch}"
            )
            print(f"Remote Bluetooth Device Address: {codex_pad_client.remote_bluetooth_device_address}")

            # 设置发射功率为0dBm
            # 发射功率影响通信距离和功耗：功率越高，通信距离越远，但功耗也越大
            # 建议根据实际应用场景选择合适的功率等级以平衡距离和电池寿命
            # Set transmission power to 0dBm
            # Transmission power affects communication range and power consumption:
            # Higher power provides longer range but consumes more battery
            # Choose appropriate power level based on your application to balance range and battery life
            # asyncio.run(codex_pad_obj.set_remote_tx_power(codex_pad.TX_POWER_0_DBM))
            print("Connected")
            return
        except bleak.exc.BleakDeviceNotFoundError:
            print("Connection timed out, trying again...")
        except Exception as e:
            print(f"Connection failed: {e}, trying again...")

connect(_BLUETOOTH_DEVICE_ADDRESS)

while True:
    # time.sleep(1)
    codex_pad_client.update()
    
    if not codex_pad_client.is_connected:
        print("Disconnected from device, trying to reconnect...")
        connect(_BLUETOOTH_DEVICE_ADDRESS)
        continue

    # 检测所有按钮的状态变化
    # 使用pressed(), released(), holding()方法检测按钮的不同状态
    # Detect state changes for all buttons
    # Use pressed(), released(), holding() methods to detect different button states
    for button in (
        codex_pad.BUTTON_UP,
        codex_pad.BUTTON_DOWN,
        codex_pad.BUTTON_LEFT,
        codex_pad.BUTTON_RIGHT,
        codex_pad.BUTTON_SQUARE_X,
        codex_pad.BUTTON_TRIANGLE_Y,
        codex_pad.BUTTON_CROSS_A,
        codex_pad.BUTTON_CIRCLE_B,
        codex_pad.BUTTON_L1,
        codex_pad.BUTTON_L2,
        codex_pad.BUTTON_L3,
        codex_pad.BUTTON_R1,
        codex_pad.BUTTON_R2,
        codex_pad.BUTTON_R3,
        codex_pad.BUTTON_SELECT,
        codex_pad.BUTTON_START,
        codex_pad.BUTTON_HOME,
    ):
        # 检测按钮是否刚刚按下（从弹起变为按下）
        # Check if button was just pressed (transition from released to pressed)
        if codex_pad_client.pressed(button):
            print(f"Button {button_to_string(button)}: pressed")

        # 检测按钮是否刚刚释放（从按下变为弹起）
        # Check if button was just released (transition from pressed to released)
        elif codex_pad_client.released(button):
            print(f"Button {button_to_string(button)}: released")

        # 检测按钮是否持续按下状态
        # Check if button is holding
        elif codex_pad_client.holding(button):
            print(f"Button {button_to_string(button)}: holding")

    # 检测摇杆轴值是否发生了有效变化（使用阈值避免微小抖动）
    # 阈值设置为2，只有当摇杆值变化达到或超过2个单位时才认为是有效变化
    # Check if joystick axis values have changed significantly (using threshold to avoid minor jitter)
    # Threshold is set to 2, only consider changes equal to or greater than 2 units as significant
    AXIS_VALUE_CHANGE_THRESHOLD = 2

    # 检测摇杆X轴或Y轴是否有显著变化
    # Check if stick X or Y axis has significant change
    if (
        codex_pad_client.has_axis_value_changed(codex_pad.AXIS_LEFT_STICK_X, AXIS_VALUE_CHANGE_THRESHOLD)
        or codex_pad_client.has_axis_value_changed(codex_pad.AXIS_LEFT_STICK_Y, AXIS_VALUE_CHANGE_THRESHOLD)
        or codex_pad_client.has_axis_value_changed(codex_pad.AXIS_RIGHT_STICK_X, AXIS_VALUE_CHANGE_THRESHOLD)
        or codex_pad_client.has_axis_value_changed(codex_pad.AXIS_RIGHT_STICK_Y, AXIS_VALUE_CHANGE_THRESHOLD)
    ):
        print(
            f"L(X: {codex_pad_client.axis_value(codex_pad.AXIS_LEFT_STICK_X):>3},",
            f"Y: {codex_pad_client.axis_value(codex_pad.AXIS_LEFT_STICK_Y):>3})",
            f"R(X: {codex_pad_client.axis_value(codex_pad.AXIS_RIGHT_STICK_X):>3},",
            f"Y: {codex_pad_client.axis_value(codex_pad.AXIS_RIGHT_STICK_Y):>3})",
        )

