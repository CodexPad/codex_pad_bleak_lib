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

| CodexPad Model | Details |
| :--- | :--- |
| CodexPad-C10 | [Product Details](../../../codex_pad_c10/blob/main/README.md#codexpad-c10) |
| CodexPad-S10 | [Product Details](../../../codex_pad_s10/blob/main/README.md#codexpad-s10) |

## Features

- **Flexible dual-mode connection**:

  - **Direct connection by address**: Quickly establish a stable connection to a specific gamepad using its known **Bluetooth device address**.

  - **Button-mask scan & connect**: No need to know the **Bluetooth device address** in advance. The library scans for nearby devices and automatically connects to the one with the strongest signal (maximum RSSI) that matches a user-defined button combination (a "button mask") being held on the gamepad — enabling fast and flexible pairing.

- **Real-time button event detection**: Read the input state of all buttons in real time, and distinguish among three events: **press**, **release**, and **hold**.

- **High-precision joystick data**: Obtain analog values for the X and Y axes of both joysticks, ranging from 0 to 255, providing precise control input.

- **Adjustable transmit power**: Dynamically adjust the Bluetooth transmit power within the range of -16 dBm to +6 dBm to suit different application scenarios (e.g., distance and power consumption requirements).

## Button-Mask Scan & Connect

### Design Intent and Advantages

1. **Prevent accidental connections and interference**: When multiple connectable devices of the same type (for example, several gamepads) are nearby, connecting by unique address is precise but typically requires "hardcoding" that address in the code. This binds the program to a specific device and lacks flexibility. By requiring the target device to be holding a specific button combination when discovered, you define a dynamic, condition-based connection rule. Your connection code no longer needs to bind to any device's physical address — any device that satisfies this "handshake protocol" (holding the correct buttons) will be connected. This both prevents the host from accidentally connecting to the wrong device among many, and enables the convenience of **connect-on-press, with devices switchable at any time**.

2. **Build an exclusive connection condition**: You can think of this button mask as a simple "password" or "connection token." It establishes an exclusive connection channel between your application and the device — only devices that satisfy this specific physical interaction condition (holding the designated buttons) can join, enhancing the intentionality and controllability of the connection.

3. **Improve code flexibility and support on-the-fly device switching**: Unlike hardcoding a specific device address, the button-mask connection logic is oriented toward "conditions" rather than "specific devices." This means the same connection code, with no modification, can connect to any gamepad that is in a discoverable state and correctly triggers the preset button condition. This brings two major benefits:

    - **No binding to a specific device**: You do not need to specify a particular gamepad's address in your code, nor maintain separate connection configurations for different gamepads.

    - **Connect on press, switch flexibly**: In practice, you can pick up another gamepad at any time; as long as it is powered on and the correct button combination is held, your program will automatically connect to it, enabling seamless switching between different gamepads.

### How It Works — Operation Steps

1. **Set the mask**: Define a **button mask** in your code and pass it to the relevant parameter of the connection function.

2. **Power on the device**: Turn on your gamepad so that it enters the discoverable, awaiting-connection state (the indicator should blink slowly).

3. **Execute the connection**: Run your program. While the program is scanning, precisely hold down all the buttons defined in your mask on the target gamepad.

4. **Automatic pairing**: After scanning a device, the program checks whether its button state exactly matches the preset mask (i.e., all specified buttons are held, and no unspecified buttons are pressed). Once a match is found, the program automatically establishes a connection with the strongest-matching device.

> **⚠️ Important warning**: The button mask must **never** include `BUTTON_HOME` (the Home button). Long-pressing the Home button triggers a system reboot of the gamepad, which will directly interrupt the connection process and leave the device in an unexpected state.

## Usage

### Preparation

Before you start coding, complete the following preparation steps to ensure a smooth development process.

#### Familiarize yourself with the product documentation

- Read the CodexPad product manual thoroughly to fully understand the hardware features, button and joystick layout, function definitions, indicator states, and power on/off operations.

#### Obtain and record the gamepad's Bluetooth device address

> **⚠️ Important note**: The direct-connection example connects by address. **When coding, you must explicitly specify your gamepad's Bluetooth Device Address in the code.**

Refer to the method provided in the product manual to obtain your gamepad's address. Its format is typically `"E4:66:E5:A2:24:5D"` (characters 0-9 and A-F, with half-width colons as separators). Please record this information carefully — you will need to replace it with your own gamepad's actual address later in the code.

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

### Direct connection by address (`example_address_directly_connect.py`)

- **File location**: [example_address_directly_connect.py](example_address_directly_connect.py)
- **Description**: Connects directly to the gamepad by address, detects changes in button state and joystick values, and prints them.
- **Operation steps**:
    1. Open `example_address_directly_connect.py` and find `_BLUETOOTH_DEVICE_ADDRESS = "16:00:00:00:02:72"`. Replace the address in quotes with your own gamepad's address (format like `"E4:66:E5:A2:24:5D"`, uppercase A-F, half-width colons).
    2. Save the file, then run: `python example_address_directly_connect.py`.
    3. The program will automatically scan and connect to the gamepad at that address. Once connected, operate the gamepad normally and view the real-time button and joystick log output in the console. If the connection fails, please try running the program a few more times.

### Scan & connect example (`example_scan_and_connect.py`)

- **File location**: [example_scan_and_connect.py](example_scan_and_connect.py)
- **Description**: Scans for and automatically connects to nearby gamepad devices by matching a specific user-defined **button** or **button combination**, detects joystick and button changes, and prints them.
- **Operation steps**:
    1. Run: `python example_scan_and_connect.py`, after the program starts, it enters the scanning/connection state.
    2. The gamepad's blue light blinks after it is powered on.
    3. **Hold down the button mask (button combination) specified in your code on the gamepad — by default Start + Cross(A) held simultaneously — and keep holding it** until the host successfully connects to the gamepad. Once connected, operate the gamepad normally and view the real-time log output in the console.

**⚠️ Debugging notes**:

During development and debugging, `Ctrl+C` is often used to interrupt the program. Note that after the program process terminates, the underlying OS-level Bluetooth connection may not be disconnected immediately. If you re-run the program at this point, you may encounter connection failures or be unable to find the device.
**Solution**: Reboot the gamepad so that it exits the connected state and re-enters discoverable mode (slow blue blinking).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
