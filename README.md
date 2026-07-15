# BLE 深度扫描器 (BLE Deep Scanner)

**一站式蓝牙低功耗（BLE）广播包分析与设备识别工具**  
支持海量 OUI 厂商数据库、Manufacturer ID 映射、协议深度解析、实时信号监控与多格式数据导出。适用于物联网安全研究、智能设备调试、信号覆盖测试等场景。

---

## 📖 项目简介

BLE 深度扫描器是一款基于 Python + `bleak` 的跨平台 GUI 工具，能够实时捕获周围 BLE 设备的广播包，并对其进行**多维度解析**：

- **MAC 地址类型识别**（公共/随机静态/可解析私有）
- **本地 OUI 数据库匹配**（支持 `oui.txt`、`mam.csv`、`oui36.csv`、`cid.csv`、`mac_vendors_database.json` 等 5 种格式）
- **厂商 ID 双重保险**（当 OUI 匹配失败时，自动回退至 Manufacturer ID 映射表）
- **协议深度识别**（Apple Continuity/Handoff/Proximity、Microsoft Swift Pair、Samsung Buds/Watch、Google Fast Pair、Eddystone、iBeacon、华为/小米/ Tile / Ruuvi / Garmin 等）
- **信号质量分析**（RSSI 实时值、平均值、最小值、最大值、物理距离估算）
- **AD 结构完整解析**（Flags、Tx Power、Appearance、设备类别、LE 角色、URI、室内定位等）
- **系统资源监控**（CPU、内存、磁盘、网络、进程）
- **数据导出**（JSON / C 数组 / 混合文本格式），可直接用于 ESP32 等嵌入式开发。

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 📡 实时扫描 | 可设置 RSSI 过滤范围，支持 active / passive 两种扫描模式 |
| 🎯 目标设备过滤 | 输入 MAC 地址或设备名称关键词（逗号分隔），仅捕获指定设备 |
| 🏷 厂商识别 | 基于本地 OUI 数据库（5 种格式）+ Manufacturer ID 映射，双重保障 |
| 📊 丰富解析 | 解析 Apple、Microsoft、Samsung、Google、华为、小米、Tile、Ruuvi、Garmin 等厂商的私有数据 |
| 📈 信号统计 | 实时显示当前 RSSI、平均值、最小值、最大值、样本数、估算距离 |
| 📋 详细面板 | 点击列表行即可查看完整 JSON 原始数据、物理层分析、服务 UUID 翻译 |
| 💾 数据持久化 | 自动将所有捕获的包写入 JSON 文件（每行一条），支持后续离线分析 |
| 🖥 系统监控 | 内置 CPU、内存、磁盘、网络、进程占用监控面板，便于性能评估 |
| 📤 数据导出 | 可将设备广播帧导出为 JSON、C 数组（.h）、或人类可读的混合文本格式 |
| 🔄 重解析 MAC | 加载 OUI 数据库后，可一键更新表格中所有 MAC 的厂商信息 |

---

## 🗂 支持的数据库格式

| 文件名 | 类型 | 说明 |
|--------|------|------|
| `oui.txt` | IEEE 官方 OUI 文件 | 标准 24 位 OUI 列表 |
| `mam.csv` | MA‑M 分配文件 | 28 位前缀 |
| `oui36.csv` | MA‑S 分配文件 | 36 位前缀 |
| `cid.csv` | CID 分配文件 | 公司 ID |
| `mac_vendors_database.json` | JSON 数组 | 键名为 `mac_prefix` 和 `vendor_name`（如您截图所示） |

> 将以上任意文件放入同一文件夹，通过 GUI 的「选择 OUI 文件夹」按钮即可一次性加载并合并。

---

## 🖥 系统要求

- **操作系统**：Windows / Linux / macOS（需支持 BLE 蓝牙）
- **Python 版本**：≥ 3.8
- **蓝牙适配器**：内置或外接 BLE 4.0+ 适配器

---

## 📦 安装与运行

### 1. 克隆仓库
```bash
git clone https://github.com/your-username/ble-deep-scanner.git
cd ble-deep-scanner
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```
`requirements.txt` 内容如下：
```
bleak>=0.21.0
psutil>=5.9.0
```

### 3. 运行程序
```bash
python scanV7.0.py
```
> 最新稳定版为 `scanV7.0.py`，推荐使用。旧版本（v6.4～v6.6）保留作历史参考。

---

## 🖱 使用方法

1. **启动扫描**：设置 RSSI 过滤范围（默认 -100 ~ 0 dBm），选择扫描模式（passive 或 active），可选输入目标设备（MAC 或名称关键词，逗号分隔），然后点击「启动扫描」。
2. **查看列表**：实时捕获的广播包会以表格形式呈现，包含时间、MAC、MAC类型/厂商、协议、RSSI、距离等列。
3. **查看详情**：点击任意行，底部详情面板会显示该包的完整 JSON 数据、MAC 物理层分析、服务 UUID 翻译等。
4. **加载厂商数据库**：点击「加载厂商数据库」，选择包含 OUI 文件的文件夹，程序会自动合并所有文件，并可在之后点击「重解析MAC厂商」更新表格中的厂商信息。
5. **保存数据**：扫描过程中所有数据自动保存在指定的 JSON 文件中（默认为 `ble_all_packets.json`）。
6. **导出广播帧**：点击「导出广播帧」可将捕获的设备原始广播数据导出为 JSON、C 数组（.h）或混合文本格式，方便嵌入式开发。

---

## 📚 版本历史

### v7.0 (最新)
- **重大更新**：完全重构解析引擎，新增 AD 结构完整解析（Flags、Tx Power、Appearance、设备类别、LE 角色、URI 等）
- 新增系统资源监控面板（CPU、内存、磁盘、网络、进程）
- 新增设备详情面板，展示更丰富的信号统计（RSSI 均值/最值/样本数）
- 新增服务数据深度解析（电池服务、环境传感、暴露通知、Google Nearby、Eddystone TLM 等）
- 支持导出 C 数组格式，可直接用于 ESP32 等嵌入式项目
- 优化界面布局和响应速度

### v6.6
- 新增目标设备过滤功能（按 MAC 或名称关键词）

### v6.5
- 新增 Manufacturer ID 映射表，提供双保险厂商识别（OUI + 厂商 ID）

### v6.4
- 适配 `mac_vendors_database.json` 的 `mac_prefix` / `vendor_name` 键名格式
- 支持 24/28/36 位前缀规范化

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request。如果您希望增加对新厂商协议的支持，请提供相应的广播包样例（十六进制数据）。建议在提交前先运行 `scanV7.0.py` 并截图，以便我们复现问题。

---

## 📄 许可证

本项目采用 **MIT 许可证**。您可以自由使用、修改、分发，但需保留原作者的版权声明。

---

## 🙏 致谢

- [bleak](https://github.com/hbldh/bleak) – 强大的跨平台 BLE 库
- [psutil](https://github.com/giampaolo/psutil) – 系统监控利器
- IEEE 及各大厂商提供的 OUI 数据库

---

> **注意**：本工具仅供学习与研究用途，请勿用于非法跟踪或干扰他人设备。使用前请确保您拥有相关设备的扫描授权。
