# CodexPad Bleak Lib

[中文](README.zh-CN.md)

## Overview

**CodexPad Bleak Lib** is a Python Bluetooth Low Energy (BLE) communication library for the CodexPad series of gamepads.

This library is built on top of the mature, cross-platform BLE library [bleak](https://bleak.readthedocs.io). Bleak (Bluetooth Low Energy platform Agnostic Klient) is an asynchronous, cross-platform GATT client that supports scanning, connecting, reading/writing characteristics, and subscribing to notifications with BLE peripherals such as the CodexPad gamepad.

Thanks to **bleak**'s excellent cross-platform support, this library runs seamlessly on the following operating systems and devices:

- Windows 10 (version 16299 or later)
- macOS (10.15 or later)
- Linux distributions (systems with BlueZ >= 5.55, including embedded devices such as **Raspberry Pi**)

Whether you are developing on a desktop computer or an embedded platform such as a Raspberry Pi, you can use this library to easily communicate with a CodexPad gamepad over BLE.

## Features

- **Flexible Dual-Mode Connection**:
  - **Direct Connection via Address**: Quickly establish a stable connection with a specific controller using a known Bluetooth Device Address.
  - **Button Mask Connection**: By scanning for and matching a specific combination of buttons held down on the target controller (defined as a "button mask" in your code), the library automatically connects to the device with the strongest signal (highest RSSI), enabling fast and flexible pairing.
- **Real-time Button Event Detection**: Reads the input status of all buttons in real time, distinguishing between **Pressed**, **Released**, and **Holding** events.
- **High-Precision Joystick Data**: Retrieves analog values for the X and Y axes of the left and right joysticks, ranging from 0 to 255, providing precise control input.

## Usage

### Preparation

Before you start coding, complete the following preparation steps to ensure a smooth development process.

#### Familiarize yourself with the product documentation

- Read the CodexPad product manual thoroughly to fully understand the hardware features, button and joystick layout, function definitions, indicator states, obtaining address, and power on/off operations.

#### Install bleak

This library depends on the `bleak` library. Choose the installation method according to your operating system:

- Recommended, universal way:

    ```shell
    pip install bleak
    ```

- Linux / Raspberry Pi (apt way):

    ```shell
    sudo apt-get update
    sudo apt install python3-bleak
    ```

> 💡 Note:
> Windows and macOS users can simply use `pip install bleak` without any additional system dependencies.
> Linux distributions (including Raspberry Pi) require BlueZ (>= 5.55). You can check the current version with the command `bluetoothctl version`.

#### Enable Bluetooth

The way to enable Bluetooth differs across operating systems. Make sure the Bluetooth hardware is enabled, not soft-blocked, and that the Bluetooth service is running properly.

- **Windows**:
  - Go to Settings → Bluetooth & devices, and make sure the Bluetooth switch is **On**.

- **macOS**:
  - Go to System Settings → Bluetooth, and make sure Bluetooth is **On**.

- **Linux / Raspberry Pi**:

    ```shell
    # Unblock Bluetooth (if applicable)
    sudo rfkill unblock bluetooth

    # Enable and start the Bluetooth service
    sudo systemctl enable bluetooth
    sudo systemctl start bluetooth

    # Verify the Bluetooth state
    bluetoothctl show
    ```

When running the Python program on Linux, the current user must be added to the `bluetooth` group, otherwise the connection may fail due to insufficient permissions:

```shell
sudo usermod -aG bluetooth $USER
# Log out and back in, or reboot, for this to take effect
```

#### Power on the gamepad and enter the awaiting-connection state

- After powering on the gamepad, it automatically enters the **awaiting-connection state** in which it is discoverable over Bluetooth. The gamepad indicator should show a **slow blinking state (about one blink per second)**.

## Examples

> **⚠️ Runtime Environment Notice**:
>
> The `import codex_pad` statement in the examples depends on the `codex_pad.py` library file located in the repository root. **Do NOT copy the example files to another directory and run them there**, or you will get a `ModuleNotFoundError`.
>
> You have three options to run the examples correctly:
>
> 1. **Run directly from the repository root (recommended)**: After cloning/downloading the repo, run `python example_xxx.py` from the directory containing `codex_pad.py`.
> 2. **Copy the library file together**: If you must move the example file, also copy `codex_pad.py` to the same directory.
> 3. **Install the library in editable mode**: If you want to be able to `import codex_pad` from anywhere, run the following in the repository root:
>
>    ```shell
>    pip install -e .
>    ```

The example code contains detailed inline comments; it is recommended that you read the source files directly for the most complete information. The following briefly introduces the core functionality and expected behavior of each example to help you get started quickly.

### Direct connection by address (`example_connect_by_button_mask.py`)

- **File location**: [example_connect_by_button_mask.py](example_connect_by_button_mask.py)
- **Description**: Connects directly to the gamepad by address, detects changes in button state and joystick values, and prints them.
- **Operation steps**:
    1. Open `example_connect_by_button_mask.py` and find `_BLUETOOTH_DEVICE_ADDRESS = "16:00:00:00:02:72"`. Replace the address in quotes with your own gamepad's address (format like `"E4:66:E5:A2:24:5D"`, uppercase A-F, half-width colons).
    2. Save the file, then run: `python example_connect_by_button_mask.py`.
    3. The program will automatically scan and connect to the gamepad at that address. Once connected, operate the gamepad normally and view the real-time button and joystick log output in the console. If the connection fails, please try running the program a few more times.

### Button mask connection example (`example_connect_by_button_mask.py`)

- **File location**: [example_connect_by_button_mask.py](example_connect_by_button_mask.py)
- **Description**: Scans for and automatically connects to nearby gamepad devices by matching a specific user-defined **button** or **button combination**, detects joystick and button changes, and prints them.

> ⚠️ **Known Issue on Raspberry Pi (Bleak Stack)**:
> The "Button Mask Connection" feature currently has a bug when using the `bleak` stack on Raspberry Pi (and potentially other Linux distributions). It may fail to connect. This feature works normally on Windows.
> A solution may be provided in the future. In the meantime, users can try switching to a different Bluetooth stack or explore other workarounds on their own.

- **Operation steps**:
    1. Run: `python example_connect_by_button_mask.py`, after the program starts, it enters the scanning/connection state.
    2. The gamepad's signal light blinks after it is powered on.
    3. **Hold down the button mask (button combination) specified in your code on the gamepad — by default Start + Cross(A) held simultaneously — and keep holding it** until the host successfully connects to the gamepad. Once connected, operate the gamepad normally and view the real-time log output in the console.

**⚠️ Debugging notes**:

During development and debugging, `Ctrl+C` is often used to interrupt the program. Note that after the program process terminates, the underlying OS-level Bluetooth connection may not be disconnected immediately. If you re-run the program at this point, you may encounter connection failures or be unable to find the device.
**Solution**: Reboot the gamepad so that it exits the connected state and re-enters discoverable mode (slow blue blinking).

## Button Mask Connection Explained

Details: [Button Mask Connection Explained](../../../codex_pad_guide/blob/main/button_mask_connection_explained.md#button-mask-connection-explained)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
