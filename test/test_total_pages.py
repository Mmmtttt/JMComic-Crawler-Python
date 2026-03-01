"""
测试获取网络端图片总数
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import jmcomic
import json

config_file = os.path.join(os.path.dirname(__file__), '..', 'config.json')
with open(config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)

TEST_ALBUM_ID = 542774
TEST_DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'pictures')

os.makedirs(TEST_DOWNLOAD_DIR, exist_ok=True)

option = jmcomic.JmOption.construct({
    'download': {
        'dir': TEST_DOWNLOAD_DIR,
        'image': {'suffix': '.jpg'}
    },
    'dir_rule': {
        'base_dir': TEST_DOWNLOAD_DIR,
        'rule': 'Bd_Aid'
    }
})

client = option.build_jm_client()

if config.get("username") and config.get("password"):
    print("正在登录...")
    client.login(config["username"], config["password"])
    print("登录成功！")

print(f"\n{'='*60}")
print(f"测试获取漫画 {TEST_ALBUM_ID} 的网络端图片总数")
print('='*60)

print("\n1. 获取漫画详情...")
album = client.get_album_detail(TEST_ALBUM_ID)

print(f"   漫画ID: {album.id}")
print(f"   标题: {album.name}")
print(f"   作者: {album.author}")
print(f"   章节数: {len(album.episode_list)}")
print(f"   page_count属性: {album.page_count}")

print("\n2. 检查episode_list结构...")
for i, episode in enumerate(album.episode_list):
    print(f"   章节 {i+1}: {episode}")

print("\n3. 获取章节详情来获取图片总数...")
total_images = 0

for i, episode in enumerate(album.episode_list):
    photo_id = episode[0]
    print(f"   章节 {i+1}: photo_id={photo_id}")
    
    try:
        photo_detail = client.get_photo_detail(photo_id)
        page_count = len(photo_detail.page_arr) if photo_detail.page_arr else 0
        print(f"      图片数: {page_count}")
        total_images += page_count
    except Exception as e:
        print(f"      获取失败: {e}")

print(f"\n   总图片数: {total_images}")

print("\n4. 下载并观察日志输出...")
downloader = jmcomic.JmDownloader(option)
album_downloaded = downloader.download_album(TEST_ALBUM_ID)

print(f"\n   下载完成")
print(f"   has_download_failures: {downloader.has_download_failures}")

print("\n5. 检查下载后的album对象...")
print(f"   album.id: {album_downloaded.id}")
print(f"   album.page_count: {album_downloaded.page_count}")

total_from_downloaded = 0
for i in range(len(album_downloaded)):
    photo = album_downloaded[i]
    if hasattr(photo, 'page_arr') and photo.page_arr:
        total_from_downloaded += len(photo.page_arr)
        print(f"   章节 {i+1}: {len(photo.page_arr)} 张图片")

print(f"   累加图片数: {total_from_downloaded}")

print(f"\n{'='*60}")
print("测试结论:")
print('='*60)
print(f"网络端图片总数获取方式:")
print(f"1. album.page_count: {album.page_count}")
print(f"2. 累加各章节图片数: {total_images}")
print(f"推荐使用: 遍历episode_list获取各章节详情后累加")
