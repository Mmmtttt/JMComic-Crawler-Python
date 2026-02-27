import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib', 'src'))

import jmcomic
import json
import argparse
from datetime import datetime

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
            "temp_dir": "temp"
        }

CONFIG = load_config()

def get_album_detail(client, album_id, precise_pages=False):
    try:
        album = client.get_album_detail(album_id)
        
        total_pages = album.page_count
        if precise_pages and total_pages == 0:
            total_pages = 0
            for i in range(len(album)):
                try:
                    photo = album[i]
                    photo_detail = client.get_photo_detail(photo.photo_id)
                    if photo_detail.page_arr:
                        total_pages += len(photo_detail.page_arr)
                except Exception as e:
                    print(f"    获取章节 {i+1} 详情失败: {e}")
        
        album_info = {
            "album_id": album.id,
            "title": album.name,
            "title_jp": getattr(album, 'name_jp', ""),
            "author": album.author[0] if album.author else "default_author",
            "pages": total_pages,
            "cover_url": f"https://cdn-msp3.18comic.vip/media/albums/{album.id}.jpg",
            "album_url": f"https://18comic.vip/album/{album.id}",
            "tags": list(album.tags) if album.tags else [],
            "category_tags": list(album.category_tags) if hasattr(album, 'category_tags') and album.category_tags else [],
            "upload_date": str(getattr(album, 'pub_date', '0')),
            "update_date": str(getattr(album, 'update_date', '0'))
        }
        return album_info
    except Exception as e:
        print(f"获取漫画 {album_id} 详情失败: {e}")
        return None

def search_comics(query, max_pages=None):
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
    
    username = CONFIG.get("username", "")
    password = CONFIG.get("password", "")
    
    if username and password:
        print("正在登录...")
        try:
            client.login(username, password)
            print("登录成功！")
        except Exception as e:
            print(f"登录失败: {e}")
            print("将以游客身份搜索...")
    
    print(f"\n正在搜索: {query}")
    
    all_results = []
    page = 1
    
    while True:
        print(f"正在获取第 {page} 页...")
        try:
            search_page = client.search_site(
                search_query=query,
                page=page,
                order_by=jmcomic.JmMagicConstants.ORDER_BY_LATEST
            )
            
            if not search_page.content:
                print(f"第 {page} 页没有结果，搜索结束")
                break
            
            for album_id, album_info in search_page.content:
                all_results.append({
                    "album_id": album_id,
                    "title": album_info.get('name', ''),
                    "tags": album_info.get('tags', [])
                })
            
            print(f"第 {page} 页: 获取到 {len(search_page.content)} 个结果")
            
            if max_pages and page >= max_pages:
                print(f"已达到最大页数限制 ({max_pages} 页)")
                break
            
            if page >= search_page.page_count:
                print(f"已到达最后一页 ({search_page.page_count} 页)")
                break
            
            page += 1
            
        except Exception as e:
            print(f"获取第 {page} 页失败: {e}")
            break
    
    print(f"\n共搜索到 {len(all_results)} 个漫画")
    return all_results, client

def save_temp_ids(results, temp_file):
    temp_dir = os.path.dirname(temp_file)
    if temp_dir and not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    with open(temp_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(f"{result['album_id']}\n")
    
    print(f"搜索结果ID已保存到: {temp_file}")

def fetch_details(client, results, precise_pages=False):
    print("\n正在获取漫画详细信息...")
    detailed_results = []
    
    for i, result in enumerate(results, 1):
        album_id = result['album_id']
        print(f"[{i}/{len(results)}] 获取漫画 {album_id} 详情...")
        
        detail = get_album_detail(client, album_id, precise_pages)
        if detail:
            detail['rank'] = i
            detailed_results.append(detail)
    
    return detailed_results

def save_search_result(results, query, output_file):
    output_data = {
        "search_query": query,
        "total_results": len(results),
        "search_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "albums": results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n搜索结果已保存到: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="搜索漫画并获取详细信息")
    parser.add_argument('query', type=str, nargs='?', help="搜索关键词")
    parser.add_argument('--max-pages', type=int, default=None, help="最大搜索页数（默认获取所有结果）")
    parser.add_argument('--output', type=str, default='search_result.json', help="输出文件路径")
    parser.add_argument('--temp', type=str, default='temp/search_ids.txt', help="临时ID文件路径")
    parser.add_argument('--skip-detail', action='store_true', help="只保存ID，不获取详细信息")
    parser.add_argument('--precise-pages', action='store_true', help="精确获取页数（较慢）")
    
    args = parser.parse_args()
    
    if not args.query:
        args.query = input("请输入搜索关键词: ").strip()
        if not args.query:
            print("错误：搜索关键词不能为空")
            return
    
    results, client = search_comics(args.query, args.max_pages)
    
    if not results:
        print("未找到任何结果")
        return
    
    save_temp_ids(results, args.temp)
    
    if not args.skip_detail:
        detailed_results = fetch_details(client, results, args.precise_pages)
        save_search_result(detailed_results, args.query, args.output)
    else:
        print("\n跳过获取详细信息")

if __name__ == "__main__":
    main()
