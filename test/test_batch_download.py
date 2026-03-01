"""
测试批量下载漫画功能（自动解密）- 图片保存到测试目录
"""
import sys
import os
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jmcomic_api import batch_download, get_client

# 创建测试目录
test_dir = os.path.join(os.path.dirname(__file__), 'pictures', 'test_batch')
os.makedirs(test_dir, exist_ok=True)

# 清空测试目录
for item in os.listdir(test_dir):
    item_path = os.path.join(test_dir, item)
    if os.path.isdir(item_path):
        shutil.rmtree(item_path)

print(f"测试目录: {test_dir}")

# 获取客户端
client = get_client()

# 测试批量下载漫画1312953和1295258（自动解密）
print("\n=== 测试批量下载漫画1312953, 1295258（自动解密）===")

album_ids = [1312953, 1295258]

stats = batch_download(
    album_ids,
    skip_existing=False,  # 不跳过，强制重新下载
    client=client,
    decode_images=True,   # 自动解密
    database={"albums": []}
)

print(f"\n下载结果统计:")
print(f"总数: {stats['total']}")
print(f"成功: {stats['success']}")
print(f"跳过: {stats['skipped']}")
print(f"失败: {stats['failed']}")

# 检查下载的图片
for album_id in album_ids:
    comic_dir = os.path.join(test_dir, str(album_id))
    if os.path.exists(comic_dir):
        images = sorted(os.listdir(comic_dir))
        print(f"\n漫画 {album_id}: {len(images)} 张图片")
        print(f"前3张: {images[:3]}")
    else:
        print(f"\n漫画 {album_id}: 目录不存在")

print("\n=== 测试完成 ===")
