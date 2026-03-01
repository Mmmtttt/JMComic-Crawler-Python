"""
重新测试下载和解密功能 - 确保从零开始
"""
import sys
import os
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jmcomic_api import (
    download_album, get_scramble_id, get_client
)

# 创建测试目录
test_dir = os.path.join(os.path.dirname(__file__), 'pictures', 'test_decode')
os.makedirs(test_dir, exist_ok=True)

# 清空测试目录
for item in os.listdir(test_dir):
    item_path = os.path.join(test_dir, item)
    if os.path.isdir(item_path):
        shutil.rmtree(item_path)

print(f"测试目录: {test_dir}")
print("已清空测试目录")

# 获取客户端
client = get_client()

# 测试1: 下载漫画1312953（应该自动解密）
print("\n=== 测试1: 下载漫画1312953（自动解密）===")
detail1, success1 = download_album(1312953, download_dir=test_dir, client=client, decode_images=True)
print(f"下载成功: {success1}")
print(f"本地图片数: {detail1.get('local_pages', 0)}")

# 检查图片
comic_dir1 = os.path.join(test_dir, "1312953")
if os.path.exists(comic_dir1):
    images1 = sorted(os.listdir(comic_dir1))
    print(f"下载的图片数量: {len(images1)}")
    print(f"前3张图片: {images1[:3]}")
else:
    print(f"目录不存在: {comic_dir1}")

# 测试2: 下载漫画1295258（应该自动解密）
print("\n=== 测试2: 下载漫画1295258（自动解密）===")
detail2, success2 = download_album(1295258, download_dir=test_dir, client=client, decode_images=True)
print(f"下载成功: {success2}")
print(f"本地图片数: {detail2.get('local_pages', 0)}")

# 检查图片
comic_dir2 = os.path.join(test_dir, "1295258")
if os.path.exists(comic_dir2):
    images2 = sorted(os.listdir(comic_dir2))
    print(f"下载的图片数量: {len(images2)}")
    print(f"前3张图片: {images2[:3]}")
else:
    print(f"目录不存在: {comic_dir2}")

# 测试3: 下载漫画1323910（不解密）
print("\n=== 测试3: 下载漫画1323910（不解密）===")
detail3, success3 = download_album(1323910, download_dir=test_dir, client=client, decode_images=False)
print(f"下载成功: {success3}")
print(f"本地图片数: {detail3.get('local_pages', 0)}")

# 检查图片
comic_dir3 = os.path.join(test_dir, "1323910")
if os.path.exists(comic_dir3):
    images3 = sorted(os.listdir(comic_dir3))
    print(f"下载的图片数量: {len(images3)}")
    print(f"前3张图片: {images3[:3]}")
else:
    print(f"目录不存在: {comic_dir3}")

print("\n=== 测试完成 ===")
print("\n总结:")
print("- 1312953 和 1295258: decode_images=True，应该已解密")
print("- 1323910: decode_images=False，应该是原始混淆图片")
