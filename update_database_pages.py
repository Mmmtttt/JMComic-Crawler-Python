import json
import os
import jmcomic
import argparse

# 配置信息
CONFIG = {
    "download_dir": "pictures",
    "database_file": "comics_database.json"
}

# 创建配置选项
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

# 简单更新模式：以本地下载数量为准
def simple_update(database):
    """使用简单逻辑更新数据库"""
    updated_count = 0
    for album_info in database["albums"]:
        comic_id = album_info["album_id"]
        local_count = get_local_progress(comic_id)
        
        # 如果本地有图片且数据库中的页数不准确，则更新
        if local_count > 0 and (album_info["pages"] == 0 or album_info["pages"] != local_count):
            old_pages = album_info["pages"]
            album_info["pages"] = local_count
            updated_count += 1
            print(f"更新漫画 {comic_id}: {old_pages} -> {local_count} 页")
    
    return updated_count

# 精确更新模式：从网页获取信息
def precise_update(database):
    """使用精确逻辑更新数据库"""
    # 创建客户端
    client = option.build_jm_client()
    
    updated_count = 0
    for album_info in database["albums"]:
        comic_id = album_info["album_id"]
        local_count = get_local_progress(comic_id)
        
        # 尝试从网页获取最新的总页数
        web_page_count = 0
        try:
            album = client.get_album_detail(str(comic_id))
            web_page_count = album.page_count
        except Exception as e:
            print(f"获取漫画 {comic_id} 的详情失败: {e}")
            # 如果获取失败，使用数据库中现有的值
            web_page_count = album_info.get("pages", 0)
        
        # 根据用户要求更新页数
        if local_count > 0:
            if web_page_count > 0:
                if local_count >= web_page_count:
                    # 实际下载数量大于等于网页抓取数量，使用实际下载数量
                    new_pages = local_count
                    status = "异常情况1: 实际下载数量大于网页抓取数量"
                else:
                    # 实际下载数量小于网页抓取数量，使用网页抓取数量
                    new_pages = web_page_count
                    status = f"下载未完成: 已下载 {local_count}/{web_page_count} 张图片"
            else:
                # 网页抓取数量为0，使用实际下载数量
                new_pages = local_count
                status = "异常情况2: 网页抓取数量为0，使用实际下载数量"
            
            # 如果页数有变化，更新数据库
            if album_info["pages"] != new_pages:
                old_pages = album_info["pages"]
                album_info["pages"] = new_pages
                updated_count += 1
                print(f"更新漫画 {comic_id}: {old_pages} -> {new_pages} 页")
                print(f"  {status}")
    
    return updated_count

# 解析命令行参数
parser = argparse.ArgumentParser(description="更新数据库中的漫画总页数")
parser.add_argument('--mode', choices=['simple', 'precise'], default='simple',
                    help="更新模式: simple (默认，以本地下载数量为准) 或 precise (从网页获取信息)")
args = parser.parse_args()

# 读取数据库
print("正在读取数据库...")
with open(CONFIG["database_file"], 'r', encoding='utf-8') as f:
    database = json.load(f)

print(f"数据库中共有 {len(database['albums'])} 个漫画")

# 根据选择的模式更新数据库
print(f"\n使用 {args.mode} 模式更新数据库...")
if args.mode == 'simple':
    updated_count = simple_update(database)
else:
    updated_count = precise_update(database)

print(f"\n共更新了 {updated_count} 个漫画的总页数")

# 保存数据库
with open(CONFIG["database_file"], 'w', encoding='utf-8') as f:
    json.dump(database, f, ensure_ascii=False, indent=2)

print(f"数据库已保存到 {CONFIG['database_file']}")

# 统计整体下载进度
total_images = 0
downloaded_comics = 0
for album_info in database["albums"]:
    if album_info["pages"] > 0:
        downloaded_comics += 1
        total_images += album_info["pages"]

print(f"\n整体下载进度:")
print(f"已下载漫画: {downloaded_comics}/{len(database['albums'])}")
print(f"已下载图片: {total_images}")

print("\n完成！")
