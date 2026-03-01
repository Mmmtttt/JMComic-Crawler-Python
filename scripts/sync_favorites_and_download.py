import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'src'))

import jmcomic
import json
from datetime import datetime
from pathlib import Path
import argparse

def load_config():
    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "username": "",
            "password": "",
            "download_dir": "pictures",
            "output_json": "comics_database.json",
            "progress_file": "download_progress.json",
            "consecutive_hit_threshold": 10
        }

CONFIG = load_config()

os.makedirs(CONFIG["download_dir"], exist_ok=True)

option = jmcomic.JmOption.construct({
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
})

def load_progress():
    if os.path.exists(CONFIG["progress_file"]):
        with open(CONFIG["progress_file"], 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_progress(progress):
    with open(CONFIG["progress_file"], 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def save_database(database):
    with open(CONFIG["output_json"], 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)

def load_database():
    if os.path.exists(CONFIG["output_json"]):
        with open(CONFIG["output_json"], 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "collection_name": "我的最爱",
        "user": "",
        "total_favorites": 0,
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "scraped_at": datetime.now().strftime("%Y-%m-%d"),
        "albums": []
    }

def build_album_id_dict(database):
    album_dict = {}
    for album in database["albums"]:
        album_dict[album["album_id"]] = album
    return album_dict

def get_local_progress(comic_id):
    comic_dir = os.path.join(CONFIG["download_dir"], str(comic_id))
    if not os.path.exists(comic_dir):
        return 0
    
    image_files = []
    for file in os.listdir(comic_dir):
        if file.endswith('.jpg') or file.endswith('.webp') or file.endswith('.png'):
            image_files.append(file)
    
    return len(image_files)

def fetch_favorite_comics(client, username, password):
    print(f"正在获取用户 {username} 的收藏夹...")
    
    try:
        print("正在登录...")
        client.login(username, password)
        print("登录成功！")
    except Exception as e:
        print(f"登录失败: {e}")
        return []
    
    print("正在获取收藏夹...")
    try:
        favorite_page = client.favorite_folder(page=1, order_by=jmcomic.JmMagicConstants.ORDER_BY_LATEST, folder_id='0')
    except Exception as e:
        print(f"获取收藏夹失败: {e}")
        return []
    
    print(f"共收藏了 {favorite_page.total} 本漫画")
    
    comic_ids = []
    
    for album_id, album_info in favorite_page.content:
        comic_ids.append(album_id)
    
    if favorite_page.page_count > 1:
        for page in range(2, favorite_page.page_count + 1):
            print(f"正在获取第 {page} 页...")
            try:
                page_result = client.favorite_folder(page=page, order_by=jmcomic.JmMagicConstants.ORDER_BY_LATEST, folder_id='0')
                for album_id, album_info in page_result.content:
                    comic_ids.append(album_id)
            except Exception as e:
                print(f"获取第 {page} 页失败: {e}")
                break
    
    print(f"\n共获取到 {len(comic_ids)} 个漫画ID")
    return comic_ids

def download_comic(client, comic_id, database, album_dict, progress, rank, total):
    current_time = datetime.now().strftime("%Y-%m-%d")
    
    existing_album = album_dict.get(int(comic_id))
    
    local_downloaded = get_local_progress(comic_id)
    
    if existing_album and existing_album.get("pages", 0) > 0 and local_downloaded == existing_album["pages"]:
        print(f"\n[{rank}/{total}] 漫画 {comic_id} 已下载完成，跳过")
        return "skipped", None
    
    try:
        print(f"\n[{rank}/{total}] 正在获取漫画 {comic_id} 的信息...")
        
        album = client.get_album_detail(comic_id)
        
        if existing_album:
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
            album_info = {
                "rank": rank,
                "album_id": int(album.album_id),
                "title": album.name,
                "title_jp": "",
                "author": album.author if album.author else "未知",
                "pages": album.page_count,
                "cover_url": f"https://cdn-msp3.18comic.vip/media/albums/{album.album_id}.jpg",
                "album_url": f"https://18comic.vip/album/{album.album_id}",
                "tags": album.tags if album.tags else [],
                "category_tags": [],
                "upload_date": album.pub_date if album.pub_date else current_time,
                "update_date": album.update_date if album.update_date else current_time
            }
            
            if hasattr(album, 'uploader') and album.uploader:
                album_info["uploader"] = album.uploader
            
            database["albums"].append(album_info)
            album_dict[int(comic_id)] = album_info
        
        save_database(database)
        
        print(f"  标题: {album.name}")
        print(f"  作者: {album.author}")
        print(f"  页数: {album.page_count}")
        print(f"  标签: {', '.join(album.tags[:5]) if album.tags else '无'}")
        print(f"  本地已下载: {local_downloaded} 张图片")
        
        if local_downloaded >= album.page_count and album.page_count > 0:
            print(f"  漫画 {comic_id} 已经下载完成，标记为完成")
            
            progress[str(comic_id)] = {
                "status": "completed",
                "start_time": progress.get(str(comic_id), {}).get("start_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "downloaded_images": local_downloaded,
                "total_images": album.page_count,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_progress(progress)
            
            return "skipped", None
        
        progress[str(comic_id)] = {
            "status": "downloading",
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "downloaded_images": local_downloaded,
            "total_images": album.page_count,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_progress(progress)
        
        print(f"  正在下载漫画 {comic_id}...")
        print(f"  开始下载，已完成 {local_downloaded}/{album.page_count} 张图片")
        
        try:
            downloader = jmcomic.JmDownloader(option)
            album = downloader.download_album(comic_id)
            
            actual_downloaded = get_local_progress(comic_id)
            
            progress[str(comic_id)] = {
                "status": "completed",
                "start_time": progress[str(comic_id)]["start_time"],
                "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "downloaded_images": actual_downloaded,
                "total_images": album.page_count,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_progress(progress)
            
            for album_info in database["albums"]:
                if album_info["album_id"] == int(comic_id):
                    if album.page_count > 0:
                        if actual_downloaded >= album.page_count:
                            album_info["pages"] = actual_downloaded
                            print(f"  异常情况1: 实际下载数量大于网页抓取数量")
                        else:
                            album_info["pages"] = album.page_count
                            print(f"  下载未完成: 已下载 {actual_downloaded}/{album.page_count} 张图片")
                    else:
                        album_info["pages"] = actual_downloaded
                        print(f"  异常情况2: 网页抓取数量为0，使用实际下载数量")
                    break
            save_database(database)
            
            print(f"  漫画 {comic_id} 下载完成")
            print(f"  共下载 {actual_downloaded} 张图片")
            print(f"  已更新数据库中的总页数为 {album_info['pages']}")
            return "success", album_info
            
        except Exception as e:
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
            return "failed", None
        
    except Exception as e:
        print(f"  获取漫画 {comic_id} 信息失败: {e}")
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
        album_dict[int(comic_id)] = album_info
        save_database(database)
        return "failed", None

def main():
    parser = argparse.ArgumentParser(description="同步收藏夹并下载新漫画")
    parser.add_argument('--username', type=str, default=None, help="用户名（默认从配置文件读取）")
    parser.add_argument('--password', type=str, default=None, help="密码（默认从配置文件读取）")
    parser.add_argument('--threshold', type=int, default=None, help="连续命中阈值（默认从配置文件读取）")
    args = parser.parse_args()
    
    username = args.username if args.username else CONFIG.get("username", "")
    password = args.password if args.password else CONFIG.get("password", "")
    threshold = args.threshold if args.threshold else CONFIG.get("consecutive_hit_threshold", 10)
    
    if not username or not password:
        print("错误：请提供用户名和密码（通过命令行参数或配置文件）")
        return
    
    print(f"\n{'='*60}")
    print(f"同步收藏夹并下载新漫画")
    print(f"用户: {username}")
    print(f"连续命中阈值: {threshold}")
    print(f"{'='*60}\n")
    
    database = load_database()
    album_dict = build_album_id_dict(database)
    progress = load_progress()
    
    print(f"数据库中已有 {len(album_dict)} 个漫画记录")
    
    client = option.build_jm_client()
    
    comic_ids = fetch_favorite_comics(client, username, password)
    
    if not comic_ids:
        print("未获取到任何漫画ID，退出")
        return
    
    database["user"] = username
    database["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    save_database(database)
    
    print(f"\n开始检查漫画ID...")
    print(f"策略: 连续 {threshold} 个漫画ID在数据库中找到则终止检索\n")
    
    original_count = len(album_dict)
    successful_count = 0
    failed_count = 0
    skipped_count = 0
    consecutive_hit_count = 0
    early_stop = False
    
    for rank, comic_id in enumerate(comic_ids, 1):
        if int(comic_id) in album_dict:
            consecutive_hit_count += 1
            print(f"[{rank}/{len(comic_ids)}] 漫画 {comic_id} 在数据库中找到 (连续命中: {consecutive_hit_count}/{threshold})")
            
            if consecutive_hit_count >= threshold:
                print(f"\n连续 {threshold} 个漫画ID都在数据库中找到，终止检索")
                print(f"跳过剩余 {len(comic_ids) - rank} 个漫画")
                early_stop = True
                break
        else:
            consecutive_hit_count = 0
            
            status, album_info = download_comic(client, comic_id, database, album_dict, progress, rank, len(comic_ids))
            
            if status == "success":
                successful_count += 1
            elif status == "skipped":
                skipped_count += 1
            else:
                failed_count += 1
    
    database["total_favorites"] = original_count + successful_count
    save_database(database)
    
    print(f"\n{'='*60}")
    print(f"任务完成统计:")
    print(f"{'='*60}")
    print(f"总漫画数: {len(comic_ids)}")
    print(f"成功下载: {successful_count}")
    print(f"失败: {failed_count}")
    print(f"跳过: {skipped_count}")
    if early_stop:
        print(f"提前终止: 是 (连续命中 {threshold} 个)")
    else:
        print(f"提前终止: 否")
    print(f"\n数据库已保存到 {CONFIG['output_json']}")
    print(f"进度文件: {CONFIG['progress_file']}")
    print(f"下载目录: {CONFIG['download_dir']}")
    print("完成！")

if __name__ == "__main__":
    main()
