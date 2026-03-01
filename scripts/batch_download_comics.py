import sys
import os

import jmcomic
import json
from datetime import datetime
from pathlib import Path

def load_config():
    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "username": "",
            "download_dir": "pictures",
            "output_json": "comics_database.json",
            "progress_file": "download_progress.json",
            "favorite_list_file": "favorite_comics.txt",
            "collection_name": "我的最爱"
        }

CONFIG = load_config()

os.makedirs(CONFIG["download_dir"], exist_ok=True)

option_dict = {
    'download': {
        'dir': CONFIG["download_dir"],
        'image': {
            'suffix': '.jpg'
        }
    },
    'dir_rule': {
        'base_dir': CONFIG["download_dir"],
        'rule': 'Bd_Aid'
    }
}

option = jmcomic.JmOption.construct(option_dict)

with open(CONFIG.get("favorite_list_file", "favorite_comics.txt"), 'r', encoding='utf-8') as f:
    comic_ids = [line.strip() for line in f if line.strip()]

print(f"共找到 {len(comic_ids)} 个漫画ID")

database = {
    "collection_name": CONFIG.get("collection_name", "我的最爱"),
    "user": CONFIG.get("username", ""),
    "total_favorites": len(comic_ids),
    "last_updated": datetime.now().strftime("%Y-%m-%d"),
    "scraped_at": datetime.now().strftime("%Y-%m-%d"),
    "albums": []
}

# 读取或初始化进度文件
def load_progress():
    if os.path.exists(CONFIG["progress_file"]):
        with open(CONFIG["progress_file"], 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# 保存进度文件
def save_progress(progress):
    with open(CONFIG["progress_file"], 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

# 保存数据库文件
def save_database():
    with open(CONFIG["output_json"], 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)

# 统计本地下载进度
def get_local_progress(comic_id):
    """统计本地已下载的图片数量"""
    comic_dir = os.path.join(CONFIG["download_dir"], str(comic_id))
    if not os.path.exists(comic_dir):
        return 0
    
    # 统计图片文件数量
    image_files = []
    for file in os.listdir(comic_dir):
        if file.endswith('.jpg') or file.endswith('.webp') or file.endswith('.png'):
            image_files.append(file)
    
    return len(image_files)

# 统计所有漫画的下载进度
def get_overall_progress():
    """统计 pictures 目录下的漫画下载进度"""
    overall_progress = {
        "total_comics": len(comic_ids),
        "downloaded_comics": 0,
        "in_progress_comics": 0,
        "not_downloaded_comics": 0,
        "total_images": 0,
        "downloaded_images": 0
    }
    
    for comic_id in comic_ids:
        local_count = get_local_progress(comic_id)
        
        # 检查是否已下载
        if local_count > 0:
            overall_progress["in_progress_comics"] += 1
            overall_progress["downloaded_images"] += local_count
        else:
            overall_progress["not_downloaded_comics"] += 1
    
    return overall_progress

# 获取当前时间
current_time = datetime.now().strftime("%Y-%m-%d")

# 加载进度文件
progress = load_progress()

# 读取数据库文件（如果存在）
if os.path.exists(CONFIG["output_json"]):
    with open(CONFIG["output_json"], 'r', encoding='utf-8') as f:
        database = json.load(f)
else:
    # 初始化数据库结构
    database = {
        "collection_name": CONFIG["collection_name"],
        "user": CONFIG["user"],
        "total_favorites": len(comic_ids),
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "scraped_at": datetime.now().strftime("%Y-%m-%d"),
        "albums": []
    }

# 统计初始进度
initial_progress = get_overall_progress()
print(f"\n初始下载进度:")
print(f"总漫画数: {initial_progress['total_comics']}")
print(f"已下载漫画: {initial_progress['downloaded_comics']}")
print(f"下载中漫画: {initial_progress['in_progress_comics']}")
print(f"未下载漫画: {initial_progress['not_downloaded_comics']}")
print(f"已下载图片: {initial_progress['downloaded_images']}")

# 统计数据库中的漫画数量
print(f"\n数据库状态:")
print(f"数据库中漫画数量: {len(database['albums'])}")

# 创建客户端（只创建一次）
client = option.build_jm_client()

# 遍历所有漫画ID
successful_count = 0
failed_count = 0
skipped_count = 0

for rank, comic_id in enumerate(comic_ids, 1):
    # 检查数据库中是否有该漫画信息
    existing_album = None
    for album_info in database["albums"]:
        if album_info["album_id"] == int(comic_id):
            existing_album = album_info
            break
    
    # 检查本地下载进度
    local_downloaded = get_local_progress(comic_id)
    
    # 如果数据库中有该漫画，并且本地图片数量等于数据库中的图片数量，则跳过
    if existing_album and existing_album.get("pages", 0) > 0 and local_downloaded == existing_album["pages"]:
        print(f"\n[{rank}/{len(comic_ids)}] 漫画 {comic_id} 已下载完成，跳过")
        skipped_count += 1
        continue
    
    try:
        print(f"\n[{rank}/{len(comic_ids)}] 正在获取漫画 {comic_id} 的信息...")
        
        # 获取漫画详情
        album = client.get_album_detail(comic_id)
        
        # 构建或更新专辑信息
        if existing_album:
            # 更新现有信息
            existing_album["title"] = album.name
            existing_album["author"] = album.author if album.author else "未知"
            existing_album["pages"] = album.page_count
            existing_album["tags"] = album.tags if album.tags else []
            existing_album["upload_date"] = album.pub_date if album.pub_date else current_time
            existing_album["update_date"] = album.update_date if album.update_date else current_time
            
            if hasattr(album, 'uploader') and album.uploader:
                existing_album["uploader"] = album.uploader
            
            album_info = existing_album
        else:
            # 构建新的专辑信息
            album_info = {
                "rank": rank,
                "album_id": int(album.album_id),
                "title": album.name,
                "title_jp": "",  # 如果需要日文标题，可以进一步解析
                "author": album.author if album.author else "未知",
                "pages": album.page_count,
                "cover_url": f"https://cdn-msp3.18comic.vip/media/albums/{album.album_id}.jpg",
                "album_url": f"https://18comic.vip/album/{album.album_id}",
                "tags": album.tags if album.tags else [],
                "category_tags": [],  # 如果需要分类标签，可以进一步解析
                "upload_date": album.pub_date if album.pub_date else current_time,
                "update_date": album.update_date if album.update_date else current_time
            }
            
            # 如果有上传者信息，添加到专辑信息中
            if hasattr(album, 'uploader') and album.uploader:
                album_info["uploader"] = album.uploader
            
            # 立即将专辑信息保存到数据库
            database["albums"].append(album_info)
        
        save_database()
        
        print(f"  标题: {album.name}")
        print(f"  作者: {album.author}")
        print(f"  页数: {album.page_count}")
        print(f"  标签: {', '.join(album.tags[:5]) if album.tags else '无'}")
        print(f"  本地已下载: {local_downloaded} 张图片")
        
        # 检查是否已经下载完成
        if local_downloaded >= album.page_count and album.page_count > 0:
            print(f"  漫画 {comic_id} 已经下载完成，标记为完成")
            
            # 更新进度为完成
            progress[str(comic_id)] = {
                "status": "completed",
                "start_time": progress.get(str(comic_id), {}).get("start_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "downloaded_images": local_downloaded,
                "total_images": album.page_count,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_progress(progress)
            
            skipped_count += 1
            continue
        
        # 初始化或更新进度
        progress[str(comic_id)] = {
            "status": "downloading",
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "downloaded_images": local_downloaded,
            "total_images": album.page_count,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_progress(progress)
        
        # 下载漫画
        print(f"  正在下载漫画 {comic_id}...")
        print(f"  开始下载，已完成 {local_downloaded}/{album.page_count} 张图片")
        
        try:
            # 创建下载器并下载
            downloader = jmcomic.JmDownloader(option)
            album = downloader.download_album(comic_id)
            
            # 统计实际下载的图片数
            actual_downloaded = get_local_progress(comic_id)
            
            # 下载完成，更新进度
            progress[str(comic_id)] = {
                "status": "completed",
                "start_time": progress[str(comic_id)]["start_time"],
                "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "downloaded_images": actual_downloaded,
                "total_images": album.page_count,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_progress(progress)
            
            # 更新数据库中的总页数
            for album_info in database["albums"]:
                if album_info["album_id"] == int(comic_id):
                    # 根据用户要求更新页数
                    if album.page_count > 0:
                        if actual_downloaded >= album.page_count:
                            # 实际下载数量大于等于网页抓取数量，使用实际下载数量
                            album_info["pages"] = actual_downloaded
                            print(f"  异常情况1: 实际下载数量大于网页抓取数量")
                        else:
                            # 实际下载数量小于网页抓取数量，使用网页抓取数量
                            album_info["pages"] = album.page_count
                            print(f"  下载未完成: 已下载 {actual_downloaded}/{album.page_count} 张图片")
                    else:
                        # 网页抓取数量为0，使用实际下载数量
                        album_info["pages"] = actual_downloaded
                        print(f"  异常情况2: 网页抓取数量为0，使用实际下载数量")
                    break
            save_database()
            
            print(f"  漫画 {comic_id} 下载完成")
            print(f"  共下载 {actual_downloaded} 张图片")
            print(f"  已更新数据库中的总页数为 {album_info['pages']}")
            successful_count += 1
            
        except Exception as e:
            # 下载失败，更新进度
            actual_downloaded = get_local_progress(comic_id)
            progress[str(comic_id)] = {
                "status": "failed",
                "start_time": progress[str(comic_id)]["start_time"],
                "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e),
                "downloaded_images": actual_downloaded,
                "total_images": album.page_count,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_progress(progress)
            
            print(f"  漫画 {comic_id} 下载失败: {e}")
            print(f"  已下载 {actual_downloaded} 张图片，还需下载 {album.page_count - actual_downloaded} 张")
            failed_count += 1
        
    except Exception as e:
        print(f"  获取漫画 {comic_id} 信息失败: {e}")
        # 即使失败，也添加基本信息到数据库
        album_info = {
            "rank": rank,
            "album_id": int(comic_id),
            "title": f"漫画 {comic_id}",
            "title_jp": "",
            "author": "未知",
            "pages": 0,
            "cover_url": f"https://cdn-msp3.18comic.vip/media/albums/{comic_id}.jpg",
            "album_url": f"https://18comic.vip/album/{comic_id}",
            "tags": [],
            "category_tags": [],
            "upload_date": current_time,
            "update_date": current_time,
            "error": str(e)
        }
        database["albums"].append(album_info)
        save_database()
        failed_count += 1

# 最终保存数据库
save_database()

# 统计最终进度
final_progress = get_overall_progress()
print(f"\n最终下载进度:")
print(f"总漫画数: {final_progress['total_comics']}")
print(f"已下载漫画: {final_progress['downloaded_comics']}")
print(f"下载中漫画: {final_progress['in_progress_comics']}")
print(f"未下载漫画: {final_progress['not_downloaded_comics']}")
print(f"已下载图片: {final_progress['downloaded_images']}")
print(f"\n本次任务统计:")
print(f"成功: {successful_count}")
print(f"失败: {failed_count}")
print(f"跳过: {skipped_count}")

print(f"\n数据库已保存到 {CONFIG['output_json']}")
print(f"进度文件: {CONFIG['progress_file']}")
print(f"共处理 {len(database['albums'])} 个漫画")
print(f"下载目录: {CONFIG['download_dir']}")
print("完成！")
