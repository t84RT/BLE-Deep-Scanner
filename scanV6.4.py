#!/usr/bin/env python3
"""
BLE 广播包深度扫描器 v6.4 (终极全格式适配版)
彻底适配截图中的 mac_vendors_database.json 键名格式。
"""

import asyncio
import json
import time
import threading
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from bleak import BleakScanner
import os

# ======================================================================
# 第一部分：蓝牙协议识别字典 (Apple, Microsoft, Google 等)
# ======================================================================
APPLE_COMPANY_ID = 76
FAST_PAIR_SERVICE_UUID = "0000fe2c-0000-1000-8000-00805f9b34fb"
MICROSOFT_COMPANY_ID = 6
SAMSUNG_COMPANY_ID = 117
GOOGLE_COMPANY_ID = 224

APPLE_NEARBY_ACTIONS = {
    "13": "AppleTV AutoFill", "27": "AppleTV Connecting...", "20": "Join This AppleTV?", 
    "19": "AppleTV Audio Sync", "1E": "AppleTV Color Balance", "09": "Setup New iPhone",
    "02": "Transfer Phone Number", "0B": "HomePod Setup", "01": "Setup New AppleTV", 
    "06": "Pair AppleTV", "0D": "HomeKit AppleTV Setup", "2B": "AppleID for AppleTV?",
    "05": "Apple Watch", "24": "Apple Vision Pro", "2F": "Connect to other Device", 
    "21": "Software Update"
}
APPLE_PROXIMITY_PAIR_DEVICES = {
    "0E20": "AirPods Pro", "0A20": "AirPods Max", "0220": "AirPods", "0F20": "AirPods 2nd Gen", 
    "1320": "AirPods 3rd Gen", "1420": "AirPods Pro 2nd Gen", "1020": "Beats Flex",
    "0620": "Beats Solo 3", "1120": "Beats Studio Buds", "1220": "Beats Fit Pro", 
    "1620": "Beats Studio Buds+"
}
APPLE_PROXIMITY_COLORS = {"0A20": {"00": "White", "02": "Red", "03": "Blue", "0F": "Black", "11": "Light Green"}}
SAMSUNG_EASY_SETUP_BUDS = {"EE7A0C": "Fallback Buds", "39EA48": "Light Purple Buds2", "850116": "Black Buds Live", "D30704": "Black Buds"}
SAMSUNG_EASY_SETUP_WATCH = {"1A": "Fallback Watch", "11": "Black Watch5 44mm", "12": "Sapphire Watch5 44mm"}

UUID_FRIENDLY_NAMES = {
    "00001800-0000-1000-8000-00805f9b34fb": "GAP (通用属性)", "0000180f-0000-1000-8000-00805f9b34fb": "Battery Service (电池)",
    "00001812-0000-1000-8000-00805f9b34fb": "HID (键鼠)", "0000180d-0000-1000-8000-00805f9b34fb": "Heart Rate (心率)",
    "000019fe-0000-1000-8000-00805f9b34fb": "Eddystone (信标)", "0000fe2c-0000-1000-8000-00805f9b34fb": "Google Fast Pair (快速配对)",
}

# ======================================================================
# 第二部分：本地海量 OUI 数据库解析核心类（V6.4 终极精准修正）
# ======================================================================
class OfflineOUIDatabase:
    def __init__(self):
        self.vendors = {}
        self.is_loaded = False
        self.load_count = 0

    def _normalize_prefix(self, prefix):
        """将各类前缀转换为标准的带冒号大写格式"""
        if not prefix:
            return ""
        # 消除所有分隔符和空格
        cleaned = prefix.strip().replace('-', '').replace(':', '').replace(' ', '').upper()
        if len(cleaned) == 6:   # 24位
            return f"{cleaned[0:2]}:{cleaned[2:4]}:{cleaned[4:6]}"
        elif len(cleaned) == 7: # 28位
            return f"{cleaned[0:2]}:{cleaned[2:4]}:{cleaned[4:6]}:{cleaned[6:8]}"
        elif len(cleaned) == 9: # 36位
            return f"{cleaned[0:2]}:{cleaned[2:4]}:{cleaned[4:6]}:{cleaned[6:8]}:{cleaned[8:10]}"
        return prefix.upper()

    def load_oui_txt(self, filepath):
        try:
            count = 0
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if "(hex)" in line:
                        p, v = line.split("(hex)")
                        self.vendors[self._normalize_prefix(p)] = v.strip()
                        count += 1
            print(f"✅ [成功] 已从 {os.path.basename(filepath)} 加载 {count} 条标准 24位 OUI 记录。")
        except Exception as e:
            print(f"⚠️ [警告] 加载 oui.txt 失败: {e}")

    def load_oui_csv(self, filepath):
        try:
            count = 0
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.lstrip('\ufeff').strip() # 修复 Windows CSV BOM 头问题
                    if not line or line.startswith("Registry"):
                        continue
                    parts = line.split(',')
                    if len(parts) >= 2:
                        p = parts[1].strip()     # Assignment 字段
                        v = parts[2].strip().strip('"') # Organization Name 字段
                        prefix = self._normalize_prefix(p)
                        if prefix:
                            self.vendors[prefix] = v
                            count += 1
            print(f"✅ [成功] 已从 {os.path.basename(filepath)} 加载 {count} 条 28/36 位 CSV 前缀记录。")
        except Exception as e:
            print(f"⚠️ [警告] 加载 {os.path.basename(filepath)} 失败: {e}")

    def load_json(self, filepath):
        """【核心修复】适配您截图中的 mac_vendors_database.json 格式"""
        try:
            count = 0
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
                
                # 处理数组格式 (如您截图所示)
                if isinstance(data, list):
                    for item in data:
                        # 注意这里修正了键名，截图中是 "mac_prefix" 和 "vendor_name"
                        if "mac_prefix" in item and "vendor_name" in item:
                            self.vendors[self._normalize_prefix(item["mac_prefix"])] = item["vendor_name"]
                            count += 1
                # 兼容某些字典格式
                elif isinstance(data, dict):
                    for prefix, vendor in data.items():
                        self.vendors[self._normalize_prefix(prefix)] = vendor
                        count += 1
                        
            print(f"✅ [成功] 已从 {os.path.basename(filepath)} 加载 {count} 条 JSON 记录。")
        except Exception as e:
            print(f"⚠️ [警告] 加载 JSON 数据库时发生错误: {e}")

    def load_directory(self, directory_path):
        """强制使用 oui.txt 覆盖优先级加载"""
        self.vendors.clear()
        self.load_count = 0
        files = os.listdir(directory_path)
        
        # 1. 优先加载 CSV 和 JSON 作为基础库
        for f in files:
            path = os.path.join(directory_path, f)
            f_lower = f.lower()
            if f_lower in ["mam.csv", "oui36.csv", "cid.csv"]:
                self.load_oui_csv(path)
            elif f_lower == "mac_vendors_database.json":
                self.load_json(path)
        
        # 2. 最后加载官方 oui.txt 进行强制补全 (覆盖前面可能缺失的 Apple/Microsoft)
        for f in files:
            path = os.path.join(directory_path, f)
            f_lower = f.lower()
            if f_lower == "oui.txt":
                self.load_oui_txt(path)
        
        self.load_count = len(self.vendors)
        print(f"📊 [最终统计] 数据库合并完成，内存中共有 {self.load_count} 条有效 OUI 前缀记录。\n")
        
        if self.load_count > 100:
            self.is_loaded = True
            return True
        return False

    def lookup(self, mac_address):
        if not mac_address or len(mac_address) < 8 or not self.is_loaded:
            return "未加载数据库"
        mac = mac_address.upper()
        # 优先匹配最长前缀
        if len(mac) >= 14 and mac[:14] in self.vendors:
            return self.vendors[mac[:14]]
        if len(mac) >= 11 and mac[:11] in self.vendors:
            return self.vendors[mac[:11]]
        if len(mac) >= 8 and mac[:8] in self.vendors:
            return self.vendors[mac[:8]]
        return "未知厂商"

# 初始化全局 OUI 数据库对象
OUI_DB = OfflineOUIDatabase()

# ======================================================================
# 第三部分：BLE 协议解析与物理层分析函数
# ======================================================================
def parse_apple_data(data_hex):
    if len(data_hex) < 2: return "Apple", "数据过短"
    subtype = data_hex[:2]
    if subtype == "0f":
        if len(data_hex) >= 8:
            action_hex = data_hex[6:8]
            action_name = APPLE_NEARBY_ACTIONS.get(action_hex.upper(), f"未知动作 0x{action_hex}")
            return "Apple Continuity (Action)", action_name
    elif subtype == "07":
        if len(data_hex) >= 12:
            prefix = data_hex[4:6]
            device_id = data_hex[6:10]
            color_code = data_hex[18:20] if len(data_hex) >= 20 else "??"
            desc = "ProximityPair"
            if prefix == "01": desc = "Not Your Device"
            elif prefix == "05": desc = "New Airtag"
            elif prefix == "07": desc = "New Device"
            dev_name = APPLE_PROXIMITY_PAIR_DEVICES.get(device_id.upper(), f"设备 0x{device_id}")
            color_name = APPLE_PROXIMITY_COLORS.get(device_id.upper(), {}).get(color_code.upper(), color_code)
            return "Apple Proximity", f"{desc} - {dev_name} (颜色:{color_name})"
    elif subtype == "12":
        if len(data_hex) >= 4:
            flags = data_hex[2:4]
            if flags == "02": return "Apple Handoff", "Wi-Fi 密码共享 (正在播报)"
            if flags in ["01", "03"]: return "Apple Handoff", f"跨设备接力 (Hex尾段: {data_hex[4:]})"
        return "Apple Handoff", f"子类型 0x12"
    elif subtype == "15":
        return "Apple HomeKit", "HomeKit 配件/设置广播"
    elif subtype == "1C":
        return "Apple Siri", "Siri/账号 联动广播"
    elif subtype in ("01", "10"):
        return "Apple FindMy", "FindMy 防丢网络广播"
    return "Apple Other", f"子类型 0x{subtype}"

def parse_microsoft_data(data_hex):
    if data_hex.startswith("030080"):
        try:
            name = bytes.fromhex(data_hex[6:]).decode('ascii').strip('\x00')
            return "Microsoft Swift Pair", f"设备名: {name}"
        except: pass
    return "Microsoft Other", f"数据: {data_hex}"

def parse_ibeacon(hex_data):
    if hex_data.startswith("0215") and len(hex_data) >= 24:
        uuid = hex_data[4:36]
        major = hex_data[36:40]
        minor = hex_data[40:44]
        tx_power_hex = hex_data[44:46]
        try:
            tx_power = int(tx_power_hex, 16) - 256 if int(tx_power_hex, 16) > 127 else int(tx_power_hex, 16)
        except:
            tx_power = "N/A"
        return "Apple iBeacon", f"UUID: {uuid}, Major: {major}, Minor: {minor}, Tx: {tx_power}"
    return None

def parse_eddystone(hex_data):
    if hex_data.startswith("00"):
        namespace = hex_data[2:22]
        instance = hex_data[22:34]
        return "Eddystone (UID)", f"Namespace: {namespace}, Instance: {instance}"
    elif hex_data.startswith("10"):
        return "Eddystone (URL)", f"URL(Hex): {hex_data[2:]}"
    return None

def parse_samsung_data(data_hex):
    if "420981" in data_hex:
        for dev_id, dev_name in SAMSUNG_EASY_SETUP_BUDS.items():
            if dev_id.lower() in data_hex: return "Samsung Buds", dev_name
        return "Samsung Buds", "未知型号"
    elif data_hex.startswith("010002000101FF000043"):
        if len(data_hex) >= 22:
            watch_id = data_hex[-2:].upper()
            return "Samsung Watch", SAMSUNG_EASY_SETUP_WATCH.get(watch_id, "未知Watch")
    return "Samsung Other", f"数据: {data_hex}"

def identify_protocol(adv_info):
    mfg_data = adv_info.get("manufacturer_data", {})
    if str(APPLE_COMPANY_ID) in mfg_data:
        data = mfg_data[str(APPLE_COMPANY_ID)]
        ib = parse_ibeacon(data)
        if ib: return ib
        return parse_apple_data(data)
    if str(MICROSOFT_COMPANY_ID) in mfg_data:
        return parse_microsoft_data(mfg_data[str(MICROSOFT_COMPANY_ID)])
    if str(SAMSUNG_COMPANY_ID) in mfg_data:
        return parse_samsung_data(mfg_data[str(SAMSUNG_COMPANY_ID)])
    if str(GOOGLE_COMPANY_ID) in mfg_data:
        return "Google Nearby", f"数据: {mfg_data[str(GOOGLE_COMPANY_ID)]}"
    
    service_data = adv_info.get("service_data", {})
    if FAST_PAIR_SERVICE_UUID in service_data:
        return "Google Fast Pair", f"Model ID: {service_data[FAST_PAIR_SERVICE_UUID]}"
    if "000019fe" in service_data:
        return parse_eddystone(service_data["000019fe"])
    if "0000feaa" in service_data:
        return "Google Nearby (Eddystone)", f"数据: {service_data['0000feaa']}"
    return "Unknown", ""

def calc_distance(rssi, tx_power=-50):
    if tx_power is None: return "N/A"
    try:
        distance = 10 ** ((rssi - tx_power) / 20.0)
        return f"{distance:.1f}m"
    except:
        return "N/A"

def get_mac_type(mac):
    if not mac or len(mac) < 2: return "无效地址"
    try:
        first_byte = int(mac[:2], 16)
        if first_byte & 0xC0 == 0xC0: return "随机静态地址"
        elif first_byte & 0xC0 == 0x80: return "可解析私有地址"
        else: return "公共地址"
    except:
        return "无效地址"

def get_mac_vendor_info(mac):
    if not mac or len(mac) < 8: return "无效地址"
    try:
        first_byte = int(mac[:2], 16)
        if first_byte & 0xC0 == 0xC0:
            type_str = "随机静态"
        elif first_byte & 0xC0 == 0x80:
            type_str = "私有解析"
        else:
            type_str = "公共地址"
        
        vendor = OUI_DB.lookup(mac)
        return f"{type_str} - {vendor}"
    except:
        return "无效地址"

# ======================================================================
# 第四部分：GUI 主类
# ======================================================================
class BLEScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BLE 深度扫描仪 v6.4 (完美兼容全部 5 种数据库格式)")
        self.root.geometry("1400x900")

        self.rssi_min = tk.IntVar(value=-120)
        self.rssi_max = tk.IntVar(value=0)
        self.scan_mode = tk.StringVar(value="active")
        self.output_file = tk.StringVar(value="ble_all_packets.json")

        self.running = False
        self.stop_event = None
        self.thread = None
        self.raw_queue = queue.Queue(maxsize=10000)
        self.file_queue = queue.Queue(maxsize=10000)
        self.writer_thread = None

        self.packet_count = 0
        self.dropped_packets = 0
        self.last_stats_time = time.time()
        self._last_count = 0
        self.row_data_map = {}

        self.create_widgets()
        self.update_gui()

    def create_widgets(self):
        control_frame = ttk.LabelFrame(self.root, text="控制面板 (完美支持 oui.txt, mam.csv, oui36.csv, cid.csv, mac_vendors_database.json)", padding=5)
        control_frame.pack(fill="x", padx=5, pady=5)

        row1 = ttk.Frame(control_frame); row1.pack(fill="x", pady=2)
        ttk.Label(row1, text="RSSI:").pack(side="left")
        ttk.Entry(row1, textvariable=self.rssi_min, width=4).pack(side="left")
        ttk.Label(row1, text="~").pack(side="left")
        ttk.Entry(row1, textvariable=self.rssi_max, width=4).pack(side="left")
        ttk.Label(row1, text="模式:").pack(side="left", padx=(10,2))
        ttk.Combobox(row1, textvariable=self.scan_mode, values=["active", "passive"], width=8, state="readonly").pack(side="left")
        ttk.Label(row1, text="保存:").pack(side="left", padx=(10,2))
        ttk.Entry(row1, textvariable=self.output_file, width=12).pack(side="left")
        ttk.Button(row1, text="浏览", command=self.browse_output).pack(side="left", padx=2)

        row2 = ttk.Frame(control_frame); row2.pack(fill="x", pady=5)
        self.start_btn = ttk.Button(row2, text="▶ 启动扫描", command=self.start_scan, width=12)
        self.start_btn.pack(side="left", padx=5)
        self.stop_btn = ttk.Button(row2, text="■ 停止", command=self.stop_scan, state="disabled", width=10)
        self.stop_btn.pack(side="left", padx=5)
        ttk.Separator(row2, orient="vertical").pack(side="left", fill="y", padx=10)
        
        self.load_oui_btn = ttk.Button(row2, text="📂 选择OUI文件夹", command=self.select_oui_folder)
        self.load_oui_btn.pack(side="left", padx=5)
        self.parse_mac_btn = ttk.Button(row2, text="🔄 重解析MAC厂商", command=self.reparse_mac_vendors, state="disabled")
        self.parse_mac_btn.pack(side="left", padx=5)
        
        self.status_label = ttk.Label(row2, text="就绪 (请留意命令行黑框的加载日志，验证数据读取条数)")
        self.status_label.pack(side="right", padx=10)

        # --- 数据表 ---
        table_frame = ttk.LabelFrame(self.root, text="捕获列表", padding=5)
        table_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        columns = ("时间", "MAC", "MAC类型/厂商", "包连接性", "Tx功率", "距离(m)", "RSSI", "设备名称", "协议", "详情")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        col_widths = [140, 120, 200, 80, 60, 70, 50, 150, 150, 250]
        for col, w in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="w")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # --- 底部详情面板 ---
        detail_frame = ttk.LabelFrame(self.root, text="数据包详情", padding=5)
        detail_frame.pack(fill="both", padx=5, pady=5)
        self.detail_text = scrolledtext.ScrolledText(detail_frame, wrap=tk.WORD, font=("Consolas", 9))
        self.detail_text.pack(fill="both", expand=True)
        self.detail_text.insert(tk.END, "点击上方表格行查看完整 JSON 数据。")
        self.detail_text.tag_config("bold", font=("Consolas", 10, "bold"))

        # --- 状态 ---
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", padx=5, pady=2)
        self.stats_label = ttk.Label(status_frame, text="总包: 0 | 速率: 0.0 pps | 队列: 0 | 丢弃: 0")
        self.stats_label.pack(side="left")

    def browse_output(self):
        fn = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if fn: self.output_file.set(fn)

    def select_oui_folder(self):
        folder = filedialog.askdirectory(title="请选择包含 OUI/CSV/JSON 数据库的文件夹")
        if not folder: return
        
        self.status_label.config(text="正在加载本地 OUI 数据库，请留意下方 Python 命令行窗口的加载日志...")
        self.root.update()
        
        print(f"\n🚀 正在扫描并加载文件夹: {folder}")
        success = OUI_DB.load_directory(folder)
        
        if success:
            self.status_label.config(text=f"✅ 数据库加载成功！共整合 {OUI_DB.load_count} 条前缀数据。请点击「重解析MAC厂商」!")
            self.parse_mac_btn.config(state="normal")
        else:
            self.status_label.config(text="❌ 加载失败：文件夹中未找到任何有效的 OUI/JSON 数据库文件。")
            self.parse_mac_btn.config(state="disabled")

    def reparse_mac_vendors(self):
        if not OUI_DB.is_loaded:
            messagebox.showwarning("提示", "请先选择加载本地的 OUI 数据库文件夹！")
            return
        
        self.status_label.config(text="正在使用 OUI 库重解析所有 MAC 地址...")
        self.root.update()
        count = 0
        
        for item_id in self.tree.get_children():
            adv_info = self.row_data_map.get(item_id)
            if not adv_info: continue
            
            mac = adv_info.get("mac", "")
            new_vendor_info = get_mac_vendor_info(mac)
            self.tree.set(item_id, column="MAC类型/厂商", value=new_vendor_info)
            count += 1
        
        self.status_label.config(text=f"✅ 重解析完成，已更新 {count} 条 MAC 地址厂商信息！")

    def add_table_row(self, adv_info):
        mac = adv_info.get("mac", "")
        vendor_info = get_mac_vendor_info(mac)
        
        rssi = adv_info.get("rssi", -100)
        tx_power = adv_info.get("tx_power")
        distance = calc_distance(rssi, tx_power if tx_power is not None else -50)
        connectable = adv_info.get("is_connectable", "N/A")
        if connectable is True: connectable = "可连接"
        elif connectable is False: connectable = "不可连接"
        
        ts = adv_info.get("timestamp", "")
        name = adv_info.get("name", "N/A")[:20]
        protocol = adv_info.get("protocol", "Unknown")
        details = adv_info.get("protocol_details", "")
        tx_power_str = str(tx_power) if tx_power is not None else "N/A"

        item_id = self.tree.insert("", 0, values=(
            ts, mac, vendor_info, connectable, tx_power_str, distance, rssi, name, protocol, details
        ))
        self.row_data_map[item_id] = adv_info

        if len(self.tree.get_children()) > 3000:
            for child in self.tree.get_children()[:len(self.tree.get_children())//2]:
                self.row_data_map.pop(child, None)
                self.tree.delete(child)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected: return
        item_id = selected[0]
        adv_info = self.row_data_map.get(item_id, {})
        
        if adv_info:
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(tk.END, "【一、完整原始数据 (Raw JSON)】\n", "bold")
            self.detail_text.insert(tk.END, json.dumps(adv_info, indent=4, ensure_ascii=False) + "\n\n")
            
            self.detail_text.insert(tk.END, "【二、MAC与物理层分析】\n", "bold")
            mac = adv_info.get("mac", "")
            self.detail_text.insert(tk.END, f"• MAC 地址类型: {get_mac_type(mac)}\n")
            self.detail_text.insert(tk.END, f"• MAC 归属厂商: {OUI_DB.lookup(mac)}\n")
            
            rssi = adv_info.get("rssi", "")
            tx_power = adv_info.get("tx_power")
            distance = calc_distance(rssi, tx_power if tx_power is not None else -50)
            self.detail_text.insert(tk.END, f"• 信号强度 (RSSI): {rssi} dBm\n")
            self.detail_text.insert(tk.END, f"• 物理距离估算 (约): {distance}\n")
            
            connectable = adv_info.get("is_connectable", "未知")
            self.detail_text.insert(tk.END, f"• 包类型与连接性: {'✅ 可连接' if connectable is True else '❌ 不可连接' if connectable is False else '未知'}\n")
            
            uuids = adv_info.get("service_uuids", [])
            if uuids:
                self.detail_text.insert(tk.END, f"\n【三、服务特征翻译】\n")
                for uuid in uuids:
                    friendly = UUID_FRIENDLY_NAMES.get(uuid, uuid)
                    self.detail_text.insert(tk.END, f"  • {uuid} -> {friendly if friendly != uuid else '未知特征'}\n")

    def update_gui(self):
        count = 0
        while count < 300 and not self.raw_queue.empty():
            try:
                adv_info = self.raw_queue.get_nowait()
                protocol, details = identify_protocol(adv_info)
                adv_info["protocol"] = protocol
                adv_info["protocol_details"] = details
                self.add_table_row(adv_info)
                
                if self.running:
                    try:
                        self.file_queue.put_nowait(adv_info)
                    except queue.Full:
                        self.dropped_packets += 1
                count += 1
            except queue.Empty:
                break

        if self.running:
            now = time.time()
            if now - self.last_stats_time >= 1.0:
                qsize = self.raw_queue.qsize()
                rate = (self.packet_count - self._last_count) / (now - self.last_stats_time)
                self.stats_label.config(text=f"总包: {self.packet_count} | 速率: {rate:.1f} pps | 队列: {qsize} | 丢弃: {self.dropped_packets}")
                self._last_count = self.packet_count
                self.last_stats_time = now
        else:
            self.stats_label.config(text=f"总包: {self.packet_count} | 已停止")
        self.root.after(100, self.update_gui)

    def start_scan(self):
        if self.running: return
        try:
            rssi_min = self.rssi_min.get()
            rssi_max = self.rssi_max.get()
        except:
            messagebox.showerror("错误", "RSSI 值须为整数")
            return

        self.packet_count = 0
        self.dropped_packets = 0
        self.row_data_map.clear()
        self.tree.delete(*self.tree.get_children())
        self.detail_text.delete(1.0, tk.END)
        while not self.raw_queue.empty(): self.raw_queue.get_nowait()
        while not self.file_queue.empty(): self.file_queue.get_nowait()

        self.stop_event = threading.Event()
        self.writer_thread = threading.Thread(target=self._file_writer, args=(self.output_file.get(),), daemon=False)
        self.writer_thread.start()

        self.thread = threading.Thread(target=self._run_scan, args=(rssi_min, rssi_max, self.scan_mode.get()), daemon=True)
        self.thread.start()

        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="扫描中...")

    async def _async_scan(self, loop, rssi_min, rssi_max, scan_mode):
        def callback(device, advertisement_data):
            try:
                rssi = advertisement_data.rssi
                if rssi < rssi_min or rssi > rssi_max: return
                
                mfg_data = {str(cid): data.hex() for cid, data in advertisement_data.manufacturer_data.items()}
                service_data = {str(uuid): data.hex() for uuid, data in advertisement_data.service_data.items()}
                raw = getattr(advertisement_data, "raw_data", None)
                raw_hex = raw.hex() if raw is not None else None

                adv_info = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    "timestamp_unix": time.time(),
                    "mac": device.address,
                    "address_type": getattr(device, "address_type", None),
                    "name": advertisement_data.local_name or device.name or "N/A",
                    "rssi": rssi,
                    "tx_power": advertisement_data.tx_power,
                    "is_connectable": getattr(advertisement_data, "connectable", None),
                    "manufacturer_data": mfg_data,
                    "service_uuids": [str(uuid) for uuid in advertisement_data.service_uuids],
                    "service_data": service_data,
                    "raw_hex": raw_hex,
                }
                try:
                    self.raw_queue.put_nowait(adv_info)
                    self.packet_count += 1
                except queue.Full:
                    self.dropped_packets += 1
            except:
                pass

        scanner = BleakScanner(callback, scanning_mode=scan_mode)
        while not self.stop_event.is_set():
            try:
                await scanner.start()
                while not self.stop_event.is_set():
                    await asyncio.sleep(0.5)
                await scanner.stop()
                break
            except Exception as e:
                print(f"扫描中断: {e}，重试中...")
                await asyncio.sleep(5)

    def _run_scan(self, rssi_min, rssi_max, scan_mode):
        try:
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._async_scan(loop, rssi_min, rssi_max, scan_mode))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("扫描错误", str(e)))
        finally:
            self.root.after(0, self._scan_finished)

    def _scan_finished(self):
        self.running = False
        try: self.file_queue.join()
        except: pass
        if self.writer_thread and self.writer_thread.is_alive():
            self.writer_thread.join(timeout=5)
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text=f"✅ 扫描完成，数据已保存至 {os.path.abspath(self.output_file.get())}")

    def stop_scan(self):
        if self.running:
            self.stop_event.set()
            self.status_label.config(text="正在停止扫描...")
            self.stop_btn.config(state="disabled")

    def _file_writer(self, output_file):
        abs_path = os.path.abspath(output_file)
        try:
            with open(abs_path, "a", encoding="utf-8") as f:
                while self.running or not self.file_queue.empty():
                    try:
                        item = self.file_queue.get(timeout=0.5)
                        f.write(json.dumps(item) + "\n")
                        f.flush()
                        self.file_queue.task_done()
                    except queue.Empty:
                        continue
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text=f"文件错误: {e}"))

    def on_closing(self):
        self.stop_scan()
        if self.thread and self.thread.is_alive(): self.thread.join(timeout=2)
        if self.writer_thread and self.writer_thread.is_alive(): self.writer_thread.join(timeout=2)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.option_add("*Font", "TkDefaultFont 9")
    app = BLEScannerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()