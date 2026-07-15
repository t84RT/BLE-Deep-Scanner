#!/usr/bin/env python3
"""
离线 MAC 厂商 + Manufacturer ID 解析工具 V2
读取 JSON 扫描数据，利用：
1. cid.csv / mam.csv / oui36.csv 匹配公共 MAC 地址前缀
2. Manufacturer ID 映射表识别随机 MAC 设备（如 Apple、Microsoft）
为每条记录添加更精准的 vendor 字段。
"""

import json
import os
import csv
from pathlib import Path

# ========== 1. Manufacturer ID 映射表（根据你的数据直接补充） ==========
# 键为 manufacturer_data 中的 Company ID，值为厂商名称
MANUFACTURER_ID_MAP = {
    "76": "Apple Inc.",          # Apple FindMy, Handoff, Proximity
    "6":  "Microsoft Corporation", # Microsoft Other
    "224": "Google",             # Google Nearby
    "117": "Samsung",            # Samsung
    "1704": "Midea Group",       # 你的美的设备
    "2571": "Unknown",
    "12288": "Unknown",
    "1946": "Unknown",
}

# ========== 2. 前缀归一化函数（与 scanV6.4.py 逻辑一致） ==========
def normalize_prefix(prefix):
    if not prefix: return ""
    cleaned = prefix.strip().replace('-', '').replace(':', '').replace(' ', '').upper()
    if len(cleaned) == 6:           # 24位 -> 3字节
        return f"{cleaned[0:2]}:{cleaned[2:4]}:{cleaned[4:6]}"
    elif len(cleaned) == 7:         # 28位 -> 3.5字节
        return f"{cleaned[0:2]}:{cleaned[2:4]}:{cleaned[4:6]}:{cleaned[6:8]}"
    elif len(cleaned) == 9:         # 36位 -> 4.5字节
        return f"{cleaned[0:2]}:{cleaned[2:4]}:{cleaned[4:6]}:{cleaned[6:8]}:{cleaned[8:10]}"
    return prefix.upper()

# ========== 3. 加载所有 CSV 数据库 ==========
def load_csv_db(csv_dir):
    vendor_map = {}
    files = ['cid.csv', 'mam.csv', 'oui36.csv']
    for fname in files:
        path = Path(csv_dir) / fname
        if not path.exists():
            print(f"⚠️ 警告: 文件 {fname} 不存在，跳过")
            continue
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row or len(row) < 3 or row[0].startswith('Registry'):
                        continue
                    prefix_raw = row[1].strip()
                    vendor = row[2].strip().strip('"')
                    if prefix_raw and vendor:
                        norm = normalize_prefix(prefix_raw)
                        if norm:
                            vendor_map[norm] = vendor
            print(f"✅ 已加载 {path.name}")
        except Exception as e:
            print(f"❌ 加载 {fname} 失败: {e}")
    print(f"📊 OUI 数据库合并完成，共 {len(vendor_map)} 条前缀记录")
    return vendor_map

# ========== 4. 双重识别主函数 ==========
def lookup_vendor(record, vendor_map):
    """双保险查询：先查OUI，查不到则查Manufacturer ID"""
    mac = record.get('mac', '')
    
    # 第一保险：MAC 前缀匹配（用于公共MAC地址）
    if mac and len(mac) >= 8:
        mac_upper = mac.upper()
        if len(mac_upper) >= 14 and mac_upper[:14] in vendor_map:
            return vendor_map[mac_upper[:14]]
        if len(mac_upper) >= 11 and mac_upper[:11] in vendor_map:
            return vendor_map[mac_upper[:11]]
        if len(mac_upper) >= 8 and mac_upper[:8] in vendor_map:
            return vendor_map[mac_upper[:8]]
    
    # 第二保险：Manufacturer ID 匹配（用于随机MAC的苹果/微软等设备）
    mfg_data = record.get('manufacturer_data', {})
    if mfg_data:
        # 取出第一个 key 进行匹配（大多数广播包只包含一个厂商ID）
        mfg_id = next(iter(mfg_data.keys()))
        if mfg_id in MANUFACTURER_ID_MAP:
            return MANUFACTURER_ID_MAP[mfg_id]
    
    return "未知厂商"

# ========== 5. 主处理函数 ==========
def process_json(input_json, csv_dir, output_json):
    print("正在加载 OUI 离线数据库...")
    vendor_map = load_csv_db(csv_dir)

    print(f"正在读取 {input_json} ...")
    with open(input_json, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    records = []
    for line in lines:
        line = line.strip()
        if not line: continue
        try:
            record = json.loads(line)
            record['vendor'] = lookup_vendor(record, vendor_map)
            records.append(record)
        except json.JSONDecodeError:
            print(f"⚠️ 跳过无效 JSON 行: {line[:50]}...")
            continue

    print(f"共处理 {len(records)} 条记录，正在写入 {output_json} ...")
    with open(output_json, 'w', encoding='utf-8') as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    print("✅ 完成！")

if __name__ == '__main__':
    # 一键运行：修改成你实际的文件路径
    INPUT_FILE = "ble_all_packets.json"          # 你的 JSON 文件名
    CSV_DIR = "."                                # 你的 CSV 文件夹路径（"."表示当前目录）
    OUTPUT_FILE = "enriched.json"                # 输出的文件名

    process_json(INPUT_FILE, CSV_DIR, OUTPUT_FILE)
    print("按任意键退出...")
    input()