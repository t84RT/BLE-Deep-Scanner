#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import asyncio
import bleak
from bleak import BleakScanner
import threading
import queue
import json
import time
import csv
import os
import sys
import traceback
import psutil

APPLE_COMPANY_ID = 76
MICROSOFT_COMPANY_ID = 6
SAMSUNG_COMPANY_ID = 117
GOOGLE_COMPANY_ID = 224
FAST_PAIR_SERVICE_UUID = "0000fe2c-0000-1000-8000-00805f9b34fb"

APPLE_NEARBY_ACTIONS = {
    "0D": "Apple TV 动作码 13",
    "1B": "Apple TV 动作码 27",
    "14": "Apple TV 动作码 20",
    "0C": "Apple TV 动作码 12",
    "08": "Apple TV 动作码 08",
    "0F": "Apple TV 动作码 15",
    "02": "Apple TV 动作码 02",
    "13": "Apple TV 动作码 19",
    "12": "Apple TV 动作码 18",
    "1A": "Apple TV 动作码 26",
    "11": "Apple TV 动作码 17",
    "10": "Apple TV 动作码 16",
    "0E": "Apple TV 动作码 14",
}

APPLE_PROXIMITY_PAIR_DEVICES = {
    "0041": "AirPods Pro 2",
    "0043": "AirPods Pro 2 (USB-C)",
    "0045": "AirPods Pro 2 (MagSafe)",
    "0020": "AirPods 3",
    "0022": "AirPods 3 (MagSafe)",
    "0012": "AirPods Pro",
    "0015": "AirPods Pro (MagSafe)",
    "000C": "AirPods 2",
    "000E": "AirPods 2 (MagSafe)",
    "0003": "AirPods",
    "0004": "PowerBeats Pro",
    "0006": "Beats Studio Buds",
    "0007": "Beats Studio Buds+",
    "0008": "Beats Fit Pro",
    "0009": "Beats Flex",
    "000B": "Beats Solo Pro",
}

APPLE_PROXIMITY_COLORS = {
    "000C": {"04": "白色", "05": "黑色"},
    "0012": {"04": "白色"},
    "0020": {"04": "白色", "05": "星空蓝", "06": "橙色", "07": "星光色", "08": "深空灰"},
    "0041": {"04": "白色", "05": "深空黑"},
    "0006": {"01": "黑色", "02": "白色", "03": "透明"},
    "0008": {"01": "黑色", "02": "白色", "03": "透明"},
}

SAMSUNG_EASY_SETUP_BUDS = {
    "22001": "Galaxy Buds",
    "22002": "Galaxy Buds+",
    "22003": "Galaxy Buds Live",
    "22004": "Galaxy Buds Pro",
    "22005": "Galaxy Buds 2",
    "22006": "Galaxy Buds 2 Pro",
    "22007": "Galaxy Buds FE",
    "22008": "Galaxy Buds 3",
    "22009": "Galaxy Buds 3 Pro",
}

SAMSUNG_EASY_SETUP_WATCH = {
    "01": "Galaxy Watch",
    "02": "Galaxy Watch Active",
    "03": "Galaxy Watch Active2",
    "04": "Galaxy Watch3",
    "05": "Galaxy Watch4",
    "06": "Galaxy Watch4 Classic",
    "07": "Galaxy Watch5",
    "08": "Galaxy Watch5 Pro",
    "09": "Galaxy Watch6",
    "0A": "Galaxy Watch6 Classic",
    "0B": "Galaxy Watch7",
}

MANUFACTURER_ID_MAP = {
    76: "Apple Inc.",
    6: "Microsoft Corporation",
    117: "Samsung Electronics Co., Ltd.",
    224: "Google LLC",
    156: "Huawei Technologies Co., Ltd.",
    25: "Sony Corporation",
    13: "LG Electronics Inc.",
    3: "Intel Corporation",
    24: "Qualcomm Incorporated",
    30: "Motorola Mobility LLC",
    10: "Dell Inc.",
    34: "Lenovo Group Limited",
    48: "Xiaomi Corporation",
    167: "Oppo Guangdong Mobile Telecommunications Corp., Ltd.",
    196: "Vivo Mobile Communications Co., Ltd.",
    142: "Realme Chongqing Mobile Telecommunications Corp., Ltd.",
    12: "Hewlett-Packard Company",
    180: "Amazon.com Services LLC",
    229: "Facebook Inc.",
    176: "Nintendo Co., Ltd.",
    18: "Canon Inc.",
    29: "Panasonic Corporation",
    23: "Nokia Corporation",
    14: "Texas Instruments Incorporated",
    8: "Broadcom Corporation",
    11: "Marvell Technology Group Ltd.",
    2: "AMD, Inc.",
    5: "Atmel Corporation",
    7: "National Semiconductor Corporation",
    61: "Ruuvi Innovations Ltd.",
    318: "Tile Inc.",
    11: "Fitbit Inc.",
    99: "Garmin Ltd.",
    16: "Logitech S.A.",
    183: "GoPro Inc.",
    225: "Amazon Lab126 Inc.",
    231: "Netatmo",
    254: "Philips Lighting",
    191: "TP-Link Technologies Co., Ltd.",
    200: "TP-Link Technologies Co., Ltd.",
}

HUAWEI_COMPANY_ID = 156
XIAOMI_COMPANY_ID = 48
TILE_COMPANY_ID = 318
RUUVI_COMPANY_ID = 61
GARMIN_COMPANY_ID = 99

BLE_STANDARD_SERVICES = {
    "00001800-0000-1000-8000-00805f9b34fb": "Generic Access",
    "00001801-0000-1000-8000-00805f9b34fb": "Generic Attribute",
    "00001802-0000-1000-8000-00805f9b34fb": "Immediate Alert",
    "00001803-0000-1000-8000-00805f9b34fb": "Link Loss",
    "00001804-0000-1000-8000-00805f9b34fb": "Tx Power",
    "00001805-0000-1000-8000-00805f9b34fb": "Current Time Service",
    "00001806-0000-1000-8000-00805f9b34fb": "Reference Time Update Service",
    "00001807-0000-1000-8000-00805f9b34fb": "Next DST Change Service",
    "00001808-0000-1000-8000-00805f9b34fb": "Glucose",
    "00001809-0000-1000-8000-00805f9b34fb": "Health Thermometer",
    "0000180a-0000-1000-8000-00805f9b34fb": "Device Information",
    "0000180d-0000-1000-8000-00805f9b34fb": "Heart Rate",
    "0000180e-0000-1000-8000-00805f9b34fb": "Phone Alert Status Service",
    "0000180f-0000-1000-8000-00805f9b34fb": "Battery Service",
    "00001810-0000-1000-8000-00805f9b34fb": "Blood Pressure",
    "00001811-0000-1000-8000-00805f9b34fb": "Alert Notification Service",
    "00001812-0000-1000-8000-00805f9b34fb": "Human Interface Device",
    "00001813-0000-1000-8000-00805f9b34fb": "Scan Parameters",
    "00001814-0000-1000-8000-00805f9b34fb": "Running Speed and Cadence",
    "00001815-0000-1000-8000-00805f9b34fb": "Automation IO",
    "00001816-0000-1000-8000-00805f9b34fb": "Cycling Speed and Cadence",
    "00001817-0000-1000-8000-00805f9b34fb": "Cycling Power",
    "00001818-0000-1000-8000-00805f9b34fb": "Location and Navigation",
    "00001819-0000-1000-8000-00805f9b34fb": "Environmental Sensing",
    "0000181a-0000-1000-8000-00805f9b34fb": "Body Composition",
    "0000181b-0000-1000-8000-00805f9b34fb": "User Data",
    "0000181c-0000-1000-8000-00805f9b34fb": "Weight Scale",
    "0000181d-0000-1000-8000-00805f9b34fb": "Bond Management Service",
    "0000181e-0000-1000-8000-00805f9b34fb": "Continuous Glucose Monitoring",
    "0000181f-0000-1000-8000-00805f9b34fb": "Internet Protocol Support Service",
    "00001820-0000-1000-8000-00805f9b34fb": "Indoor Positioning",
    "00001821-0000-1000-8000-00805f9b34fb": "Pulse Oximeter Service",
    "00001822-0000-1000-8000-00805f9b34fb": "HTTP Proxy",
    "00001823-0000-1000-8000-00805f9b34fb": "Transport Discovery",
    "00001824-0000-1000-8000-00805f9b34fb": "Object Transfer Service",
    "00001825-0000-1000-8000-00805f9b34fb": "Fitness Machine Service",
    "00001826-0000-1000-8000-00805f9b34fb": "Mesh Provisioning Service",
    "00001827-0000-1000-8000-00805f9b34fb": "Mesh Proxy Service",
    "00001828-0000-1000-8000-00805f9b34fb": "Reconnection Configuration",
    "00001829-0000-1000-8000-00805f9b34fb": "Insulin Delivery",
    "0000182a-0000-1000-8000-00805f9b34fb": "Binary Sensor",
    "0000182b-0000-1000-8000-00805f9b34fb": "Emergency Configuration",
    "0000182c-0000-1000-8000-00805f9b34fb": "Audio Input Control",
    "0000182d-0000-1000-8000-00805f9b34fb": "Volume Control",
    "0000182e-0000-1000-8000-00805f9b34fb": "Volume Offset Control",
    "0000182f-0000-1000-8000-00805f9b34fb": "Coordinated Set",
    "00001830-0000-1000-8000-00805f9b34fb": "Phone Status",
    "00001831-0000-1000-8000-00805f9b34fb": "Generic Media Control Service",
    "00001832-0000-1000-8000-00805f9b34fb": "Media Control Service",
    "00001833-0000-1000-8000-00805f9b34fb": "Media Presentation Control Service",
    "00001834-0000-1000-8000-00805f9b34fb": "Audio Stream Control Service",
    "00001835-0000-1000-8000-00805f9b34fb": "Broadcast Audio Scan Service",
    "00001836-0000-1000-8000-00805f9b34fb": "Broadcast Audio Announcement Service",
    "00001837-0000-1000-8000-00805f9b34fb": "Common Audio Service",
    "00001838-0000-1000-8000-00805f9b34fb": "Microphone Control Service",
    "00001839-0000-1000-8000-00805f9b34fb": "Telephony and Media Audio Control Service",
    "0000183a-0000-1000-8000-00805f9b34fb": "Hearing Access Service",
    "0000183b-0000-1000-8000-00805f9b34fb": "Telecooperation Service",
}

AD_TYPE_MAP = {
    0x01: ("Flags", "flags"),
    0x02: ("Incomplete List of 16-bit Service UUIDs", "service_uuids_16bit_incomplete"),
    0x03: ("Complete List of 16-bit Service UUIDs", "service_uuids_16bit_complete"),
    0x04: ("Incomplete List of 32-bit Service UUIDs", "service_uuids_32bit_incomplete"),
    0x05: ("Complete List of 32-bit Service UUIDs", "service_uuids_32bit_complete"),
    0x06: ("Incomplete List of 128-bit Service UUIDs", "service_uuids_128bit_incomplete"),
    0x07: ("Complete List of 128-bit Service UUIDs", "service_uuids_128bit_complete"),
    0x08: ("Shortened Local Name", "name_short"),
    0x09: ("Complete Local Name", "name_complete"),
    0x0A: ("Tx Power Level", "tx_power"),
    0x0D: ("Class of Device", "class_of_device"),
    0x0E: ("Simple Pairing Hash C", "simple_pairing_hash"),
    0x0F: ("Simple Pairing Randomizer R", "simple_pairing_randomizer"),
    0x10: ("Device ID", "device_id"),
    0x11: ("Security Manager TK Value", "security_manager_tk"),
    0x12: ("Security Manager Out of Band Flags", "security_manager_flags"),
    0x14: ("Peripheral Connection Interval Range", "conn_interval_range"),
    0x15: ("Solicited Service UUIDs - 16-bit", "solicited_uuids_16bit"),
    0x16: ("Solicited Service UUIDs - 128-bit", "solicited_uuids_128bit"),
    0x17: ("Service Data - 16-bit UUID", "service_data_16bit"),
    0x18: ("Public Target Address", "public_target_address"),
    0x19: ("Random Target Address", "random_target_address"),
    0x1A: ("Appearance", "appearance"),
    0x1B: ("Advertising Interval", "advertising_interval"),
    0x1C: ("LE Bluetooth Device Address", "le_address"),
    0x1D: ("LE Role", "le_role"),
    0x1E: ("Simple Pairing Hash C-256", "simple_pairing_hash_256"),
    0x1F: ("Simple Pairing Randomizer R-256", "simple_pairing_randomizer_256"),
    0x20: ("List of 32-bit Service UUIDs", "service_uuids_32bit_solicited"),
    0x21: ("List of 128-bit Service UUIDs", "service_uuids_128bit_solicited"),
    0x22: ("Service Data - 32-bit UUID", "service_data_32bit"),
    0x23: ("Service Data - 128-bit UUID", "service_data_128bit"),
    0x24: ("LE Secure Connections Confirmation Value", "le_secure_confirmation"),
    0x25: ("LE Secure Connections Random Value", "le_secure_random"),
    0x26: ("URI", "uri"),
    0x27: ("Indoor Positioning", "indoor_positioning"),
    0x28: ("Transport Discovery Data", "transport_discovery"),
    0x29: ("LE Supported Features", "le_supported_features"),
    0x2A: ("Channel Map Update Indication", "channel_map_update"),
    0x2B: ("PB-ADV", "pb_adv"),
    0x2C: ("Mesh Message", "mesh_message"),
    0x2D: ("Mesh Beacon", "mesh_beacon"),
    0x2E: ("BIGInfo", "big_info"),
    0x2F: ("Broadcast_Code", "broadcast_code"),
    0x3D: ("Manufacturer Specific Data", "manufacturer_specific"),
    0xFF: ("Manufacturer Specific Data", "manufacturer_specific"),
}


class OfflineOUIDatabase:
    def __init__(self):
        self.vendors = {}
        self.mam_vendors = {}
        self.cid_vendors = {}
        self.load_count = 0
        self.is_loaded = False

    def _normalize_prefix(self, prefix):
        cleaned = prefix.strip().replace('-', '').replace(':', '').replace(' ', '').upper()
        if len(cleaned) == 6:
            return f"{cleaned[0:2]}:{cleaned[2:4]}:{cleaned[4:6]}"
        elif len(cleaned) == 7:
            return f"{cleaned[0:2]}:{cleaned[2:4]}:{cleaned[4:6]}:{cleaned[6:8]}"
        elif len(cleaned) == 9:
            return f"{cleaned[0:2]}:{cleaned[2:4]}:{cleaned[4:6]}:{cleaned[6:8]}:{cleaned[8:10]}"
        return cleaned

    def load_oui_txt(self, file_path):
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return False
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                count = 0
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            prefix = self._normalize_prefix(parts[0])
                            vendor_name = parts[-1].strip()
                            if prefix:
                                self.vendors[prefix] = vendor_name
                                count += 1
            self.load_count += count
            self.is_loaded = True
            print(f"✅ [成功] 已从 {os.path.basename(file_path)} 加载 {count} 条标准 24位 OUI 记录。")
            return True
        except Exception as e:
            print(f"❌ [错误] 加载 {file_path} 失败: {e}")
            traceback.print_exc()
            return False

    def load_oui_csv(self, file_path):
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return False
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f)
                next(reader, None)
                count = 0
                for row in reader:
                    if len(row) >= 2:
                        prefix = self._normalize_prefix(row[0])
                        vendor_name = row[-1].strip()
                        if prefix:
                            self.vendors[prefix] = vendor_name
                            count += 1
            self.load_count += count
            self.is_loaded = True
            print(f"✅ [成功] 已从 {os.path.basename(file_path)} 加载 {count} 条 CSV 前缀记录。")
            return True
        except Exception as e:
            print(f"❌ [错误] 加载 {file_path} 失败: {e}")
            traceback.print_exc()
            return False

    def load_json(self, file_path):
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return False
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                count = 0
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            prefix = item.get('mac_prefix', '')
                            vendor_name = item.get('vendor_name', '')
                            if prefix and vendor_name:
                                normalized = self._normalize_prefix(prefix)
                                if normalized:
                                    self.vendors[normalized] = vendor_name.strip()
                                    count += 1
                elif isinstance(data, dict):
                    for prefix, vendor_name in data.items():
                        normalized = self._normalize_prefix(prefix)
                        if normalized:
                            self.vendors[normalized] = vendor_name.strip()
                            count += 1
            self.load_count += count
            self.is_loaded = True
            print(f"✅ [成功] 已从 {os.path.basename(file_path)} 加载 {count} 条 JSON 记录。")
            return True
        except Exception as e:
            print(f"❌ [错误] 加载 {file_path} 失败: {e}")
            traceback.print_exc()
            return False

    def load_directory(self, directory):
        success_count = 0
        files_tried = []
        
        csv_files = ['cid.csv', 'mam.csv', 'oui36.csv']
        for f in csv_files:
            path = os.path.join(directory, f)
            if os.path.exists(path):
                files_tried.append(f)
                if self.load_oui_csv(path):
                    success_count += 1
        
        json_path = os.path.join(directory, 'mac_vendors_database.json')
        if os.path.exists(json_path):
            files_tried.append('mac_vendors_database.json')
            if self.load_json(json_path):
                success_count += 1
        
        txt_path = os.path.join(directory, 'oui.txt')
        if os.path.exists(txt_path):
            files_tried.append('oui.txt')
            if self.load_oui_txt(txt_path):
                success_count += 1
        
        if success_count > 0:
            print(f"📊 [最终统计] 数据库合并完成，内存中共有 {len(self.vendors)} 条有效 OUI 前缀记录。")
            return True
        else:
            print(f"❌ [失败] 未成功加载任何数据库文件。尝试了: {files_tried}")
            return False

    def auto_load_from_script_dir(self):
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        return self.load_directory(script_dir)


OUI_DB = OfflineOUIDatabase()


def _format_mac_address(raw_bytes):
    if len(raw_bytes) >= 6:
        return ":".join(f"{b:02X}" for b in raw_bytes)
    return raw_bytes.hex()

def _parse_class_of_device(raw_bytes):
    if len(raw_bytes) >= 3:
        cod = int.from_bytes(raw_bytes, 'little')
        major = (cod >> 8) & 0x1F
        minor = cod & 0xFF
        service_class = (cod >> 13) & 0x1FF
        service_classes = []
        if service_class & 0x001:
            service_classes.append("Limited Discoverability")
        if service_class & 0x002:
            service_classes.append("Positioning")
        if service_class & 0x004:
            service_classes.append("Networking")
        if service_class & 0x008:
            service_classes.append("Rendering")
        if service_class & 0x010:
            service_classes.append("Capturing")
        if service_class & 0x020:
            service_classes.append("Object Transfer")
        if service_class & 0x040:
            service_classes.append("Audio")
        if service_class & 0x080:
            service_classes.append("Telephony")
        if service_class & 0x100:
            service_classes.append("Information")
        major_map = {
            0: "Miscellaneous",
            1: "Computer",
            2: "Phone",
            3: "LAN/Network Access Point",
            4: "Audio/Video",
            5: "Peripheral",
            6: "Imaging",
            7: "Wearable",
            8: "Toy",
            9: "Health",
            10: "Uncategorized",
        }
        return f"Major: {major_map.get(major, f'0x{major:02X}')}, Minor: 0x{minor:02X}, Services: {', '.join(service_classes) if service_classes else 'None'}"
    return raw_bytes.hex()

def _parse_le_role(raw_bytes):
    if len(raw_bytes) >= 1:
        role = raw_bytes[0]
        if role == 0:
            return "Only Peripheral"
        elif role == 1:
            return "Only Central"
        elif role == 2:
            return "Peripheral and Central (Preferred Peripheral)"
        elif role == 3:
            return "Peripheral and Central (Preferred Central)"
    return f"0x{raw_bytes.hex()}"

def _parse_le_features(raw_bytes):
    features = []
    if len(raw_bytes) >= 1:
        byte0 = raw_bytes[0]
        if byte0 & 0x01:
            features.append("Encryption")
        if byte0 & 0x02:
            features.append("Connection Parameters Request")
        if byte0 & 0x04:
            features.append("Extended Reject Indication")
        if byte0 & 0x08:
            features.append("Slave-initiated Features Exchange")
        if byte0 & 0x10:
            features.append("LE Ping")
        if byte0 & 0x20:
            features.append("LE Data Packet Length Extension")
        if byte0 & 0x40:
            features.append("LL Privacy")
        if byte0 & 0x80:
            features.append("Extended Scanner Filter Policies")
    if len(raw_bytes) >= 2:
        byte1 = raw_bytes[1]
        if byte1 & 0x01:
            features.append("2M PHY")
        if byte1 & 0x02:
            features.append("Coded PHY")
        if byte1 & 0x04:
            features.append("Extended Advertising")
        if byte1 & 0x08:
            features.append("Periodic Advertising")
        if byte1 & 0x10:
            features.append("Channel Selection Algorithm #2")
        if byte1 & 0x20:
            features.append("LE Power Class 1")
    return ", ".join(features) if features else f"Raw: {raw_bytes.hex()}"

def parse_ad_structure(raw_hex):
    if not raw_hex:
        return {}
    
    ad_data = {}
    pos = 0
    raw_bytes = bytes.fromhex(raw_hex)
    
    while pos < len(raw_bytes):
        if pos + 1 >= len(raw_bytes):
            break
        length = raw_bytes[pos]
        if length == 0 or pos + length >= len(raw_bytes):
            break
        ad_type = raw_bytes[pos + 1]
        ad_value = raw_bytes[pos + 2: pos + 1 + length]
        
        if ad_type in AD_TYPE_MAP:
            type_name, type_key = AD_TYPE_MAP[ad_type]
            if type_key == "flags":
                flags = ad_value[0] if len(ad_value) > 0 else 0
                flag_bits = []
                if flags & 0x01:
                    flag_bits.append("LE Limited Discoverable Mode")
                if flags & 0x02:
                    flag_bits.append("LE General Discoverable Mode")
                if flags & 0x04:
                    flag_bits.append("BR/EDR Not Supported")
                if flags & 0x08:
                    flag_bits.append("Simultaneous LE and BR/EDR")
                if flags & 0x10:
                    flag_bits.append("Simultaneous LE and BR/EDR (Controller)")
                ad_data["flags"] = ",".join(flag_bits) if flag_bits else f"0x{flags:02X}"
            elif type_key in ("name_short", "name_complete"):
                try:
                    ad_data[type_key] = ad_value.decode('utf-8')
                except:
                    ad_data[type_key] = ad_value.hex()
            elif type_key == "tx_power":
                ad_data[type_key] = int(ad_value[0]) - 256 if ad_value[0] > 127 else int(ad_value[0])
            elif type_key == "appearance":
                if len(ad_value) >= 2:
                    appearance = int.from_bytes(ad_value, 'little')
                    ad_data[type_key] = appearance
            elif type_key == "advertising_interval":
                if len(ad_value) >= 2:
                    interval = int.from_bytes(ad_value, 'little')
                    ad_data[type_key] = f"{interval * 0.625}ms"
            elif type_key == "manufacturer_specific":
                if len(ad_value) >= 2:
                    company_id = int.from_bytes(ad_value[:2], 'little')
                    mfg_data = ad_value[2:].hex()
                    ad_data[f"mfg_company_id"] = company_id
                    ad_data[f"mfg_data_hex"] = mfg_data
            elif type_key.startswith("service_data"):
                ad_data[type_key] = ad_value.hex()
            elif type_key == "class_of_device":
                ad_data[type_key] = _parse_class_of_device(ad_value)
            elif type_key == "conn_interval_range":
                if len(ad_value) >= 4:
                    min_interval = int.from_bytes(ad_value[:2], 'little')
                    max_interval = int.from_bytes(ad_value[2:4], 'little')
                    ad_data[type_key] = f"Min: {min_interval * 1.25}ms, Max: {max_interval * 1.25}ms"
                else:
                    ad_data[type_key] = ad_value.hex()
            elif type_key == "public_target_address":
                ad_data[type_key] = _format_mac_address(ad_value)
            elif type_key == "random_target_address":
                ad_data[type_key] = _format_mac_address(ad_value)
            elif type_key == "le_role":
                ad_data[type_key] = _parse_le_role(ad_value)
            elif type_key == "le_supported_features":
                ad_data[type_key] = _parse_le_features(ad_value)
            elif type_key == "channel_map_update":
                if len(ad_value) >= 4:
                    map_update = int.from_bytes(ad_value[:3], 'little')
                    instant = ad_value[3]
                    channels = []
                    for i in range(37):
                        if map_update & (1 << i):
                            channels.append(str(i))
                    ad_data[type_key] = f"Channels: {', '.join(channels) if channels else 'None'}, Instant: {instant}"
                else:
                    ad_data[type_key] = ad_value.hex()
            elif type_key == "device_id":
                if len(ad_value) >= 3:
                    source = ad_value[0]
                    vendor_id = int.from_bytes(ad_value[1:3], 'little')
                    ad_data[type_key] = f"Source: 0x{source:02X}, VendorID: 0x{vendor_id:04X}"
                else:
                    ad_data[type_key] = ad_value.hex()
            elif type_key == "uri":
                try:
                    ad_data[type_key] = ad_value.decode('utf-8')
                except:
                    ad_data[type_key] = ad_value.hex()
            elif type_key == "indoor_positioning":
                if len(ad_value) >= 4:
                    pos_type = ad_value[0]
                    pos_data = ad_value[1:].hex()
                    ad_data[type_key] = f"Type: 0x{pos_type:02X}, Data: {pos_data}"
                else:
                    ad_data[type_key] = ad_value.hex()
            elif type_key == "simple_pairing_hash":
                ad_data[type_key] = f"Hash: {ad_value.hex()}"
            elif type_key == "simple_pairing_randomizer":
                ad_data[type_key] = f"Randomizer: {ad_value.hex()}"
            elif type_key == "simple_pairing_hash_256":
                ad_data[type_key] = f"Hash-256: {ad_value.hex()}"
            elif type_key == "simple_pairing_randomizer_256":
                ad_data[type_key] = f"Randomizer-256: {ad_value.hex()}"
            elif type_key == "security_manager_tk":
                if len(ad_value) >= 16:
                    ad_data[type_key] = f"TK: {ad_value.hex()}"
                else:
                    ad_data[type_key] = f"TK (partial): {ad_value.hex()}"
            elif type_key == "security_manager_flags":
                if len(ad_value) >= 1:
                    flags = ad_value[0]
                    flag_bits = []
                    if flags & 0x01:
                        flag_bits.append("OOB Data Present")
                    if flags & 0x02:
                        flag_bits.append("LE Supported")
                    if flags & 0x04:
                        flag_bits.append("Secure Connections Supported")
                    if flags & 0x08:
                        flag_bits.append("Address Type OOB")
                    if flags & 0x10:
                        flag_bits.append("Keypress Notification")
                    ad_data[type_key] = ", ".join(flag_bits) if flag_bits else f"0x{flags:02X}"
                else:
                    ad_data[type_key] = ad_value.hex()
            elif type_key == "le_address":
                ad_data[type_key] = _format_mac_address(ad_value)
            elif type_key.startswith("solicited_uuids"):
                if len(ad_value) >= 2:
                    uuid_count = len(ad_value) // 2
                    uuids = []
                    for i in range(uuid_count):
                        uuid_hex = ad_value[i*2:(i+1)*2].hex()
                        uuids.append(f"0x{uuid_hex}")
                    ad_data[type_key] = ", ".join(uuids)
                else:
                    ad_data[type_key] = ad_value.hex()
            else:
                ad_data[type_key] = ad_value.hex()
        
        pos += 1 + length
    
    return ad_data


def parse_apple_data(data_hex):
    if len(data_hex) >= 2:
        subtype = data_hex[0:2].upper()
        if subtype == "07":
            if len(data_hex) >= 20:
                prefix = data_hex[4:6]
                device_id = data_hex[6:10]
                color_code = data_hex[18:20] if len(data_hex) >= 20 else "??"
                desc = "ProximityPair"
                if prefix == "01":
                    desc = "Not Your Device"
                elif prefix == "05":
                    desc = "New Airtag"
                elif prefix == "07":
                    desc = "New Device"
                dev_name = APPLE_PROXIMITY_PAIR_DEVICES.get(device_id.upper(), f"设备 0x{device_id}")
                color_name = APPLE_PROXIMITY_COLORS.get(device_id.upper(), {}).get(color_code.upper(), color_code)
                return "Apple Proximity", f"{desc} - {dev_name} (颜色:{color_name})"
            else:
                return "Apple Proximity", "ProximityPair (数据不完整)"
        elif subtype == "12":
            if len(data_hex) >= 4:
                flags = data_hex[2:4]
                if flags == "02":
                    return "Apple Handoff", "Wi-Fi 密码共享 (正在播报)"
                if flags in ["01", "03"]:
                    return "Apple Handoff", f"跨设备接力 (Hex尾段: {data_hex[4:]})"
            return "Apple Handoff", f"子类型 0x12"
        elif subtype == "15":
            return "Apple HomeKit", "HomeKit 配件/设置广播"
        elif subtype == "1C":
            return "Apple Siri", "Siri/账号 联动广播"
        elif subtype in ("01", "10"):
            return "Apple FindMy", "FindMy 防丢网络广播"
        elif subtype == "06":
            return "Apple Continuity", "Continuity 服务发现"
        elif subtype == "08":
            return "Apple Nearby", "Nearby Actions"
        elif subtype == "20":
            return "Apple AirDrop", "AirDrop 发现"
        elif subtype == "22":
            return "Apple TV", "Apple TV 配对"
        else:
            return "Apple Other", f"子类型 0x{subtype}"
    return "Apple Other", "数据不足"


def parse_microsoft_data(data_hex):
    if data_hex.startswith("030080"):
        try:
            name = bytes.fromhex(data_hex[6:]).decode('ascii').strip('\x00')
            return "Microsoft Swift Pair", f"设备名: {name}"
        except Exception as e:
            print(f"解析 Microsoft 数据失败: {e}")
    return "Microsoft Other", f"数据: {data_hex}"


def parse_ibeacon(hex_data):
    if hex_data.startswith("0215") and len(hex_data) >= 24:
        uuid = hex_data[4:36]
        major = hex_data[36:40]
        minor = hex_data[40:44]
        tx_power_hex = hex_data[44:46]
        try:
            tx_power = int(tx_power_hex, 16) - 256 if int(tx_power_hex, 16) > 127 else int(tx_power_hex, 16)
        except Exception as e:
            print(f"解析 iBeacon TxPower 失败: {e}")
            tx_power = "N/A"
        return "Apple iBeacon", f"UUID: {uuid}, Major: {major}, Minor: {minor}, Tx: {tx_power}"
    return None


def parse_eddystone(hex_data):
    if hex_data.startswith("00"):
        namespace = hex_data[2:22]
        instance = hex_data[22:34]
        return "Eddystone (UID)", f"Namespace: {namespace}, Instance: {instance}"
    elif hex_data.startswith("10"):
        url_prefix_map = {
            "00": "http://www.",
            "01": "https://www.",
            "02": "http://",
            "03": "https://",
        }
        url_suffix_map = {
            "00": ".com/",
            "01": ".org/",
            "02": ".edu/",
            "03": ".net/",
            "04": ".info/",
            "05": ".biz/",
            "06": ".gov/",
            "07": ".com",
            "08": ".org",
            "09": ".edu",
            "0A": ".net",
            "0B": ".info",
            "0C": ".biz",
            "0D": ".gov",
        }
        try:
            prefix = url_prefix_map.get(hex_data[2:4], "")
            url_chars = hex_data[4:]
            url = prefix
            i = 0
            while i < len(url_chars):
                byte = url_chars[i:i+2]
                if byte in url_suffix_map:
                    url += url_suffix_map[byte]
                else:
                    url += chr(int(byte, 16))
                i += 2
            return "Eddystone (URL)", f"URL: {url}"
        except:
            return "Eddystone (URL)", f"URL(Hex): {hex_data[2:]}"
    elif hex_data.startswith("20"):
        try:
            tx_power = int(hex_data[2:4], 16) - 256 if int(hex_data[2:4], 16) > 127 else int(hex_data[2:4], 16)
            return "Eddystone (TLM)", f"TxPower: {tx_power}dBm"
        except:
            return "Eddystone (TLM)", f"数据: {hex_data[2:]}"
    return None


def parse_samsung_data(data_hex):
    if "420981" in data_hex:
        for dev_id, dev_name in SAMSUNG_EASY_SETUP_BUDS.items():
            if dev_id.lower() in data_hex:
                return "Samsung Buds", dev_name
        return "Samsung Buds", "未知型号"
    elif data_hex.startswith("010002000101FF000043"):
        if len(data_hex) >= 22:
            watch_id = data_hex[-2:].upper()
            return "Samsung Watch", SAMSUNG_EASY_SETUP_WATCH.get(watch_id, "未知Watch")
    return "Samsung Other", f"数据: {data_hex}"


def parse_huawei_data(data_hex):
    if len(data_hex) >= 4:
        subtype = data_hex[0:4].upper()
        if subtype == "0100":
            return "Huawei HWA", "华为快速配对服务"
        elif subtype == "0200":
            return "Huawei Share", "华为分享"
        elif subtype == "0300":
            return "Huawei FreeBuds", "华为耳机"
        elif subtype == "0400":
            return "Huawei Watch", "华为手表"
        elif subtype == "0500":
            return "Huawei Tag", "华为防丢器"
        elif subtype == "0600":
            return "Huawei HiLink", "华为智能家居"
        elif subtype == "0700":
            return "Huawei PC Connect", "华为电脑连接"
        elif data_hex.startswith("08"):
            return "Huawei Nearby", f"Nearby 广播 (数据: {data_hex[2:]})"
    return "Huawei Other", f"数据: {data_hex}"


def parse_xiaomi_data(data_hex):
    if len(data_hex) >= 2:
        subtype = data_hex[0:2].upper()
        if subtype == "01":
            if len(data_hex) >= 6:
                device_type = data_hex[2:6].upper()
                dev_map = {
                    "0001": "Mi Band 1",
                    "0002": "Mi Band 2",
                    "0003": "Mi Band 3",
                    "0004": "Mi Band 4",
                    "0005": "Mi Band 5",
                    "0006": "Mi Band 6",
                    "0007": "Mi Band 7",
                    "0008": "Mi Band 8",
                    "0101": "Mi Watch",
                    "0102": "Mi Watch S1",
                    "0103": "Mi Watch S2",
                    "0201": "Mi Air Purifier",
                    "0301": "Mi Thermometer",
                    "0401": "Mi Scale",
                    "0501": "Mi Robot Vacuum",
                    "0601": "Mi Light",
                    "0701": "Mi Camera",
                }
                return "Xiaomi Device", dev_map.get(device_type, f"未知设备 (类型码: {device_type})")
            return "Xiaomi Device", "小米设备"
        elif subtype == "02":
            return "Xiaomi MiFit", "MiFit 广播"
        elif subtype == "03":
            return "Xiaomi Mi Home", "米家智能家居"
        elif subtype == "04":
            return "Xiaomi AirDots", "小米真无线耳机"
        elif subtype == "05":
            return "Xiaomi Tag", "小米防丢器"
        elif subtype == "06":
            return "Xiaomi Car Connect", "小米车联"
    return "Xiaomi Other", f"数据: {data_hex}"


def parse_tile_data(data_hex):
    if len(data_hex) >= 8:
        tile_type = data_hex[0:2].upper()
        battery = None
        if len(data_hex) >= 10:
            battery_raw = int(data_hex[8:10], 16)
            battery = f"{battery_raw}%" if battery_raw <= 100 else "N/A"
        type_map = {
            "01": "Tile Mate",
            "02": "Tile Slim",
            "03": "Tile Pro",
            "04": "Tile Sport",
            "05": "Tile Style",
            "06": "Tile Sticker",
            "07": "Tile Pro (2020)",
            "08": "Tile Mate (2020)",
            "09": "Tile Slim (2020)",
            "0A": "Tile Sticker (2020)",
            "0B": "Tile Pro (2022)",
            "0C": "Tile Mate (2022)",
        }
        return "Tile Tracker", f"{type_map.get(tile_type, f'Tile 类型 0x{tile_type}')} (电量: {battery if battery else 'N/A'})"
    return "Tile Tracker", "Tile 防丢器"


def parse_ruuvi_data(data_hex):
    if len(data_hex) >= 4:
        format_version = data_hex[0:2].upper()
        if format_version == "03":
            return "RuuviTag", "Format 3 (RAW)"
        elif format_version == "05":
            if len(data_hex) >= 20:
                temp_raw = int(data_hex[2:6], 16)
                humidity_raw = int(data_hex[6:10], 16)
                pressure_raw = int(data_hex[10:14], 16)
                acc_x = int(data_hex[14:18], 16)
                acc_y = int(data_hex[18:22], 16)
                acc_z = int(data_hex[22:26], 16)
                temp = temp_raw / 200.0
                humidity = humidity_raw / 400.0
                pressure = pressure_raw / 100.0
                return "RuuviTag", f"Format 5 - 温度: {temp:.1f}°C, 湿度: {humidity:.1f}%, 气压: {pressure:.1f}hPa"
            return "RuuviTag", "Format 5 (数据不完整)"
        elif format_version == "06":
            return "RuuviTag", "Format 6 (LONG_RANGE)"
        elif format_version == "07":
            return "RuuviTag", "Format 7 (EXTENDED)"
        elif format_version == "08":
            return "RuuviTag", "Format 8 (MESH)"
    return "RuuviTag", "RuuviTag 传感器"


def parse_garmin_data(data_hex):
    if len(data_hex) >= 4:
        subtype = data_hex[0:4].upper()
        if subtype == "0100":
            return "Garmin Fitness", "Garmin 健身设备"
        elif subtype == "0200":
            return "Garmin Watch", "Garmin 手表"
        elif subtype == "0300":
            return "Garmin Cycling", "Garmin 骑行设备"
        elif subtype == "0400":
            return "Garmin Running", "Garmin 跑步传感器"
        elif subtype == "0500":
            return "Garmin Golf", "Garmin 高尔夫设备"
        elif subtype == "0600":
            return "Garmin Dog Collar", "Garmin 狗狗项圈"
    return "Garmin Device", f"数据: {data_hex}"


def parse_battery_service_data(data_hex):
    if len(data_hex) >= 2:
        level = int(data_hex[:2], 16)
        return f"Battery Level: {level}%"
    return ""


def parse_environmental_sensor(data_hex):
    if len(data_hex) >= 4:
        results = {}
        pos = 0
        while pos < len(data_hex):
            if pos + 2 > len(data_hex):
                break
            sensor_type = data_hex[pos:pos+2]
            length = int(data_hex[pos+2:pos+4], 16) * 2 if pos + 4 <= len(data_hex) else 0
            if pos + 4 + length > len(data_hex):
                break
            value_hex = data_hex[pos+4:pos+4+length]
            pos += 4 + length
            
            if sensor_type == "01":
                if len(value_hex) >= 4:
                    temp = int(value_hex[:4], 16) / 100.0
                    results["Temperature"] = f"{temp:.2f}°C"
            elif sensor_type == "02":
                if len(value_hex) >= 4:
                    humidity = int(value_hex[:4], 16) / 100.0
                    results["Humidity"] = f"{humidity:.2f}%"
            elif sensor_type == "03":
                if len(value_hex) >= 4:
                    pressure = int(value_hex[:4], 16) / 10.0
                    results["Pressure"] = f"{pressure:.1f} hPa"
            elif sensor_type == "04":
                if len(value_hex) >= 4:
                    altitude = int(value_hex[:4], 16) / 100.0
                    results["Altitude"] = f"{altitude:.2f} m"
            elif sensor_type == "05":
                if len(value_hex) >= 4:
                    temp_range = int(value_hex[:4], 16) / 100.0
                    results["Temperature Range"] = f"{temp_range:.2f}°C"
            elif sensor_type == "06":
                if len(value_hex) >= 2:
                    humidity_range = int(value_hex[:2], 16) / 2.0
                    results["Humidity Range"] = f"{humidity_range:.1f}%"
            elif sensor_type == "07":
                if len(value_hex) >= 4:
                    pressure_range = int(value_hex[:4], 16) / 10.0
                    results["Pressure Range"] = f"{pressure_range:.1f} hPa"
            elif sensor_type == "08":
                if len(value_hex) >= 2:
                    sensor_status = int(value_hex[:2], 16)
                    status_bits = []
                    if sensor_status & 0x01:
                        status_bits.append("Temperature Valid")
                    if sensor_status & 0x02:
                        status_bits.append("Humidity Valid")
                    if sensor_status & 0x04:
                        status_bits.append("Pressure Valid")
                    results["Sensor Status"] = ", ".join(status_bits) if status_bits else f"0x{sensor_status:02X}"
            elif sensor_type == "09":
                if len(value_hex) >= 2:
                    gas = int(value_hex[:2], 16)
                    results["Gas"] = f"{gas} kOhm"
            elif sensor_type == "0A":
                if len(value_hex) >= 4:
                    VOC_index = int(value_hex[:4], 16)
                    results["VOC Index"] = f"{VOC_index}"
            elif sensor_type == "0B":
                if len(value_hex) >= 4:
                    CO2 = int(value_hex[:4], 16)
                    results["CO2"] = f"{CO2} ppm"
        return results
    return {}


def parse_exposure_notification(data_hex):
    if len(data_hex) >= 2:
        version = int(data_hex[:2], 16)
        results = {"Version": f"v{version}"}
        if version == 1 and len(data_hex) >= 16:
            transmission_risk = int(data_hex[2:4], 16)
            results["Transmission Risk Level"] = f"{transmission_risk}"
            rolling_period = int(data_hex[4:6], 16)
            results["Rolling Period"] = f"{rolling_period}"
            rolling_start = int(data_hex[6:10], 16)
            results["Rolling Start Interval"] = f"{rolling_start}"
            results["Temporary Exposure Key"] = data_hex[10:42]
        elif version == 2 and len(data_hex) >= 4:
            results["State"] = data_hex[2:4]
        return results
    return {}


def parse_google_nearby(data_hex):
    if len(data_hex) >= 4:
        results = {}
        version = int(data_hex[:2], 16)
        results["Version"] = f"{version}"
        if version == 1 and len(data_hex) >= 6:
            length = int(data_hex[2:4], 16)
            data_type = int(data_hex[4:6], 16)
            type_names = {
                0: "Broadcast",
                1: "Discover",
                2: "Connect",
                3: "Disconnect",
                4: "Status",
                5: "Url",
                6: "Message",
            }
            results["Data Type"] = type_names.get(data_type, f"0x{data_type:02X}")
            if length > 0 and len(data_hex) >= 6 + length * 2:
                payload = data_hex[6:6 + length * 2]
                results["Payload"] = payload
        return results
    return {}


def parse_apple_continuity(data_hex):
    if len(data_hex) >= 4:
        results = {}
        subtype = data_hex[0:2].upper()
        sub_names = {
            "01": "AirDrop",
            "02": "AirPlay",
            "03": "Handoff",
            "04": "Instant Hotspot",
            "05": "Tethering",
            "06": "Personal Hotspot",
            "07": "Game Controller",
            "08": "Nearby",
            "09": "WiFi Password Sharing",
            "0A": "Universal Clipboard",
        }
        results["Subtype"] = sub_names.get(subtype, f"0x{subtype}")
        if len(data_hex) >= 6:
            flags = int(data_hex[2:4], 16)
            flag_bits = []
            if flags & 0x01:
                flag_bits.append("Available")
            if flags & 0x02:
                flag_bits.append("Busy")
            if flags & 0x04:
                flag_bits.append("Locked")
            results["Flags"] = ", ".join(flag_bits) if flag_bits else f"0x{flags:02X}"
        return results
    return {}


def parse_eddystone_tlm(data_hex):
    if len(data_hex) >= 18:
        version = int(data_hex[:2], 16)
        battery_voltage = int(data_hex[2:6], 16)
        temperature_raw = int(data_hex[6:8], 16)
        temperature = temperature_raw - 128 if temperature_raw > 127 else temperature_raw
        pdu_count = int(data_hex[8:16], 16)
        uptime = int(data_hex[16:24], 16) if len(data_hex) >= 24 else 0
        return {
            "Version": f"{version}",
            "Battery Voltage": f"{battery_voltage} mV",
            "Temperature": f"{temperature}°C",
            "PDU Count": f"{pdu_count}",
            "Uptime": f"{uptime} seconds",
        }
    return {}


def parse_service_data_by_uuid(uuid, data_hex):
    uuid_lower = uuid.lower()
    results = {}
    
    if uuid_lower == "0000180f" or uuid_lower.endswith("180f"):
        if len(data_hex) >= 2:
            level = int(data_hex[:2], 16)
            results["Battery Level"] = f"{level}%"
            if len(data_hex) >= 4:
                flags = int(data_hex[2:4], 16)
                flag_bits = []
                if flags & 0x01:
                    flag_bits.append("Battery Level Known")
                if flags & 0x02:
                    flag_bits.append("Charging")
                if flags & 0x04:
                    flag_bits.append("Service Supported")
                results["Battery Flags"] = ", ".join(flag_bits) if flag_bits else f"0x{flags:02X}"
    
    elif uuid_lower == "0000181a" or uuid_lower.endswith("181a"):
        env_data = parse_environmental_sensor(data_hex)
        results.update(env_data)
    
    elif uuid_lower == "0000fd6f" or uuid_lower.endswith("fd6f"):
        exposure_data = parse_exposure_notification(data_hex)
        results.update(exposure_data)
    
    elif uuid_lower == "0000fe9f" or uuid_lower.endswith("fe9f"):
        nearby_data = parse_google_nearby(data_hex)
        results.update(nearby_data)
    
    elif uuid_lower == "0000feaa" or uuid_lower.endswith("feaa"):
        eddystone_data = parse_eddystone_tlm(data_hex)
        results.update(eddystone_data)
    
    elif uuid_lower == "0000fd89" or uuid_lower.endswith("fd89"):
        continuity_data = parse_apple_continuity(data_hex)
        results.update(continuity_data)
    
    elif uuid_lower == "0000ffb0" or uuid_lower.endswith("ffb0"):
        if len(data_hex) >= 4:
            results["Beacon Type"] = data_hex[:2]
            results["Beacon Data"] = data_hex[2:]
    
    elif uuid_lower == "0000ffb2" or uuid_lower.endswith("ffb2"):
        if len(data_hex) >= 4:
            results["Sensor Type"] = data_hex[:2]
            if len(data_hex) >= 8:
                value = int(data_hex[2:8], 16) / 100.0
                results["Sensor Value"] = f"{value}"
    
    elif uuid_lower == "0000ffcc" or uuid_lower.endswith("ffcc"):
        if len(data_hex) >= 8:
            results["Beacon ID"] = data_hex[:8]
            if len(data_hex) >= 12:
                major = int(data_hex[8:12], 16)
                results["Major"] = f"{major}"
            if len(data_hex) >= 16:
                minor = int(data_hex[12:16], 16)
                results["Minor"] = f"{minor}"
    
    elif uuid_lower == "0000181b" or uuid_lower.endswith("181b"):
        if len(data_hex) >= 2:
            interval = int(data_hex[:2], 16) * 1.25
            results["Heart Rate Min Interval"] = f"{interval} ms"
        if len(data_hex) >= 4:
            max_interval = int(data_hex[2:4], 16) * 1.25
            results["Heart Rate Max Interval"] = f"{max_interval} ms"
    
    elif uuid_lower == "0000180d" or uuid_lower.endswith("180d"):
        if len(data_hex) >= 2:
            flags = int(data_hex[:2], 16)
            flag_bits = []
            if flags & 0x01:
                flag_bits.append("Sensor Contact")
            if flags & 0x02:
                flag_bits.append("Energy Expended")
            if flags & 0x04:
                flag_bits.append("RR-Interval")
            results["Heart Rate Flags"] = ", ".join(flag_bits) if flag_bits else f"0x{flags:02X}"
    
    elif uuid_lower == "0000fe2c" or uuid_lower.endswith("fe2c"):
        if len(data_hex) >= 4:
            model_id = data_hex[:4]
            results["Google Fast Pair Model ID"] = model_id
            if len(data_hex) >= 8:
                action = int(data_hex[4:6], 16)
                actions = {
                    0: "Initial Pairing",
                    1: "Re-pairing",
                    2: "Key-based Pairing",
                    3: "BLE Advertisement",
                }
                results["Action"] = actions.get(action, f"0x{action:02X}")
    
    elif uuid_lower == "00001822" or uuid_lower.endswith("1822"):
        if len(data_hex) >= 6:
            pressure_kPa = int(data_hex[:4], 16) / 10.0
            results["Systolic Pressure"] = f"{pressure_kPa} kPa"
            if len(data_hex) >= 10:
                diastolic_kPa = int(data_hex[4:8], 16) / 10.0
                results["Diastolic Pressure"] = f"{diastolic_kPa} kPa"
    
    elif uuid_lower == "0000181c" or uuid_lower.endswith("181c"):
        if len(data_hex) >= 4:
            weight = int(data_hex[:4], 16) / 100.0
            results["Weight"] = f"{weight} kg"
    
    elif uuid_lower == "0000181d" or uuid_lower.endswith("181d"):
        if len(data_hex) >= 2:
            flags = int(data_hex[:2], 16)
            flag_bits = []
            if flags & 0x01:
                flag_bits.append("Bondable")
            if flags & 0x02:
                flag_bits.append("MITM Protection")
            if flags & 0x04:
                flag_bits.append("Secure Connections")
            results["Bond Management Flags"] = ", ".join(flag_bits) if flag_bits else f"0x{flags:02X}"
    
    elif uuid_lower == "0000182a" or uuid_lower.endswith("182a"):
        if len(data_hex) >= 2:
            type_id = int(data_hex[:2], 16)
            type_names = {
                0: "No Sensor",
                1: "Contact Sensor",
                2: "Push Button",
                3: "Motion Sensor",
                4: "Door/Window Sensor",
                5: "Temperature Sensor",
                6: "Humidity Sensor",
                7: "Occupancy Sensor",
            }
            results["Binary Sensor Type"] = type_names.get(type_id, f"0x{type_id:02X}")
    
    return results


def identify_protocol(adv_info):
    mfg_data = adv_info.get("manufacturer_data", {})
    if str(APPLE_COMPANY_ID) in mfg_data:
        data = mfg_data[str(APPLE_COMPANY_ID)]
        ib = parse_ibeacon(data)
        if ib:
            return ib
        return parse_apple_data(data)
    if str(MICROSOFT_COMPANY_ID) in mfg_data:
        return parse_microsoft_data(mfg_data[str(MICROSOFT_COMPANY_ID)])
    if str(SAMSUNG_COMPANY_ID) in mfg_data:
        return parse_samsung_data(mfg_data[str(SAMSUNG_COMPANY_ID)])
    if str(GOOGLE_COMPANY_ID) in mfg_data:
        return "Google Nearby", f"数据: {mfg_data[str(GOOGLE_COMPANY_ID)]}"
    if str(HUAWEI_COMPANY_ID) in mfg_data:
        return parse_huawei_data(mfg_data[str(HUAWEI_COMPANY_ID)])
    if str(XIAOMI_COMPANY_ID) in mfg_data:
        return parse_xiaomi_data(mfg_data[str(XIAOMI_COMPANY_ID)])
    if str(TILE_COMPANY_ID) in mfg_data:
        return parse_tile_data(mfg_data[str(TILE_COMPANY_ID)])
    if str(RUUVI_COMPANY_ID) in mfg_data:
        return parse_ruuvi_data(mfg_data[str(RUUVI_COMPANY_ID)])
    if str(GARMIN_COMPANY_ID) in mfg_data:
        return parse_garmin_data(mfg_data[str(GARMIN_COMPANY_ID)])

    service_data = adv_info.get("service_data", {})
    if FAST_PAIR_SERVICE_UUID in service_data:
        return "Google Fast Pair", f"Model ID: {service_data[FAST_PAIR_SERVICE_UUID]}"
    if "000019fe" in service_data:
        return parse_eddystone(service_data["000019fe"])
    if "0000feaa" in service_data:
        return "Google Nearby (Eddystone)", f"数据: {service_data['0000feaa']}"
    
    service_uuids = adv_info.get("service_uuids", [])
    uuid_strings = [str(uuid).lower() for uuid in service_uuids]
    
    if "0000180f" in uuid_strings:
        battery_info = ""
        if "0000180f" in service_data:
            battery_info = parse_battery_service_data(service_data["0000180f"])
        return "BLE Battery Service", battery_info if battery_info else "支持电池服务"
    
    if "0000180d" in uuid_strings:
        return "BLE Heart Rate", "心率监测设备"
    
    if "00001814" in uuid_strings:
        return "BLE Running Speed", "跑步速度传感器"
    
    if "00001816" in uuid_strings:
        return "BLE Cycling Speed", "骑行速度传感器"
    
    if "0000181a" in uuid_strings:
        return "BLE Environmental Sensing", "环境传感器"
    
    if "00001819" in uuid_strings:
        return "BLE Environmental Sensing", "环境感知设备"
    
    if "0000ffe0" in uuid_strings:
        return "BLE Vendor Specific", "厂商自定义服务"
    
    if service_uuids:
        known_services = []
        for uuid in service_uuids:
            uuid_str = str(uuid).lower()
            if uuid_str in BLE_STANDARD_SERVICES:
                known_services.append(BLE_STANDARD_SERVICES[uuid_str])
        if known_services:
            return "BLE Standard Service", ", ".join(known_services[:3])
    
    name = adv_info.get("name", "").lower()
    if "airtag" in name:
        return "Apple AirTag", "苹果防丢器"
    if "airpods" in name:
        return "Apple AirPods", "苹果无线耳机"
    if "watch" in name and ("apple" in name or "iphone" in name):
        return "Apple Watch", "苹果手表"
    if "galaxy" in name:
        return "Samsung Galaxy", "三星设备"
    if "huawei" in name:
        return "Huawei Device", "华为设备"
    if "xiaomi" in name:
        return "Xiaomi Device", "小米设备"
    if "mi band" in name:
        return "Xiaomi Mi Band", "小米手环"
    if "fitbit" in name:
        return "Fitbit Device", "Fitbit设备"
    if "amazfit" in name:
        return "Amazfit Device", "华米设备"
    if "headphones" in name or "earbuds" in name or "buds" in name:
        return "Bluetooth Headphones", "蓝牙耳机"
    if "speaker" in name:
        return "Bluetooth Speaker", "蓝牙音箱"
    if "mouse" in name:
        return "Bluetooth Mouse", "蓝牙鼠标"
    if "keyboard" in name:
        return "Bluetooth Keyboard", "蓝牙键盘"
    if "light" in name or "bulb" in name:
        return "Smart Light", "智能灯"
    if "thermometer" in name:
        return "Thermometer", "温度计"
    if "scale" in name:
        return "Smart Scale", "智能秤"
    if "lock" in name:
        return "Smart Lock", "智能锁"
    if "gateway" in name or "hub" in name:
        return "Smart Gateway", "智能网关"
    
    return "Unknown", ""


def calc_distance(rssi, tx_power=None):
    if tx_power is None or tx_power == 0:
        tx_power = -59
    try:
        rssi_val = int(rssi)
        tx_val = int(tx_power)
        if rssi_val > 0 or tx_val > 0:
            return "N/A"
        distance = 10 ** ((rssi_val - tx_val) / 20.0)
        if distance < 0.1:
            return f"{0.1:.1f}m"
        elif distance > 100:
            return f">100m"
        return f"{distance:.1f}m"
    except Exception as e:
        return "N/A"


def get_mac_type(mac):
    if not mac or len(mac) < 2:
        return "无效地址"
    try:
        first_byte = int(mac[:2], 16)
        bit6 = (first_byte >> 6) & 1
        bit5 = (first_byte >> 5) & 1
        if bit6 == 0 and bit5 == 0:
            return "公共地址"
        elif bit6 == 0 and bit5 == 1:
            return "随机静态地址"
        elif bit6 == 1 and bit5 == 0:
            return "可解析私有地址"
        else:
            return "不可解析私有地址"
    except Exception as e:
        print(f"解析 MAC 地址失败: {e}")
        return "无效地址"


def enrich_vendor(adv_info):
    mac = adv_info.get("mac", "")
    adv_info["mac_type"] = get_mac_type(mac)
    
    if not mac:
        adv_info["vendor"] = "未知厂商"
        return
    
    prefix_24 = ":".join(mac.split(":")[:3]).upper()
    prefix_28 = ":".join(mac.split(":")[:3] + [mac.split(":")[3][:1]]).upper() if len(mac.split(":")) > 3 else ""
    prefix_36 = ":".join(mac.split(":")[:4]).upper() if len(mac.split(":")) > 3 else ""
    
    vendor_name = None
    if OUI_DB.is_loaded:
        if prefix_36 and prefix_36 in OUI_DB.vendors:
            vendor_name = OUI_DB.vendors[prefix_36]
        elif prefix_28 and prefix_28 in OUI_DB.vendors:
            vendor_name = OUI_DB.vendors[prefix_28]
        elif prefix_24 in OUI_DB.vendors:
            vendor_name = OUI_DB.vendors[prefix_24]
    
    if not vendor_name:
        mfg_data = adv_info.get("manufacturer_data", {})
        for cid_str in mfg_data:
            try:
                cid = int(cid_str)
                if cid in MANUFACTURER_ID_MAP:
                    vendor_name = MANUFACTURER_ID_MAP[cid]
                    break
            except ValueError:
                continue
    
    adv_info["vendor"] = vendor_name if vendor_name else "未知厂商"


class BLEScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BLE 深度扫描器 v7.0")
        self.root.geometry("1400x900")
        
        self.running = False
        self.thread = None
        self.writer_thread = None
        self.stop_event = None
        self.packet_count = 0
        self.dropped_packets = 0
        
        self.raw_queue = queue.Queue(maxsize=10000)
        self.file_queue = queue.Queue(maxsize=10000)
        
        self.row_data_map = {}
        self.device_frequency = {}
        self.device_rssi_history = {}
        
        self.create_widgets()
        self.auto_load_database()
        self.update_gui()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.start_btn = ttk.Button(top_frame, text="启动扫描", command=self.start_scan)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(top_frame, text="停止扫描", command=self.stop_scan, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(top_frame, text="保存当前数据", command=self.save_current_data)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = ttk.Button(top_frame, text="导出广播帧", command=self.export_broadcast_frames)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        self.load_db_btn = ttk.Button(top_frame, text="加载厂商数据库", command=self.load_database)
        self.load_db_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(top_frame, text="RSSI 范围:").pack(side=tk.LEFT, padx=(15, 5))
        self.rssi_min = ttk.Spinbox(top_frame, from_=-120, to=0, width=5)
        self.rssi_min.set(-100)
        self.rssi_min.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(top_frame, text="~").pack(side=tk.LEFT, padx=2)
        
        self.rssi_max = ttk.Spinbox(top_frame, from_=-120, to=0, width=5)
        self.rssi_max.set(0)
        self.rssi_max.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(top_frame, text="扫描模式:").pack(side=tk.LEFT, padx=(15, 5))
        self.scan_mode = ttk.Combobox(top_frame, values=["passive", "active"], width=8)
        self.scan_mode.set("passive")
        self.scan_mode.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(top_frame, text="目标设备:").pack(side=tk.LEFT, padx=(15, 5))
        self.target_devices = ttk.Entry(top_frame, width=30)
        self.target_devices.insert(0, "")
        self.target_devices.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(top_frame, text="输出文件:").pack(side=tk.LEFT, padx=(15, 5))
        self.output_file = ttk.Entry(top_frame, width=40)
        self.output_file.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ble_all_packets.json"))
        self.output_file.pack(side=tk.LEFT, padx=5)
        
        browse_btn = ttk.Button(top_frame, text="浏览", command=self.browse_output)
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(top_frame, text="就绪 - 点击启动扫描", foreground="green")
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        table_frame = ttk.Frame(notebook)
        notebook.add(table_frame, text="扫描列表")
        
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(table_frame, yscrollcommand=scrollbar.set, show="headings")
        scrollbar.config(command=self.tree.yview)
        
        self.tree["columns"] = ("time", "mac", "mac_type", "vendor", "protocol", "details", "name", "rssi", "distance", "frequency")
        self.tree.column("time", width=160, anchor=tk.CENTER)
        self.tree.column("mac", width=180, anchor=tk.CENTER)
        self.tree.column("mac_type", width=120, anchor=tk.CENTER)
        self.tree.column("vendor", width=180, anchor=tk.W)
        self.tree.column("protocol", width=140, anchor=tk.CENTER)
        self.tree.column("details", width=180, anchor=tk.W)
        self.tree.column("name", width=140, anchor=tk.W)
        self.tree.column("rssi", width=60, anchor=tk.CENTER)
        self.tree.column("distance", width=70, anchor=tk.CENTER)
        self.tree.column("frequency", width=70, anchor=tk.CENTER)
        
        self.tree.heading("time", text="时间")
        self.tree.heading("mac", text="MAC地址")
        self.tree.heading("mac_type", text="MAC类型")
        self.tree.heading("vendor", text="厂商")
        self.tree.heading("protocol", text="协议类型")
        self.tree.heading("details", text="协议详情")
        self.tree.heading("name", text="设备名称")
        self.tree.heading("rssi", text="RSSI")
        self.tree.heading("distance", text="距离")
        self.tree.heading("frequency", text="频次")
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        detail_frame = ttk.Frame(notebook)
        notebook.add(detail_frame, text="设备详情")
        
        self.detail_text = tk.Text(detail_frame, wrap=tk.WORD)
        self.detail_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        self._create_system_monitor(notebook)
    
    def _create_system_monitor(self, notebook):
        monitor_frame = ttk.Frame(notebook)
        notebook.add(monitor_frame, text="系统监控")
        
        monitor_frame.grid_columnconfigure(0, weight=1)
        monitor_frame.grid_columnconfigure(1, weight=1)
        
        cpu_frame = ttk.LabelFrame(monitor_frame, text="CPU 监控")
        cpu_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        cpu_frame.grid_columnconfigure(0, weight=1)
        
        self.cpu_usage_var = tk.StringVar(value="0%")
        ttk.Label(cpu_frame, text="CPU 使用率:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(cpu_frame, textvariable=self.cpu_usage_var, font=("Arial", 16, "bold")).grid(row=0, column=1, padx=5, pady=2, sticky="e")
        
        self.cpu_bar = ttk.Progressbar(cpu_frame, length=300, mode="determinate")
        self.cpu_bar.grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        
        self.cpu_cores_var = tk.StringVar(value="")
        ttk.Label(cpu_frame, textvariable=self.cpu_cores_var).grid(row=2, column=0, columnspan=2, padx=5, pady=2, sticky="w")
        
        self.cpu_temp_var = tk.StringVar(value="")
        ttk.Label(cpu_frame, textvariable=self.cpu_temp_var).grid(row=3, column=0, columnspan=2, padx=5, pady=2, sticky="w")
        
        mem_frame = ttk.LabelFrame(monitor_frame, text="内存监控")
        mem_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        mem_frame.grid_columnconfigure(0, weight=1)
        
        self.mem_usage_var = tk.StringVar(value="0%")
        ttk.Label(mem_frame, text="内存使用率:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(mem_frame, textvariable=self.mem_usage_var, font=("Arial", 16, "bold")).grid(row=0, column=1, padx=5, pady=2, sticky="e")
        
        self.mem_bar = ttk.Progressbar(mem_frame, length=300, mode="determinate")
        self.mem_bar.grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        
        self.mem_detail_var = tk.StringVar(value="")
        ttk.Label(mem_frame, textvariable=self.mem_detail_var).grid(row=2, column=0, columnspan=2, padx=5, pady=2, sticky="w")
        
        disk_frame = ttk.LabelFrame(monitor_frame, text="磁盘监控")
        disk_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        disk_frame.grid_columnconfigure(0, weight=1)
        disk_frame.grid_columnconfigure(1, weight=1)
        disk_frame.grid_columnconfigure(2, weight=1)
        disk_frame.grid_columnconfigure(3, weight=1)
        
        ttk.Label(disk_frame, text="驱动器").grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(disk_frame, text="总量").grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(disk_frame, text="已用").grid(row=0, column=2, padx=5, pady=2)
        ttk.Label(disk_frame, text="使用率").grid(row=0, column=3, padx=5, pady=2)
        
        self.disk_labels = []
        row = 1
        try:
            for disk in psutil.disk_partitions(all=False):
                if disk.fstype:
                    label1 = ttk.Label(disk_frame, text=disk.device)
                    label1.grid(row=row, column=0, padx=5, pady=1)
                    label2 = ttk.Label(disk_frame, text="")
                    label2.grid(row=row, column=1, padx=5, pady=1)
                    label3 = ttk.Label(disk_frame, text="")
                    label3.grid(row=row, column=2, padx=5, pady=1)
                    label4 = ttk.Label(disk_frame, text="")
                    label4.grid(row=row, column=3, padx=5, pady=1)
                    bar = ttk.Progressbar(disk_frame, length=150, mode="determinate")
                    bar.grid(row=row, column=4, padx=5, pady=1)
                    self.disk_labels.append((disk.device, label1, label2, label3, label4, bar))
                    row += 1
        except:
            pass
        
        net_frame = ttk.LabelFrame(monitor_frame, text="网络监控")
        net_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        net_frame.grid_columnconfigure(0, weight=1)
        net_frame.grid_columnconfigure(1, weight=1)
        
        self.net_sent_var = tk.StringVar(value="0 KB/s")
        ttk.Label(net_frame, text="发送速度:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(net_frame, textvariable=self.net_sent_var).grid(row=0, column=1, padx=5, pady=2, sticky="e")
        
        self.net_recv_var = tk.StringVar(value="0 KB/s")
        ttk.Label(net_frame, text="接收速度:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(net_frame, textvariable=self.net_recv_var).grid(row=1, column=1, padx=5, pady=2, sticky="e")
        
        self.net_total_var = tk.StringVar(value="")
        ttk.Label(net_frame, textvariable=self.net_total_var).grid(row=2, column=0, columnspan=2, padx=5, pady=2, sticky="w")
        
        proc_frame = ttk.LabelFrame(monitor_frame, text="进程监控 (CPU占用最高)")
        proc_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        proc_frame.grid_columnconfigure(0, weight=1)
        proc_frame.grid_columnconfigure(1, weight=1)
        proc_frame.grid_columnconfigure(2, weight=1)
        proc_frame.grid_columnconfigure(3, weight=1)
        
        ttk.Label(proc_frame, text="进程名").grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(proc_frame, text="PID").grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(proc_frame, text="CPU%").grid(row=0, column=2, padx=5, pady=2)
        ttk.Label(proc_frame, text="内存(MB)").grid(row=0, column=3, padx=5, pady=2)
        
        self.proc_labels = []
        for i in range(10):
            name_label = ttk.Label(proc_frame, text="")
            name_label.grid(row=i+1, column=0, padx=5, pady=1, sticky="w")
            pid_label = ttk.Label(proc_frame, text="")
            pid_label.grid(row=i+1, column=1, padx=5, pady=1)
            cpu_label = ttk.Label(proc_frame, text="")
            cpu_label.grid(row=i+1, column=2, padx=5, pady=1)
            mem_label = ttk.Label(proc_frame, text="")
            mem_label.grid(row=i+1, column=3, padx=5, pady=1)
            self.proc_labels.append((name_label, pid_label, cpu_label, mem_label))
        
        self.sys_info_var = tk.StringVar(value="")
        ttk.Label(monitor_frame, textvariable=self.sys_info_var, font=("Arial", 8)).grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        self._net_io_counters = psutil.net_io_counters()
        self._last_net_sent = self._net_io_counters.bytes_sent
        self._last_net_recv = self._net_io_counters.bytes_recv
        self._last_net_time = time.time()
        
        self._update_system_monitor()
    
    def _format_size(self, bytes_size):
        if bytes_size < 1024:
            return f"{bytes_size} B"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size / 1024:.2f} KB"
        elif bytes_size < 1024 * 1024 * 1024:
            return f"{bytes_size / (1024 * 1024):.2f} MB"
        else:
            return f"{bytes_size / (1024 * 1024 * 1024):.2f} GB"
    
    def _update_system_monitor(self):
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.cpu_usage_var.set(f"{cpu_percent}%")
            self.cpu_bar.config(value=cpu_percent)
            
            cpu_count = psutil.cpu_count(logical=True)
            cpu_physical = psutil.cpu_count(logical=False)
            cpu_freq = psutil.cpu_freq()
            freq_str = f"{cpu_freq.current:.1f} MHz" if cpu_freq else "N/A"
            self.cpu_cores_var.set(f"逻辑核心: {cpu_count}, 物理核心: {cpu_physical}, 当前频率: {freq_str}")
            
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    core_temp = ""
                    for name, entries in temps.items():
                        for entry in entries:
                            if "core" in name.lower() or name.lower() == "cpu":
                                core_temp = f"CPU温度: {entry.current:.1f}°C"
                                break
                        if core_temp:
                            break
                    if not core_temp and temps:
                        first_key = list(temps.keys())[0]
                        core_temp = f"{first_key}: {temps[first_key][0].current:.1f}°C"
                    self.cpu_temp_var.set(core_temp)
                else:
                    self.cpu_temp_var.set("CPU温度: 暂不支持")
            except:
                self.cpu_temp_var.set("CPU温度: 暂不支持")
            
            mem = psutil.virtual_memory()
            self.mem_usage_var.set(f"{mem.percent}%")
            self.mem_bar.config(value=mem.percent)
            self.mem_detail_var.set(f"总内存: {self._format_size(mem.total)}, 已用: {self._format_size(mem.used)}, 可用: {self._format_size(mem.available)}")
            
            for device, label1, label2, label3, label4, bar in self.disk_labels:
                try:
                    usage = psutil.disk_usage(device)
                    label2.config(text=self._format_size(usage.total))
                    label3.config(text=self._format_size(usage.used))
                    label4.config(text=f"{usage.percent}%")
                    bar.config(value=usage.percent)
                except:
                    label2.config(text="N/A")
                    label3.config(text="N/A")
                    label4.config(text="N/A")
                    bar.config(value=0)
            
            current_time = time.time()
            elapsed = current_time - self._last_net_time
            if elapsed > 0:
                try:
                    net_io = psutil.net_io_counters()
                    sent_bytes = net_io.bytes_sent - self._last_net_sent
                    recv_bytes = net_io.bytes_recv - self._last_net_recv
                    sent_kbs = sent_bytes / elapsed / 1024
                    recv_kbs = recv_bytes / elapsed / 1024
                    
                    if sent_kbs < 1024:
                        self.net_sent_var.set(f"{sent_kbs:.2f} KB/s")
                    else:
                        self.net_sent_var.set(f"{sent_kbs / 1024:.2f} MB/s")
                    
                    if recv_kbs < 1024:
                        self.net_recv_var.set(f"{recv_kbs:.2f} KB/s")
                    else:
                        self.net_recv_var.set(f"{recv_kbs / 1024:.2f} MB/s")
                    
                    self.net_total_var.set(f"累计发送: {self._format_size(net_io.bytes_sent)}, 累计接收: {self._format_size(net_io.bytes_recv)}")
                    
                    self._last_net_sent = net_io.bytes_sent
                    self._last_net_recv = net_io.bytes_recv
                    self._last_net_time = current_time
                except:
                    pass
            
            try:
                processes = sorted(psutil.process_iter(['name', 'pid', 'cpu_percent', 'memory_info']),
                                   key=lambda p: p.info.get('cpu_percent', 0), reverse=True)[:10]
                
                for i, proc in enumerate(processes):
                    info = proc.info
                    name_label, pid_label, cpu_label, mem_label = self.proc_labels[i]
                    name_label.config(text=info.get('name', '')[:20])
                    pid_label.config(text=str(info.get('pid', '')))
                    cpu_label.config(text=f"{info.get('cpu_percent', 0):.1f}%")
                    mem_mb = info.get('memory_info', {}).rss / (1024 * 1024) if info.get('memory_info') else 0
                    mem_label.config(text=f"{mem_mb:.1f}")
            except:
                pass
            
            try:
                boot_time = psutil.boot_time()
                boot_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(boot_time))
                uptime_sec = time.time() - boot_time
                uptime_hours = int(uptime_sec / 3600)
                uptime_minutes = int((uptime_sec % 3600) / 60)
                self.sys_info_var.set(f"系统启动时间: {boot_str}, 运行时长: {uptime_hours}小时{uptime_minutes}分钟")
            except:
                pass
            
        except Exception as e:
            print(f"系统监控更新失败: {e}")
        
        self.root.after(1000, self._update_system_monitor)
    
    def auto_load_database(self):
        success = OUI_DB.auto_load_from_script_dir()
        if success:
            self.status_label.config(text=f"就绪 - 已加载 {OUI_DB.load_count} 条厂商记录", foreground="green")
        else:
            self.status_label.config(text="就绪 - 厂商数据库未加载", foreground="orange")
    
    def load_database(self):
        folder_path = filedialog.askdirectory(title="选择厂商数据库文件夹")
        if folder_path:
            success = OUI_DB.load_directory(folder_path)
            if success:
                self.status_label.config(text=f"已加载 {OUI_DB.load_count} 条厂商记录", foreground="green")
            else:
                messagebox.showerror("错误", "加载数据库失败")
    
    def browse_output(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")])
        if file_path:
            self.output_file.delete(0, tk.END)
            self.output_file.insert(0, file_path)
    
    def start_scan(self):
        if self.running:
            return
        try:
            rssi_min = int(self.rssi_min.get())
            rssi_max = int(self.rssi_max.get())
        except Exception as e:
            messagebox.showerror("错误", "RSSI 值须为整数")
            return
        
        self.packet_count = 0
        self.dropped_packets = 0
        self.row_data_map.clear()
        self.device_frequency.clear()
        self.device_rssi_history.clear()
        self.tree.delete(*self.tree.get_children())
        self.detail_text.delete(1.0, tk.END)
        while not self.raw_queue.empty():
            self.raw_queue.get_nowait()
        while not self.file_queue.empty():
            self.file_queue.get_nowait()
        
        self.stop_event = threading.Event()
        self.writer_thread = threading.Thread(target=self._file_writer, args=(self.output_file.get(),), daemon=False)
        self.writer_thread.start()
        
        scan_mode_value = self.scan_mode.get()
        self.thread = threading.Thread(target=self._run_scan, args=(rssi_min, rssi_max, scan_mode_value), daemon=True)
        self.thread.start()
        
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.root.after(0, self.update_gui)
        target = self.target_devices.get().strip()
        if target:
            self.status_label.config(text=f"扫描中... 目标设备: {target}", foreground="blue")
        else:
            self.status_label.config(text="扫描中... (全部设备)", foreground="blue")
    
    def stop_scan(self):
        if not self.running:
            return
        self.running = False
        self.stop_event.set()
        self.status_label.config(text="停止中...", foreground="orange")
    
    async def _async_scan(self, loop, rssi_min, rssi_max, scan_mode):
        def callback(device, advertisement_data):
            try:
                rssi = advertisement_data.rssi
                if rssi < rssi_min or rssi > rssi_max:
                    return
                
                mfg_data = {str(cid): data.hex() for cid, data in advertisement_data.manufacturer_data.items()}
                service_data = {str(uuid): data.hex() for uuid, data in advertisement_data.service_data.items()}
                raw = getattr(advertisement_data, "raw_data", None)
                raw_hex = raw.hex() if raw is not None else None
                
                ad_struct = parse_ad_structure(raw_hex)
                
                name = advertisement_data.local_name or device.name or ""
                connectable = getattr(advertisement_data, "connectable", None)
                appearance = getattr(advertisement_data, "appearance", None)
                
                mac_lower = device.address.lower()
                if mac_lower not in self.device_rssi_history:
                    self.device_rssi_history[mac_lower] = []
                self.device_rssi_history[mac_lower].append((time.time(), rssi))
                if len(self.device_rssi_history[mac_lower]) > 50:
                    self.device_rssi_history[mac_lower] = self.device_rssi_history[mac_lower][-50:]
                
                rssi_history = self.device_rssi_history[mac_lower]
                rssi_avg = sum(r for _, r in rssi_history) / len(rssi_history) if rssi_history else rssi
                rssi_min_val = min(r for _, r in rssi_history) if rssi_history else rssi
                rssi_max_val = max(r for _, r in rssi_history) if rssi_history else rssi
                
                adv_info = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    "timestamp_unix": time.time(),
                    "mac": device.address,
                    "address_type": getattr(device, "address_type", None),
                    "name": name or "N/A",
                    "name_short": ad_struct.get("name_short", "N/A"),
                    "name_complete": ad_struct.get("name_complete", "N/A"),
                    "rssi": rssi,
                    "rssi_avg": round(rssi_avg, 1),
                    "rssi_min": rssi_min_val,
                    "rssi_max": rssi_max_val,
                    "rssi_samples": len(rssi_history),
                    "tx_power": advertisement_data.tx_power,
                    "is_connectable": connectable,
                    "appearance": appearance,
                    "appearance_desc": self._get_appearance_desc(appearance),
                    "flags": ad_struct.get("flags", "N/A"),
                    "advertising_interval": ad_struct.get("advertising_interval", "N/A"),
                    "conn_interval_range": ad_struct.get("conn_interval_range", "N/A"),
                    "class_of_device": ad_struct.get("class_of_device", "N/A"),
                    "le_role": ad_struct.get("le_role", "N/A"),
                    "le_supported_features": ad_struct.get("le_supported_features", "N/A"),
                    "public_target_address": ad_struct.get("public_target_address", "N/A"),
                    "random_target_address": ad_struct.get("random_target_address", "N/A"),
                    "device_id": ad_struct.get("device_id", "N/A"),
                    "uri": ad_struct.get("uri", "N/A"),
                    "indoor_positioning": ad_struct.get("indoor_positioning", "N/A"),
                    "channel_map_update": ad_struct.get("channel_map_update", "N/A"),
                    "manufacturer_data": mfg_data,
                    "service_uuids": [str(uuid) for uuid in advertisement_data.service_uuids],
                    "service_data": service_data,
                    "service_data_parsed": {},
                    "service_uuids_16bit": ad_struct.get("service_uuids_16bit_complete", "") + ad_struct.get("service_uuids_16bit_incomplete", ""),
                    "service_uuids_128bit": ad_struct.get("service_uuids_128bit_complete", "") + ad_struct.get("service_uuids_128bit_incomplete", ""),
                    "raw_hex": raw_hex,
                    "ad_structure": ad_struct,
                }
                
                for uuid, data_hex in service_data.items():
                    parsed = parse_service_data_by_uuid(uuid, data_hex)
                    if parsed:
                        adv_info["service_data_parsed"][uuid] = parsed
                
                enrich_vendor(adv_info)
                
                protocol, details = identify_protocol(adv_info)
                adv_info["protocol"] = protocol
                adv_info["protocol_details"] = details
                adv_info["distance"] = calc_distance(rssi, advertisement_data.tx_power)
                
                mac_lower = device.address.lower()
                if mac_lower not in self.device_frequency:
                    self.device_frequency[mac_lower] = 0
                self.device_frequency[mac_lower] += 1
                adv_info["frequency"] = self.device_frequency[mac_lower]
                
                try:
                    self.raw_queue.put_nowait(adv_info)
                    self.packet_count += 1
                except queue.Full:
                    self.dropped_packets += 1
            except Exception as e:
                print(f"扫描回调处理失败: {e}")
                traceback.print_exc()
        
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
                traceback.print_exc()
                try:
                    await scanner.stop()
                except Exception as stop_e:
                    print(f"停止扫描器时发生错误: {stop_e}")
                await asyncio.sleep(5)
    
    def _get_appearance_desc(self, appearance):
        if appearance is None:
            return "N/A"
        try:
            app = int(appearance)
            category = app >> 6
            appearance_map = {
                0: "Unknown",
                1: "Generic Phone",
                2: "Generic Computer",
                3: "Generic Watch",
                4: "Generic Clock",
                5: "Generic Display",
                6: "Generic Remote Control",
                7: "Generic Eye Glasses",
                8: "Generic Tag",
                9: "Generic Keyring",
                10: "Generic Media Player",
                11: "Generic Barcode Scanner",
                12: "Generic Thermometer",
                13: "Generic Heart Rate Sensor",
                14: "Generic Blood Pressure",
                15: "Generic Human Interface Device",
                16: "Generic Keyboard",
                17: "Generic Mouse",
                18: "Generic Joystick",
                19: "Generic Gamepad",
                20: "Generic Digitizer Tablet",
                21: "Generic Card Reader",
                22: "Generic Digital Pen",
                23: "Generic Barcode Scanner",
                24: "Generic Health Thermometer",
                25: "Generic Weight Scale",
                26: "Generic Outdoor Sports Activity",
                32: "Heart Rate Sensor",
                33: "Heart Rate Belt",
                64: "Blood Pressure Monitor",
                65: "Blood Pressure Arm",
                66: "Blood Pressure Wrist",
                96: "Human Interface Device",
                97: "Keyboard",
                98: "Mouse",
                99: "Joystick",
                100: "Gamepad",
                101: "Digitizer Tablet",
                102: "Card Reader",
                103: "Digital Pen",
                104: "Barcode Scanner",
                128: "Glucose Meter",
                160: "Thermometer",
                161: "Ear Thermometer",
                162: "Forehead Thermometer",
                192: "Weight Scale",
                224: "Personal Fitness Equipment",
                225: "Running Walking Sensor",
                226: "Cycling Sensor",
                227: "Cycling Speed Sensor",
                228: "Cycling Cadence Sensor",
                229: "Cycling Power Sensor",
                230: "Cycling Speed and Cadence Sensor",
                256: "Generic Glucose Meter",
            }
            return appearance_map.get(category, f"Category {category}")
        except:
            return f"0x{appearance:04X}"
    
    def _run_scan(self, rssi_min, rssi_max, scan_mode):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._async_scan(loop, rssi_min, rssi_max, scan_mode))
        except Exception as e:
            print(f"扫描线程异常: {e}")
            traceback.print_exc()
            self.root.after(0, lambda: messagebox.showerror("扫描错误", str(e)))
        finally:
            self.root.after(0, self._scan_finished)
    
    def _scan_finished(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
        def wait_writer_done():
            try:
                if self.writer_thread and self.writer_thread.is_alive():
                    self.writer_thread.join(timeout=0.1)
                    if self.writer_thread.is_alive():
                        self.root.after(100, wait_writer_done)
                        return
            except Exception as e:
                print(f"等待写入线程失败: {e}")
            self.status_label.config(text=f"扫描完成 - 共 {self.packet_count} 包, 丢弃 {self.dropped_packets} 包", foreground="green")
        
        self.root.after(0, wait_writer_done)
    
    def _file_writer(self, output_path):
        try:
            with open(output_path, 'a', encoding='utf-8') as f:
                while not self.stop_event.is_set() or not self.file_queue.empty():
                    try:
                        data = self.file_queue.get(timeout=1)
                        f.write(json.dumps(data, ensure_ascii=False) + '\n')
                        self.file_queue.task_done()
                    except queue.Empty:
                        continue
        except Exception as e:
            print(f"写入文件失败: {e}")
            traceback.print_exc()
    
    def update_gui(self):
        try:
            while not self.raw_queue.empty():
                adv_info = self.raw_queue.get_nowait()
                self.file_queue.put_nowait(adv_info)
                
                mac = adv_info["mac"]
                existing_row = self.row_data_map.get(mac)
                if existing_row:
                    self.tree.delete(existing_row)
                
                row_id = self.tree.insert("", tk.END, values=(
                    adv_info["timestamp"],
                    adv_info["mac"],
                    adv_info["mac_type"],
                    adv_info["vendor"],
                    adv_info["protocol"],
                    adv_info["protocol_details"],
                    adv_info["name"],
                    adv_info["rssi"],
                    adv_info["distance"],
                    adv_info["frequency"],
                ))
                self.row_data_map[mac] = row_id
                
                if len(self.row_data_map) > 3000:
                    for row in list(self.row_data_map.values())[:1500]:
                        try:
                            self.tree.delete(row)
                        except:
                            pass
                    self.row_data_map = {k: v for k, v in list(self.row_data_map.items())[1500:]}
            
            self.status_label.config(text=f"扫描中 - 已捕获 {self.packet_count} 包 (丢弃 {self.dropped_packets})")
        except Exception as e:
            print(f"更新 GUI 失败: {e}")
            traceback.print_exc()
        
        if self.running:
            self.root.after(100, self.update_gui)
    
    def on_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item["values"]
            if len(values) >= 2:
                mac = values[1]
                self.show_device_details(mac)
    
    def show_device_details(self, mac):
        self.detail_text.delete(1.0, tk.END)
        
        all_data = []
        try:
            with open(self.output_file.get(), 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            if data.get("mac") == mac:
                                all_data.append(data)
                        except:
                            continue
        except Exception as e:
            print(f"读取文件失败: {e}")
        
        if not all_data:
            self.detail_text.insert(tk.END, f"未找到设备 {mac} 的详细数据")
            return
        
        latest = all_data[-1]
        
        details = []
        details.append("=" * 60)
        details.append(f"设备详情 - {mac}")
        details.append("=" * 60)
        details.append(f"\n【基本信息】")
        details.append(f"  时间: {latest.get('timestamp', 'N/A')}")
        details.append(f"  Unix时间戳: {latest.get('timestamp_unix', 'N/A'):.6f}")
        details.append(f"  设备名称: {latest.get('name', 'N/A')}")
        details.append(f"  短名称: {latest.get('name_short', 'N/A')}")
        details.append(f"  完整名称: {latest.get('name_complete', 'N/A')}")
        details.append(f"  MAC类型: {latest.get('mac_type', 'N/A')}")
        details.append(f"  地址类型: {latest.get('address_type', 'N/A')}")
        details.append(f"  可连接: {latest.get('is_connectable', 'N/A')}")
        details.append(f"  外观: {latest.get('appearance_desc', 'N/A')}")
        details.append(f"  广播间隔: {latest.get('advertising_interval', 'N/A')}")
        details.append(f"  连接间隔范围: {latest.get('conn_interval_range', 'N/A')}")
        
        details.append(f"\n【信号信息】")
        details.append(f"  当前 RSSI: {latest.get('rssi', 'N/A')} dBm")
        details.append(f"  RSSI 平均值: {latest.get('rssi_avg', 'N/A')} dBm")
        details.append(f"  RSSI 最小值: {latest.get('rssi_min', 'N/A')} dBm")
        details.append(f"  RSSI 最大值: {latest.get('rssi_max', 'N/A')} dBm")
        details.append(f"  RSSI 样本数: {latest.get('rssi_samples', 'N/A')}")
        details.append(f"  Tx功率: {latest.get('tx_power', 'N/A')} dBm")
        details.append(f"  估算距离: {latest.get('distance', 'N/A')}")
        details.append(f"  出现频次: {latest.get('frequency', 'N/A')}")

        details.append(f"\n【协议信息】")
        details.append(f"  协议类型: {latest.get('protocol', 'N/A')}")
        details.append(f"  协议详情: {latest.get('protocol_details', 'N/A')}")
        details.append(f"  厂商: {latest.get('vendor', 'N/A')}")

        flags = latest.get('flags', 'N/A')
        if flags != 'N/A':
            details.append(f"\n【广播标志】")
            details.append(f"  {flags}")

        class_of_device = latest.get('class_of_device', 'N/A')
        if class_of_device != 'N/A':
            details.append(f"\n【设备类别 (Class of Device)】")
            details.append(f"  {class_of_device}")

        le_role = latest.get('le_role', 'N/A')
        if le_role != 'N/A':
            details.append(f"\n【LE 角色】")
            details.append(f"  {le_role}")

        le_features = latest.get('le_supported_features', 'N/A')
        if le_features != 'N/A':
            details.append(f"\n【LE 支持特性】")
            details.append(f"  {le_features}")

        device_id = latest.get('device_id', 'N/A')
        if device_id != 'N/A':
            details.append(f"\n【设备 ID】")
            details.append(f"  {device_id}")

        public_target = latest.get('public_target_address', 'N/A')
        if public_target != 'N/A':
            details.append(f"\n【公共目标地址】")
            details.append(f"  {public_target}")

        random_target = latest.get('random_target_address', 'N/A')
        if random_target != 'N/A':
            details.append(f"\n【随机目标地址】")
            details.append(f"  {random_target}")

        uri = latest.get('uri', 'N/A')
        if uri != 'N/A':
            details.append(f"\n【URI】")
            details.append(f"  {uri}")

        indoor_pos = latest.get('indoor_positioning', 'N/A')
        if indoor_pos != 'N/A':
            details.append(f"\n【室内定位】")
            details.append(f"  {indoor_pos}")

        channel_map = latest.get('channel_map_update', 'N/A')
        if channel_map != 'N/A':
            details.append(f"\n【信道映射更新】")
            details.append(f"  {channel_map}")

        mfg_data = latest.get('manufacturer_data', {})
        if mfg_data:
            details.append(f"\n【厂商自定义数据】")
            for cid, data in mfg_data.items():
                details.append(f"  Company ID: 0x{int(cid):04X}")
                details.append(f"  Data (Hex): {data}")

        service_uuids = latest.get('service_uuids', [])
        if service_uuids:
            details.append(f"\n【服务UUID】")
            for uuid in service_uuids[:10]:
                uuid_str = str(uuid).lower()
                svc_name = BLE_STANDARD_SERVICES.get(uuid_str, "未知服务")
                details.append(f"  {uuid} ({svc_name})")

        service_data = latest.get('service_data', {})
        if service_data:
            details.append(f"\n【服务数据】")
            for uuid, data in service_data.items():
                details.append(f"  {uuid}: {data}")

        service_data_parsed = latest.get('service_data_parsed', {})
        if service_data_parsed:
            details.append(f"\n【服务数据深度解析】")
            for uuid, parsed in service_data_parsed.items():
                details.append(f"  UUID: {uuid}")
                for key, value in parsed.items():
                    details.append(f"    - {key}: {value}")

        security_manager_flags = latest.get('security_manager_flags', 'N/A')
        if security_manager_flags != 'N/A' and security_manager_flags != 'N/A':
            details.append(f"\n【安全管理器标志】")
            details.append(f"  {security_manager_flags}")

        simple_pairing_hash = latest.get('simple_pairing_hash', 'N/A')
        if simple_pairing_hash != 'N/A':
            details.append(f"\n【Simple Pairing Hash】")
            details.append(f"  {simple_pairing_hash}")

        le_address = latest.get('le_address', 'N/A')
        if le_address != 'N/A':
            details.append(f"\n【LE 蓝牙地址】")
            details.append(f"  {le_address}")

        solicited_uuids = latest.get('solicited_uuids_16bit', '')
        if solicited_uuids:
            details.append(f"\n【请求服务 UUID】")
            details.append(f"  16-bit: {solicited_uuids}")

        raw_hex = latest.get('raw_hex', '')
        if raw_hex:
            details.append(f"\n【原始数据】")
            details.append(f"  Raw Hex: {raw_hex}")

        ad_struct = latest.get('ad_structure', {})
        if ad_struct:
            details.append(f"\n【AD结构完整解析】")
            for key, value in ad_struct.items():
                details.append(f"  {key}: {value}")

        self.detail_text.insert(tk.END, '\n'.join(details))
    
    def save_current_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                for item in self.tree.get_children():
                    values = self.tree.item(item)['values']
                    if len(values) >= 10:
                        data = {
                            "timestamp": values[0],
                            "mac": values[1],
                            "mac_type": values[2],
                            "vendor": values[3],
                            "protocol": values[4],
                            "protocol_details": values[5],
                            "name": values[6],
                            "rssi": values[7],
                            "distance": values[8],
                            "frequency": values[9],
                        }
                        f.write(json.dumps(data, ensure_ascii=False) + '\n')
            messagebox.showinfo("保存成功", f"已保存 {len(self.tree.get_children())} 条记录")
    
    def _build_ad_structure_hex(self, data):
        ad_parts = []
        
        flags = data.get("flags", "")
        if flags != "N/A":
            flag_val = 0
            if "LE General Discoverable Mode" in flags:
                flag_val |= 0x02
            if "BR/EDR Not Supported" in flags:
                flag_val |= 0x04
            if "Simultaneous LE and BR/EDR" in flags:
                flag_val |= 0x08
            if isinstance(flags, str) and flags.startswith("0x"):
                flag_val = int(flags, 16)
            if flag_val > 0:
                ad_parts.append(f"0201{flag_val:02X}")
        
        name = data.get("name", "") or data.get("name_complete", "") or data.get("name_short", "")
        if name and name != "N/A":
            name_bytes = name.encode('utf-8')
            name_len = len(name_bytes) + 1
            if name_len <= 255:
                name_hex = name_bytes.hex()
                ad_parts.append(f"{name_len:02X}09{name_hex}")
        
        tx_power = data.get("tx_power")
        if tx_power is not None and tx_power != "N/A":
            if isinstance(tx_power, int):
                tx_val = tx_power & 0xFF
                ad_parts.append(f"020A{tx_val:02X}")
        
        appearance = data.get("appearance")
        if appearance is not None and appearance != "N/A" and appearance != 0:
            app_bytes = appearance.to_bytes(2, 'little')
            ad_parts.append(f"031A{app_bytes.hex()}")
        
        mfg_data = data.get("manufacturer_data", {})
        for cid, mfg_hex in mfg_data.items():
            try:
                company_id = int(cid)
                cid_bytes = company_id.to_bytes(2, 'little')
                cid_hex = cid_bytes.hex()
                ad_len = 2 + len(mfg_hex) // 2 + 1
                if ad_len <= 255:
                    ad_parts.append(f"{ad_len:02X}FF{cid_hex}{mfg_hex}")
            except:
                pass
        
        service_uuids = data.get("service_uuids", [])
        if service_uuids:
            uuid_hex = ""
            for uuid in service_uuids:
                uuid_str = str(uuid).lower()
                if len(uuid_str) == 8:
                    uuid_hex += uuid_str[-4:] + uuid_str[:4]
                elif len(uuid_str) == 36:
                    short_uuid = uuid_str[4:8]
                    uuid_hex += short_uuid[-2:] + short_uuid[:2]
            
            if uuid_hex:
                ad_len = len(uuid_hex) // 2 + 1
                if ad_len <= 255:
                    ad_parts.append(f"{ad_len:02X}03{uuid_hex}")
        
        service_data = data.get("service_data", {})
        for uuid, svc_hex in service_data.items():
            try:
                uuid_str = str(uuid).lower()
                short_uuid = ""
                if len(uuid_str) == 8:
                    short_uuid = uuid_str[-4:] + uuid_str[:4]
                elif len(uuid_str) == 36:
                    short_uuid = uuid_str[4:8]
                    short_uuid = short_uuid[-2:] + short_uuid[:2]
                
                if short_uuid and svc_hex:
                    ad_len = 2 + len(svc_hex) // 2 + 1
                    if ad_len <= 255:
                        ad_parts.append(f"{ad_len:02X}17{short_uuid}{svc_hex}")
            except:
                pass
        
        return "".join(ad_parts)
    
    def export_broadcast_frames(self):
        output_file_path = self.output_file.get()
        if not os.path.exists(output_file_path):
            messagebox.showerror("错误", "输出文件不存在，请先进行扫描")
            return
        
        formats = [
            ("JSON格式 (.json)", "json"),
            ("C数组格式 (.h)", "c"),
            ("混合格式 (.txt)", "txt"),
        ]
        
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=formats)
        if not file_path:
            return
        
        ext = file_path.split('.')[-1].lower()
        
        devices = {}
        try:
            with open(output_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            mac = data.get("mac", "").lower()
                            if mac and mac not in devices:
                                raw_data = data.get("raw_hex", "")
                                name = data.get("name", "") or data.get("name_complete", "") or data.get("name_short", "")
                                if not name or name == "N/A":
                                    name = f"Device_{mac[:8]}"
                                
                                if not raw_data:
                                    raw_data = self._build_ad_structure_hex(data)
                                
                                devices[mac] = {
                                    "name": name,
                                    "mac": data.get("mac", ""),
                                    "raw_data": raw_data,
                                    "tx_power": data.get("tx_power"),
                                    "flags": data.get("flags", "N/A"),
                                    "is_connectable": data.get("is_connectable", False),
                                    "appearance": data.get("appearance"),
                                    "manufacturer_data": data.get("manufacturer_data", {}),
                                    "service_uuids": data.get("service_uuids", []),
                                    "service_data": data.get("service_data", {}),
                                    "protocol": data.get("protocol", "N/A"),
                                    "protocol_details": data.get("protocol_details", "N/A"),
                                    "vendor": data.get("vendor", "N/A"),
                                }
                        except:
                            continue
        except Exception as e:
            messagebox.showerror("错误", f"读取文件失败: {e}")
            return
        
        if not devices:
            messagebox.showinfo("提示", "未找到设备数据")
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if ext == 'json':
                    export_data = []
                    for mac, info in devices.items():
                        bytes_list = [info["raw_data"][i:i+2] for i in range(0, len(info["raw_data"]), 2)] if info["raw_data"] else []
                        export_data.append({
                            "device_name": info["name"],
                            "mac_address": info["mac"],
                            "mac_address_lower": mac,
                            "raw_hex": info["raw_data"],
                            "raw_length": len(bytes_list),
                            "raw_bytes": [f"0x{b}" for b in bytes_list],
                            "tx_power": info["tx_power"],
                            "flags": info["flags"],
                            "is_connectable": info["is_connectable"],
                            "appearance": info["appearance"],
                            "manufacturer_data": info["manufacturer_data"],
                            "service_uuids": info["service_uuids"],
                            "service_data": info["service_data"],
                            "protocol": info["protocol"],
                            "protocol_details": info["protocol_details"],
                            "vendor": info["vendor"],
                        })
                    f.write(json.dumps(export_data, ensure_ascii=False, indent=2))
                
                elif ext == 'c':
                    f.write("// BLE Broadcast Frames for ESP32C3\n")
                    f.write("// Generated by BLE Scanner\n")
                    f.write(f"// Devices: {len(devices)}\n")
                    f.write(f"// Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("//\n")
                    f.write("#ifndef BLE_BROADCAST_FRAMES_H\n")
                    f.write("#define BLE_BROADCAST_FRAMES_H\n")
                    f.write("//\n")
                    f.write("#include \"esp_bt_defs.h\"\n")
                    f.write("#include \"esp_gap_ble_api.h\"\n")
                    f.write("//\n")
                    f.write("typedef struct {\n")
                    f.write("    const char* device_name;\n")
                    f.write("    const char* mac_address;\n")
                    f.write("    const uint8_t* raw_data;\n")
                    f.write("    const size_t raw_length;\n")
                    f.write("    int8_t tx_power;\n")
                    f.write("    uint8_t flags;\n")
                    f.write("    bool is_connectable;\n")
                    f.write("    uint16_t appearance;\n")
                    f.write("    const char* protocol;\n")
                    f.write("    const char* vendor;\n")
                    f.write("} ble_broadcast_frame_t;\n")
                    f.write("//\n")
                    
                    idx = 0
                    for mac, info in devices.items():
                        bytes_list = [info["raw_data"][i:i+2] for i in range(0, len(info["raw_data"]), 2)] if info["raw_data"] else []
                        bytes_hex = [f"0x{b}" for b in bytes_list]
                        bytes_str = ", ".join(bytes_hex) if bytes_hex else ""
                        clean_name = info["name"].replace('"', '\\"').replace("'", "\\'")
                        
                        f.write(f"// Device {idx+1}: {clean_name}\n")
                        f.write(f"// MAC: {info['mac']}\n")
                        f.write(f"// Protocol: {info['protocol']} - {info['protocol_details']}\n")
                        f.write(f"// Vendor: {info['vendor']}\n")
                        f.write(f"// TX Power: {info['tx_power']} dBm\n")
                        f.write(f"// Connectable: {'Yes' if info['is_connectable'] else 'No'}\n")
                        if bytes_str:
                            f.write(f"static const uint8_t broadcast_data_{idx}[] = {{{bytes_str}}};\n")
                        else:
                            f.write(f"static const uint8_t broadcast_data_{idx}[] = {{0x02, 0x01, 0x06}};\n")
                        f.write("//\n")
                        idx += 1
                    
                    f.write("// Device list\n")
                    f.write(f"#define BLE_BROADCAST_FRAME_COUNT {len(devices)}\n")
                    f.write("static const ble_broadcast_frame_t ble_broadcast_frames[] = {\n")
                    idx = 0
                    for mac, info in devices.items():
                        clean_name = info["name"].replace('"', '\\"').replace("'", "\\'")
                        flags_val = 0x06
                        if isinstance(info["flags"], str) and info["flags"].startswith("0x"):
                            flags_val = int(info["flags"], 16)
                        elif isinstance(info["flags"], str):
                            if "LE General Discoverable Mode" in info["flags"]:
                                flags_val |= 0x02
                            if "BR/EDR Not Supported" in info["flags"]:
                                flags_val |= 0x04
                        
                        f.write(f"    {{\n")
                        f.write(f"        .device_name = \"{clean_name}\",\n")
                        f.write(f"        .mac_address = \"{info['mac']}\",\n")
                        f.write(f"        .raw_data = broadcast_data_{idx},\n")
                        f.write(f"        .raw_length = sizeof(broadcast_data_{idx}),\n")
                        f.write(f"        .tx_power = {info['tx_power'] if info['tx_power'] is not None else -1},\n")
                        f.write(f"        .flags = 0x{flags_val:02X},\n")
                        f.write(f"        .is_connectable = {str(info['is_connectable']).lower()},\n")
                        f.write(f"        .appearance = {info['appearance'] if info['appearance'] else 0},\n")
                        f.write(f"        .protocol = \"{info['protocol']}\",\n")
                        f.write(f"        .vendor = \"{info['vendor']}\",\n")
                        f.write(f"    }},\n")
                        idx += 1
                    f.write("};\n")
                    f.write("//\n")
                    f.write("// ESP32C3 Broadcast API Example:\n")
                    f.write("//\n")
                    f.write("// esp_ble_gap_advertise_data_set(broadcast_data_X, sizeof(broadcast_data_X), NULL, 0);\n")
                    f.write("// esp_ble_gap_start_advertising(&adv_params);\n")
                    f.write("//\n")
                    f.write("#endif\n")
                
                elif ext == 'txt':
                    f.write("=" * 70 + "\n")
                    f.write("BLE Broadcast Frame Export\n")
                    f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Total Devices: {len(devices)}\n")
                    f.write("=" * 70 + "\n\n")
                    
                    idx = 0
                    for mac, info in devices.items():
                        bytes_list = [info["raw_data"][i:i+2] for i in range(0, len(info["raw_data"]), 2)] if info["raw_data"] else []
                        bytes_hex = [f"0x{b}" for b in bytes_list]
                        
                        f.write(f"--- Device {idx+1} ---\n")
                        f.write(f"Name: {info['name']}\n")
                        f.write(f"MAC: {info['mac']}\n")
                        f.write(f"MAC (lower): {mac}\n")
                        f.write(f"Protocol: {info['protocol']} - {info['protocol_details']}\n")
                        f.write(f"Vendor: {info['vendor']}\n")
                        f.write(f"TX Power: {info['tx_power']} dBm\n")
                        f.write(f"Connectable: {'Yes' if info['is_connectable'] else 'No'}\n")
                        f.write(f"Appearance: {info['appearance']}\n")
                        f.write(f"Flags: {info['flags']}\n")
                        f.write(f"Raw Length: {len(bytes_list)} bytes\n")
                        f.write(f"Raw Hex: {info['raw_data']}\n")
                        if bytes_hex:
                            f.write(f"C Array: uint8_t data[] = {{{', '.join(bytes_hex)}}};\n")
                            f.write(f"Python Bytes: bytes.fromhex('{info['raw_data']}')\n")
                        f.write("\n")
                        
                        if info["manufacturer_data"]:
                            f.write(f"  Manufacturer Data:\n")
                            for cid, mfg_data in info["manufacturer_data"].items():
                                f.write(f"    Company ID: 0x{int(cid):04X}\n")
                                f.write(f"    Data: {mfg_data}\n")
                        
                        if info["service_uuids"]:
                            f.write(f"  Service UUIDs:\n")
                            for uuid in info["service_uuids"]:
                                f.write(f"    {uuid}\n")
                        
                        if info["service_data"]:
                            f.write(f"  Service Data:\n")
                            for uuid, svc_data in info["service_data"].items():
                                f.write(f"    {uuid}: {svc_data}\n")
                        
                        f.write("\n")
                        idx += 1
            
            messagebox.showinfo("导出成功", f"已导出 {len(devices)} 个设备的广播帧数据")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = BLEScannerGUI(root)
    root.mainloop()