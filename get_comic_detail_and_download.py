import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib', 'src'))

import jmcomic
import json
from datetime import datetime

def load_config():
    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "download_dir": "pictures",
            "output_json": "comics_database.json"
        }

CONFIG = load_config()

def load_database():
    db_file = CONFIG.get("output_json", "comics_database.json")
    if os.path.exists(db_file):
        with open(db_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "collection_name": "单独下载",
            "user": "",
            "total_favorites": 0,
            "last_updated": "",
            "albums": []
        }

def save_database(database):
    db_file = CONFIG.get("output_json", "comics_database.json")
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)

def get_local_progress(comic_id):
    comic_dir = os.path.join(CONFIG.get("download_dir", "pictures"), str(comic_id))
    if not os.path.exists(comic_dir):
        return 0
    image_files = []
    for file in os.listdir(comic_dir):
        if file.endswith('.jpg') or file.endswith('.webp') or file.endswith('.png'):
            image_files.append(file)
    return len(image_files)

comic_id = 542774

option = jmcomic.JmOption.construct({
    'download': {
        'dir': CONFIG.get("download_dir", "pictures"),
        'image': {
            'suffix': '.jpg'
        }
    },
    'dir_rule': {
        'base_dir': CONFIG.get("download_dir", "pictures"),
        'rule': 'Bd_Aid'
    }
})

downloader = jmcomic.JmDownloader(option)
album = downloader.download_album(comic_id)

print("漫画详情信息:")
print(f"ID: {album.id}")
print(f"标题: {album.name}")
print(f"作者: {album.author}")
print(f"章节数: {len(album)}")
print(f"总页数: {album.page_count}")
print(f"关键词: {album.tags}")

print("\n章节信息:")
for i, photo in enumerate(album):
    print(f"章节 {i+1}: {photo.name} (ID: {photo.photo_id}, 图片数: {len(photo)})")

if not downloader.has_download_failures:
    print("\n下载成功！")
    total_images = sum(len(photo) for photo in album)
    print(f"所有图片已下载完成，共 {total_images} 张图片")
else:
    print("\n部分下载失败！")
    if downloader.download_failed_photo:
        print(f"失败的章节: {len(downloader.download_failed_photo)}")
    if downloader.download_failed_image:
        print(f"失败的图片: {len(downloader.download_failed_image)}")

database = load_database()

existing_index = None
for i, a in enumerate(database["albums"]):
    if a["album_id"] == int(album.id):
        existing_index = i
        break

actual_pages = get_local_progress(comic_id)

album_info = {
    "rank": len(database["albums"]) + 1 if existing_index is None else database["albums"][existing_index]["rank"],
    "album_id": int(album.id),
    "title": album.name,
    "title_jp": "",
    "author": album.author if album.author else "未知",
    "pages": actual_pages,
    "cover_url": f"https://cdn-msp3.18comic.vip/media/albums/{album.id}.jpg",
    "album_url": f"https://18comic.vip/album/{album.id}",
    "tags": list(album.tags) if album.tags else [],
    "category_tags": list(album.category_tags) if hasattr(album, 'category_tags') and album.category_tags else [],
    "upload_date": str(getattr(album, 'pub_date', '0')),
    "update_date": str(getattr(album, 'update_date', '0'))
}

if existing_index is not None:
    database["albums"][existing_index] = album_info
    print(f"\n数据库中已存在该漫画，已更新信息")
else:
    database["albums"].append(album_info)
    database["total_favorites"] = len(database["albums"])
    print(f"\n已添加到数据库")

database["last_updated"] = datetime.now().strftime("%Y-%m-%d")
save_database(database)

print(f"数据库已保存，当前共 {len(database['albums'])} 个漫画")
