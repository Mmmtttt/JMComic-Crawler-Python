"""
测试手动解密功能
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jmcomic_api import JmImageTool, get_scramble_id, get_client
from PIL import Image

# 测试目录
test_dir = os.path.join(os.path.dirname(__file__), 'pictures', 'test_download')

# 下载漫画1323910（不解密）
print("=== 测试手动解密 ===")

# 获取scramble_id
client = get_client()
scramble_id = get_scramble_id(1323910, client)
print(f"scramble_id: {scramble_id}")

# 选择第一张图片
test_image_path = os.path.join(test_dir, "1323910", "00001.jpg")
output_path = os.path.join(test_dir, "1323910", "00001_decoded.jpg")

# 打开图片
img = Image.open(test_image_path)
print(f"图片尺寸: {img.size}")

# 计算分割数
num = JmImageTool.get_num(scramble_id, 1323910, "00001.jpg")
print(f"分割数: {num}")

# 解密并保存
if num > 0:
    JmImageTool.decode_and_save(num, img, output_path)
    print(f"解密成功，已保存到: {output_path}")
else:
    print("该图片不需要解密")

# 尝试其他分割数
print("\n=== 尝试不同分割数 ===")
for test_num in [2, 4, 6, 8, 10, 12, 14, 16]:
    test_output = os.path.join(test_dir, "1323910", f"00001_decoded_{test_num}.jpg")
    JmImageTool.decode_and_save(test_num, img, test_output)
    print(f"分割数 {test_num} -> {test_output}")
