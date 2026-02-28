"""
测试download_album的进度回调功能
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from jmcomic_api import download_album, get_client
import json

config_file = os.path.join(os.path.dirname(__file__), '..', 'config.json')
with open(config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)

TEST_ALBUM_ID = 542774
TEST_DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'pictures')

os.makedirs(TEST_DOWNLOAD_DIR, exist_ok=True)

print(f"\n{'='*60}")
print(f"测试 download_album 进度回调功能")
print('='*60)

progress_records = []

def my_progress_callback(current, total, image_filename, status):
    progress_records.append({
        "current": current,
        "total": total,
        "image_filename": image_filename,
        "status": status
    })
    print(f"  进度: [{current}/{total}] {image_filename}")

print("\n1. 使用进度回调下载...")
client = get_client()
detail, success = download_album(
    TEST_ALBUM_ID, 
    download_dir=TEST_DOWNLOAD_DIR, 
    client=client,
    show_progress=False,
    progress_callback=my_progress_callback
)

print(f"\n2. 检查返回结果...")
print(f"   下载成功: {success}")
print(f"   本地图片数: {detail.get('local_pages', 0)}")
print(f"   网络端图片总数: {detail.get('total_pages', 0)}")

print(f"\n3. 进度回调记录...")
print(f"   总回调次数: {len(progress_records)}")
if progress_records:
    print(f"   第一条: {progress_records[0]}")
    print(f"   最后一条: {progress_records[-1]}")

print(f"\n{'='*60}")
print("测试结论:")
print('='*60)
if len(progress_records) > 0:
    print("✅ 进度回调功能正常")
    print(f"   回调次数: {len(progress_records)}")
    print(f"   每条记录包含: current(当前页), total(总页数), image_filename(文件名), status(状态)")
else:
    print("❌ 进度回调未触发")

if detail.get('total_pages', 0) > 0:
    print("✅ 返回值包含 total_pages 字段")
else:
    print("❌ 返回值缺少 total_pages 字段")
