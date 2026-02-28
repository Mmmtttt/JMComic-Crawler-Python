"""
获取单个漫画详情并下载
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib', 'src'))

from jmcomic_api import (
    load_config, get_client, get_album_detail,
    download_album, load_database, save_database, add_to_database
)
from datetime import datetime

comic_id = 542774

detail, success = download_album(comic_id)

print("漫画详情信息:")
print(f"ID: {detail['album_id']}")
print(f"标题: {detail['title']}")
print(f"作者: {detail['author']}")
print(f"章节数: {detail.get('episode_count', 'N/A')}")
print(f"总页数: {detail['pages']}")
print(f"关键词: {detail['tags']}")

if success:
    print("\n下载成功！")
    print(f"本地图片数: {detail['local_pages']}")
else:
    print("\n部分下载失败！")

add_to_database(detail)
print(f"\n已保存到数据库")
