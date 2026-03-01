import sys
import os

import jmcomic
import json

def load_config():
    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "username": "",
            "password": "",
            "favorite_list_file": "favorite_comics.txt"
        }

CONFIG = load_config()

username = CONFIG.get("username", "")
password = CONFIG.get("password", "")

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

client = option.build_jm_client()

try:
    print("正在登录...")
    client.login(username, password)
    print("登录成功！")
    
    print("正在获取收藏夹...")
    favorite_page = client.favorite_folder(page=1, order_by=jmcomic.JmMagicConstants.ORDER_BY_LATEST, folder_id='0')
    
    print(f"共收藏了 {favorite_page.total} 本漫画")
    
    comic_ids = []
    
    for album_id, album_info in favorite_page.content:
        comic_ids.append(album_id)
    
    if favorite_page.page_count > 1:
        for page in range(2, favorite_page.page_count + 1):
            print(f"正在获取第 {page} 页...")
            page_result = client.favorite_folder(page=page, order_by=jmcomic.JmMagicConstants.ORDER_BY_LATEST, folder_id='0')
            for album_id, album_info in page_result.content:
                comic_ids.append(album_id)
    
    print("\n收藏的漫画ID列表:")
    for i, comic_id in enumerate(comic_ids, 1):
        print(f"{i}. {comic_id}")
    
    with open(CONFIG.get("favorite_list_file", "favorite_comics.txt"), 'w', encoding='utf-8') as f:
        for comic_id in comic_ids:
            f.write(f"{comic_id}\n")
    
    print("\n漫画ID已保存到 " + CONFIG.get("favorite_list_file", "favorite_comics.txt") + " 文件中")
    
    print(f"\n共获取到 {len(comic_ids)} 个漫画ID")
    
except Exception as e:
    print(f"错误: {e}")
finally:
    if 'client' in locals():
        del client
