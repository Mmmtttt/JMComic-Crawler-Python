"""
测试download_album的网络端图片总数功能
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from jmcomic_api import download_album, get_total_pages, get_client, load_config
import json

config_file = os.path.join(os.path.dirname(__file__), '..', 'config.json')
with open(config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)

TEST_ALBUM_ID = 542774
TEST_DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'pictures')

os.makedirs(TEST_DOWNLOAD_DIR, exist_ok=True)

print(f"\n{'='*60}")
print(f"测试 download_album 网络端图片总数功能")
print('='*60)

print("\n1. 测试 get_total_pages() 函数...")
client = get_client()
total = get_total_pages(TEST_ALBUM_ID, client)
print(f"   网络端图片总数: {total}")

print("\n2. 测试 download_album() 函数（带进度显示）...")
detail, success = download_album(
    TEST_ALBUM_ID, 
    download_dir=TEST_DOWNLOAD_DIR, 
    client=client,
    show_progress=True
)

print(f"\n3. 检查返回结果...")
print(f"   下载成功: {success}")
print(f"   本地图片数: {detail.get('local_pages', 0)}")
print(f"   网络端图片总数: {detail.get('total_pages', 0)}")
print(f"   漫画标题: {detail.get('title', '')}")

print(f"\n{'='*60}")
print("测试结论:")
print('='*60)
if detail.get('total_pages', 0) > 0:
    print("✅ 网络端图片总数功能正常")
    print(f"   total_pages: {detail.get('total_pages', 0)}")
else:
    print("❌ 网络端图片总数获取失败")

if detail.get('local_pages', 0) == detail.get('total_pages', 0):
    print("✅ 本地图片数与网络端一致")
else:
    print(f"⚠️ 本地图片数({detail.get('local_pages', 0)})与网络端({detail.get('total_pages', 0)})不一致")
