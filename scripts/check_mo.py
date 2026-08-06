#!/usr/bin/env python3
"""检查 .mo 文件是否包含中文翻译"""
import os, sys

os.chdir("/home/frappe/frappe-bench")

sys.path.insert(0, "apps/frappe")

# 方法1: 直接读取 .mo 二进制文件检查是否有中文
mo_path = "sites/assets/locale/zh/LC_MESSAGES/erpnext.mo"
with open(mo_path, "rb") as f:
    raw = f.read()

# 尝试解码为 utf-8
text = raw.decode("utf-8", errors="replace")
has_chinese = any("\u4e00" <= c <= "\u9fff" for c in text)
print(f"MO 文件大小: {len(raw)} bytes")
print(f"包含中文字符: {has_chinese}")

# 方法2: 用 babel 读取
from babel.messages.mofile import read_mo
with open(mo_path, "rb") as f:
    catalog = read_mo(f)

msg_count = len(catalog)
print(f"Babel 读取翻译数: {msg_count}")

# 查找包含中文的翻译
chinese_count = 0
for msg_id, msg in catalog:
    if msg.string and any("\u4e00" <= c <= "\u9fff" for c in str(msg.string)):
        chinese_count += 1
        if chinese_count <= 3:
            print(f"  中文翻译: {msg_id} -> {msg.string}")

print(f"包含中文的翻译总数: {chinese_count}")
print("完成!")
