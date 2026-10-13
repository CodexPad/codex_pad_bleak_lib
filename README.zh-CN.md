# CodexPad Bleak Lib

[English](README.md)

## 概述

**CodexPad Bleak Lib** 是一个为 CodexPad 系列手柄提供的 Python 蓝牙低功耗（BLE）通信库。

本库基于成熟的跨平台蓝牙库 [bleak](https://bleak.readthedocs.io) 构建。Bleak（Bluetooth Low Energy platform Agnostic Klient）是一个异步、跨平台的 GATT 客户端，支持与 BLE 外设（如 CodexPad 手柄）进行扫描、连接、特征值读写及通知订阅等操作。

得益于 **bleak** 优秀的跨平台能力，本库可以无缝运行在以下操作系统和设备上：

- Windows 10（版本 16299 或更高）
- macOS（10.15 或更高版本）
- Linux 发行版（包含 BlueZ >= 5.55 的系统，如**树莓派**等嵌入式设备）

无论你是在桌面电脑还是树莓派等嵌入式平台上开发，都可以使用本库轻松实现与手柄的数据交互。

## 特性

- **灵活的双模式连接**：
  - **地址直连**：通过手柄的地址快速与指定手柄建立稳定连接。
  - **按键掩码连接**：通过扫描并匹配目标手柄上被按住的、由用户代码自定义的按键组合（即“按钮掩码”），自动连接信号最强（RSSI最大）的设备，实现快速、灵活的配对。
- **实时按键事件检测**：可实时读取所有按键的输入状态，并区分**按下**、**释放**和**按住**三种事件。
- **高精度摇杆数据**：获取左右摇杆X轴和Y轴的模拟量数值，范围从0至255，提供精准的控制输入。

## 使用说明

### 准备工作

在开始编程前，请完成以下准备工作，以确保开发过程顺利进行。

#### 熟悉产品文档

- 详细阅读 CodexPad 产品手册，全面了解硬件特性、熟悉手柄按键摇杆布局、功能定义、指示灯状态、地址获取以及开关机操作等基本信息。

#### 安装bleak

本库依赖 bleak 库。请根据您的操作系统选择安装方式：

- 通用方式（推荐）：

    ```shell
    pip install bleak
    ```

- Linux / 树莓派（apt 方式）：

    ```shell
    sudo apt-get update
    sudo apt install python3-bleak
    ```

> 💡注意：  
> Windows 和 macOS 用户直接使用 `pip install bleak` 即可，无需额外系统依赖。  
> Linux 发行版（含树莓派）需要确保系统已安装 BlueZ（>= 5.55）。可使用 `bluetoothctl version` 命令检查当前版本。

#### 开启蓝牙

不同操作系统的蓝牙开启方式不同，请确保蓝牙硬件已启用、未被软屏蔽，且蓝牙服务正常运行。

- Windows:
  - 通过系统设置 → 蓝牙和设备 → 确保蓝牙开关为"开"。

- macOS:
  - 通过系统设置 → 蓝牙 → 确保蓝牙为"打开"状态。

- Linux / 树莓派：

    ``` shell
    # 解除蓝牙软屏蔽（如适用）
    sudo rfkill unblock bluetooth

    # 启用并启动蓝牙服务
    sudo systemctl enable bluetooth
    sudo systemctl start bluetooth

    # 验证蓝牙状态
    bluetoothctl show
    ```

在 Linux 系统上运行 Python 程序时，当前用户需要加入 bluetooth 用户组，否则可能因权限不足导致连接失败：

```shell
sudo usermod -aG bluetooth $USER
#执行后需重新登录或重启生效
```

#### 开启手柄并进入待连接状态

- 将手柄开机，手柄开机后会自动处于蓝牙可被发现的**待连接状态**，此时手柄指示灯应呈现**慢闪状态（约每秒闪烁一次）**。

## 示例说明

> **⚠️ 运行环境提示**：
>
> 示例代码中的 `import codex_pad` 依赖于仓库根目录下的 `codex_pad.py` 库文件。**请不要单独将示例文件拷贝到其他目录运行**，否则会报 `ModuleNotFoundError`。
>
> 你有以下三种方式正确运行示例：
>
> 1. **在仓库根目录下直接运行**（推荐）：克隆或下载仓库后，在包含 `codex_pad.py` 的目录中直接执行 `python example_xxx.py`。
> 2. **将库文件一起拷贝**：如果你确实需要将示例文件放到其他位置，请务必同时将 `codex_pad.py` 文件复制到同一目录下。
> 3. **以可编辑模式安装本库**：如果你希望在任何位置都能 `import codex_pad`，可以在仓库根目录下执行：
>
>    ```shell
>    pip install -e .
>    ```
>
>    这样 `codex_pad` 会被安装到 Python 环境中，之后你可以在任意位置运行示例。

示例代码中包含详细的注释说明，建议直接查阅代码文件以获取最完整的信息。以下简要介绍各示例的核心功能与预期行为，助您快速入门。

### 地址直连示例（`example_connect_by_address.py`）

- **文件位置**：[example_connect_by_address.py](example_connect_by_address.py)
- **示例说明**：通过地址与手柄进行地址直连，检测到按钮状态与摇杆数值变化后打印。
- **操作步骤**：
    1. 打开 `example_connect_by_address.py`，找到 `_BLUETOOTH_DEVICE_ADDRESS = "16:00:00:00:02:72"`，将引号内的地址改为您自己手柄的地址（格式形如 `"E4:66:E5:A2:24:5D"`，字符为大写 A-F、半角冒号分隔）。
    2. 保存文件后运行：`python example_connect_by_address.py`。
    3. 程序会自动扫描并连接该地址对应的手柄。连接建立后，正常操作手柄即可在控制台查看实时的按键与摇杆日志输出。连接失败请多尝试几次。

### 按键掩码连接示例 (`example_connect_by_button_mask.py`)

- **文件位置**：[example_connect_by_button_mask.py](example_connect_by_button_mask.py)
- **示例说明**：通过匹配特定的自定义的**按键**或者**按键组合**来扫描并自动连接附近的手柄设备，检测摇杆和按键变化并打印。

> ⚠️ **树莓派已知问题（Bleak 协议栈）**：
> 目前在树莓派（以及其他可能的 Linux 发行版）上使用 `bleak` 协议栈时，“按键掩码连接”功能存在 bug，可能会出现连接不上的问题。该功能在 Windows 上测试正常。
> 后续可能会有解决方案。在此期间，用户可以自行研究更换蓝牙协议栈或探索其他解决方法。

- **默认按键掩码**：代码中预设的默认组合为 **Start + Cross(A)**，即 `_BUTTON_MASK = BUTTON_START | BUTTON_CROSS_A`。如需修改，可编辑代码中的 `_BUTTON_MASK` 变量，将其改为您需要的按键组合。
- **操作步骤**：
    1. 运行：`python example_connect_by_button_mask.py`, 代码启动后进入扫描连接状态。
    2. 手柄开机后蓝灯闪烁。
    3. **在手柄上按住代码中指定的按键掩码（默认为 Start + Cross(A) 同时按住），并保持不放**，直到主机成功连接手柄。连接建立后，正常操作手柄即可在控制台查看实时日志输出。

**⚠️ 调试注意事项**：

在开发调试过程中，经常需要使用 Ctrl+C 中断程序运行。需要注意的是：程序进程终止后，操作系统底层的蓝牙连接可能并不会立即中断。此时若重新运行程序，可能会遇到连接失败或无法搜索到设备的情况。  
解决方法：重启手柄，使其退出连接状态并重新进入可发现模式（蓝灯慢闪）。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。
