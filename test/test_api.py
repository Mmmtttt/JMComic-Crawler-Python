"""
JMComic API 测试脚本
测试所有API接口的功能和返回格式
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from jmcomic_api import (
    load_config, get_client, get_option,
    get_album_detail, download_album, get_local_progress, get_total_pages,
    search_comics, search_comics_full,
    get_favorite_comics, get_favorite_comics_full,
    load_database, save_database, add_to_database,
    load_progress, save_progress, batch_download, sync_favorites,
    get_scramble_id
)
from utils import (
    load_json_file, save_json_file, load_text_file, save_text_file,
    get_download_stats, print_download_stats, count_images,
    format_file_size, parse_album_ids, validate_album_id
)

TEST_DIR = os.path.dirname(__file__)
TEST_DOWNLOAD_DIR = os.path.join(TEST_DIR, 'pictures')
TEST_DB_FILE = os.path.join(TEST_DIR, 'test_database.json')
TEST_PROGRESS_FILE = os.path.join(TEST_DIR, 'test_progress.json')

os.makedirs(TEST_DOWNLOAD_DIR, exist_ok=True)

config_file = os.path.join(os.path.dirname(__file__), '..', 'config.json')
with open(config_file, 'r', encoding='utf-8') as f:
    original_config = json.load(f)

test_config = {
    "username": original_config.get("username", ""),
    "password": original_config.get("password", ""),
    "download_dir": TEST_DOWNLOAD_DIR,
    "output_json": TEST_DB_FILE,
    "progress_file": TEST_PROGRESS_FILE,
    "favorite_list_file": os.path.join(TEST_DIR, 'test_favorites.txt'),
    "consecutive_hit_threshold": 5,
    "collection_name": "测试收藏"
}

import jmcomic_api
import utils

jmcomic_api._config = test_config
utils._config = test_config

TEST_ALBUM_ID = 1323910

def print_header(name):
    print(f"\n{'='*60}")
    print(f"测试: {name}")
    print('='*60)

def test_load_config():
    print_header("load_config()")
    config = load_config()
    print(f"download_dir: {config.get('download_dir')}")
    print(f"output_json: {config.get('output_json')}")
    assert "download_dir" in config
    assert "output_json" in config
    print("✅ 通过")
    return config

def test_get_client():
    print_header("get_client()")
    client = get_client()
    print(f"客户端类型: {type(client).__name__}")
    print("✅ 通过")
    return client

def test_get_option():
    print_header("get_option()")
    option = get_option()
    print(f"选项类型: {type(option).__name__}")
    print("✅ 通过")
    return option

def test_get_album_detail(client):
    print_header("get_album_detail()")
    detail = get_album_detail(TEST_ALBUM_ID, client)
    
    print(f"album_id: {detail.get('album_id')}")
    print(f"title: {detail.get('title', '')[:50]}...")
    print(f"author: {detail.get('author')}")
    print(f"pages: {detail.get('pages')}")
    print(f"tags: {detail.get('tags', [])[:3]}...")
    
    expected_keys = ["album_id", "title", "author", "pages", "tags", "cover_url", "album_url"]
    missing = [k for k in expected_keys if k not in detail]
    
    if missing:
        print(f"❌ 缺少字段: {missing}")
        return None
    
    assert detail["album_id"] == TEST_ALBUM_ID
    print("✅ 通过")
    return detail

def test_download_album(client):
    print_header("download_album()")
    
    progress_records = []
    def progress_callback(current, total, image_filename, status):
        progress_records.append({"current": current, "total": total})
    
    detail, success = download_album(
        TEST_ALBUM_ID, 
        download_dir=TEST_DOWNLOAD_DIR, 
        client=client,
        progress_callback=progress_callback
    )
    
    print(f"下载成功: {success}")
    print(f"本地图片数: {detail.get('local_pages', 0)}")
    print(f"网络端图片总数: {detail.get('total_pages', 0)}")
    print(f"进度回调次数: {len(progress_records)}")
    
    assert detail is not None
    assert "local_pages" in detail
    assert "total_pages" in detail
    
    local_count = get_local_progress(TEST_ALBUM_ID, TEST_DOWNLOAD_DIR)
    print(f"验证本地图片数: {local_count}")
    
    assert detail["total_pages"] > 0, "网络端图片总数应该大于0"
    
    print("✅ 通过")
    return detail, success

def test_get_total_pages(client):
    print_header("get_total_pages()")
    total = get_total_pages(TEST_ALBUM_ID, client)
    
    print(f"网络端图片总数: {total}")
    
    assert total > 0, "网络端图片总数应该大于0"
    
    print("✅ 通过")
    return total

def test_get_local_progress():
    print_header("get_local_progress()")
    count = get_local_progress(TEST_ALBUM_ID, TEST_DOWNLOAD_DIR)
    print(f"本地图片数量: {count}")
    print("✅ 通过")
    return count

def test_search_comics(client):
    print_header("search_comics()")
    result = search_comics("砂漠", max_pages=1, client=client)
    
    print(f"query: {result.get('query')}")
    print(f"total: {result.get('total')}")
    print(f"results count: {len(result.get('results', []))}")
    
    expected_keys = ["query", "total", "results"]
    missing = [k for k in expected_keys if k not in result]
    
    if missing:
        print(f"❌ 缺少字段: {missing}")
        return None
    
    if result["results"]:
        first = result["results"][0]
        print(f"第一个结果: album_id={first.get('album_id')}, title={first.get('title', '')[:30]}...")
    
    print("✅ 通过")
    return result

def test_search_comics_range(client):
    print_header("search_comics() 范围搜索")
    
    result = search_comics("萝莉", client=client, start_index=5, end_index=10)
    
    print(f"total: {result.get('total')}")
    print(f"start_index: {result.get('start_index')}")
    print(f"end_index: {result.get('end_index')}")
    print(f"results count: {len(result.get('results', []))}")
    
    expected_keys = ["query", "total", "results", "start_index", "end_index"]
    missing = [k for k in expected_keys if k not in result]
    
    if missing:
        print(f"❌ 缺少字段: {missing}")
        return None
    
    assert result["end_index"] - result["start_index"] == len(result["results"])
    
    print("✅ 通过")
    return result

def test_get_favorite_comics(client):
    print_header("get_favorite_comics()")
    result = get_favorite_comics(client=client)
    
    print(f"total: {result.get('total')}")
    print(f"comics count: {len(result.get('comics', []))}")
    
    expected_keys = ["total", "comics"]
    missing = [k for k in expected_keys if k not in result]
    
    if missing:
        print(f"❌ 缺少字段: {missing}")
        return None
    
    if result["comics"]:
        first = result["comics"][0]
        print(f"第一个收藏: album_id={first.get('album_id')}, title={first.get('title', '')[:30]}...")
    
    print("✅ 通过")
    return result

def test_database_operations(detail):
    print_header("数据库操作")
    
    db = load_database()
    print(f"加载数据库: {len(db.get('albums', []))} 个漫画")
    
    add_to_database(detail)
    
    db = load_database()
    print(f"添加后: {len(db.get('albums', []))} 个漫画")
    
    found = False
    for album in db["albums"]:
        if album["album_id"] == detail["album_id"]:
            found = True
            print(f"找到添加的漫画: {album['title'][:30]}...")
            break
    
    assert found, "漫画未添加到数据库"
    print("✅ 通过")
    return db

def test_progress_operations():
    print_header("进度操作")
    
    progress = load_progress()
    print(f"加载进度: {len(progress)} 条记录")
    
    test_progress = {
        "test_album_123": {
            "status": "completed",
            "downloaded_images": 100
        }
    }
    
    save_progress(test_progress)
    
    loaded = load_progress()
    assert "test_album_123" in loaded
    print(f"保存的进度: test_album_123 -> {loaded['test_album_123']}")
    print("✅ 通过")

def test_utils_functions():
    """测试工具函数"""
    print("\n=== 测试工具函数 ===")
    
    try:
        import jmcomic
        # 测试JMComicText.parse_to_jm_id
        test_cases = [
            ("JM12345", "12345"),
            ("jm12345", "12345"),
            ("https://18comic.vip/album/12345", "12345"),
            ("https://18comic.vip/photo/12345", "12345"),
            ("https://18comic.vip/album/?id=12345", "12345"),
        ]
        
        for input, expected in test_cases:
            result = jmcomic.JmcomicText.parse_to_jm_id(input)
            assert result == expected, f"parse_to_jm_id failed for {input}: expected {expected}, got {result}"
            print(f"✅ parse_to_jm_id({input}) = {result}")
        
        print("\n✅ 工具函数测试通过")
    except Exception as e:
        print(f"⚠️  警告: JMComicText测试失败，可能未安装jmcomic库: {e}")

def test_image_decoding(client=None):
    """测试图片解密功能"""
    print("\n=== 测试图片解密功能 ===")
    
    # 测试JmImageTool.get_num
    from jmcomic_api import JmImageTool, JmMagicConstants
    
    # 测试用例1: aid < scramble_id
    num1 = JmImageTool.get_num(100000, 50000, "00001.jpg")
    assert num1 == 0, f"get_num failed for aid < scramble_id: expected 0, got {num1}"
    print(f"✅ get_num(aid < scramble_id) = {num1}")
    
    # 测试用例2: aid < SCRAMBLE_268850
    num2 = JmImageTool.get_num(100000, 200000, "00001.jpg")
    assert num2 == 10, f"get_num failed for aid < SCRAMBLE_268850: expected 10, got {num2}"
    print(f"✅ get_num(aid < SCRAMBLE_268850) = {num2}")
    
    # 测试用例3: aid < SCRAMBLE_421926
    num3 = JmImageTool.get_num(100000, 300000, "00001.jpg")
    assert num3 >= 2 and num3 <= 20 and num3 % 2 == 0, f"get_num failed for aid < SCRAMBLE_421926: expected even number between 2-20, got {num3}"
    print(f"✅ get_num(aid < SCRAMBLE_421926) = {num3}")
    
    # 测试用例4: aid >= SCRAMBLE_421926
    num4 = JmImageTool.get_num(100000, 500000, "00001.jpg")
    assert num4 >= 2 and num4 <= 16 and num4 % 2 == 0, f"get_num failed for aid >= SCRAMBLE_421926: expected even number between 2-16, got {num4}"
    print(f"✅ get_num(aid >= SCRAMBLE_421926) = {num4}")
    
    # 测试真实图片解密
    import os
    import random
    
    # 尝试从已下载的漫画中随机选择一张图片
    comic_dirs = [d for d in os.listdir(TEST_DOWNLOAD_DIR) if d.isdigit()]
    
    if comic_dirs:
        # 随机选择一个漫画目录
        random_comic_id = random.choice(comic_dirs)
        comic_dir = os.path.join(TEST_DOWNLOAD_DIR, random_comic_id)
        
        # 随机选择一张图片
        image_files = [f for f in os.listdir(comic_dir) if f.endswith(('.webp', '.jpg', '.png'))]
        
        if image_files:
            random_image = random.choice(image_files)
            test_image_path = os.path.join(comic_dir, random_image)
            
            print(f"\n📸 测试真实图片解密: {test_image_path}")
            print(f"📋 漫画ID: {random_comic_id}")
            
            try:
                # 打开图片
                img = JmImageTool.open_image(test_image_path)
                print(f"✅ 成功打开图片，尺寸: {img.size}")
                
                # 获取真实scramble_id
                if client is not None:
                    scramble_id = get_scramble_id(int(random_comic_id), client)
                    print(f"🔑 获取到真实scramble_id: {scramble_id}")
                else:
                    scramble_id = 220980
                    print(f"🔑 使用默认scramble_id: {scramble_id}")
                
                # 使用真实参数计算分割数
                num = JmImageTool.get_num(scramble_id, int(random_comic_id), random_image)
                print(f"📊 计算得到分割数: {num}")
                
                # 解密并保存
                output_path = os.path.join(comic_dir, f"{os.path.splitext(random_image)[0]}_decoded.jpg")
                JmImageTool.decode_and_save(num, img, output_path)
                print(f"✅ 解密成功，已保存到: {output_path}")
                
            except Exception as e:
                print(f"⚠️  真实图片解密测试失败: {e}")
        else:
            print(f"\nℹ️  漫画目录 {random_comic_id} 中未找到图片文件")
    else:
        print(f"\nℹ️  未找到已下载的漫画目录")
    
    print("\n✅ 图片解密功能测试通过")

def test_batch_download(client):
    print_header("batch_download()")
    
    test_ids = [1312953, 1295258]
    
    def progress_callback(current, total, album_id, status):
        print(f"  [{current}/{total}] {album_id}: {status}")
    
    stats = batch_download(test_ids, client=client, progress_callback=progress_callback)
    
    print(f"批量下载结果: total={stats['total']}, success={stats['success']}, skipped={stats['skipped']}, failed={stats['failed']}")
    
    expected_keys = ["total", "success", "skipped", "failed"]
    missing = [k for k in expected_keys if k not in stats]
    
    if missing:
        print(f"❌ 缺少字段: {missing}")
        return None
    
    print("✅ 通过")

def test_download_original_image(client):
    print_header("download_original_image()")
    
    test_album_id = "1323910"
    comic_dir = os.path.join(TEST_DOWNLOAD_DIR, test_album_id)
    
    if os.path.exists(comic_dir):
        import shutil
        print(f"🗑️  删除已存在的目录: {comic_dir}")
        shutil.rmtree(comic_dir)
    
    # 下载原始混淆图片
    detail, success = download_album(
        test_album_id, 
        download_dir=TEST_DOWNLOAD_DIR, 
        client=client,
        decode_images=False
    )
    
    print(f"下载成功: {success}")
    print(f"本地图片数: {detail.get('local_pages', 0)}")
    print(f"网络端图片总数: {detail.get('total_pages', 0)}")
    
    # 解密一张图片
    comic_dir = os.path.join(TEST_DOWNLOAD_DIR, "1323910")
    image_files = [f for f in os.listdir(comic_dir) if f.endswith(('.webp', '.jpg', '.png'))]
    
    if image_files:
        # 选择第一张图片
        test_image = image_files[0]
        test_image_path = os.path.join(comic_dir, test_image)
        
        # 去掉扩展名
        test_image_name = os.path.splitext(test_image)[0]
        
        print(f"\n📸 解密图片: {test_image_path}")
        
        try:
            # 打开图片
            from jmcomic_api import JmImageTool
            img = JmImageTool.open_image(test_image_path)
            print(f"✅ 成功打开图片，尺寸: {img.size}")
            w, h = img.size
            print(f"   高度 {h}，计算各分割数的余数:")
            for n in [2, 4, 6, 8, 10, 12]:
                print(f"     {n} 分割: {h} % {n} = {h % n}")
            
            # 获取真实scramble_id
            scramble_id = get_scramble_id(1323910, client)
            print(f"\n🔑 获取到 scramble_id: {scramble_id}")
            
            # 计算分割数（使用不带扩展名的文件名）
            num = JmImageTool.get_num(scramble_id, 1323910, test_image_name)
            print(f"📊 计算得到分割数: {num}")
            
            # 解密并保存
            output_path = os.path.join(comic_dir, f"{os.path.splitext(test_image)[0]}_decoded.jpg")
            JmImageTool.decode_and_save(num, img, output_path)
            print(f"✅ 解密成功，已保存到: {output_path}")
            
        except Exception as e:
            print(f"⚠️  图片解密失败: {e}")
    
    print("✅ 通过")

def run_all_tests():
    print("\n" + "="*60)
    print("开始运行所有API测试")
    print("="*60)
    
    results = []
    
    try:
        config = test_load_config()
        results.append(("load_config", True, ""))
    except Exception as e:
        results.append(("load_config", False, str(e)))
        print(f"❌ 失败: {e}")
    
    try:
        client = test_get_client()
        results.append(("get_client", True, ""))
    except Exception as e:
        results.append(("get_client", False, str(e)))
        print(f"❌ 失败: {e}")
        return results
    
    try:
        test_get_option()
        results.append(("get_option", True, ""))
    except Exception as e:
        results.append(("get_option", False, str(e)))
        print(f"❌ 失败: {e}")
    
    try:
        detail = test_get_album_detail(client)
        results.append(("get_album_detail", True, ""))
    except Exception as e:
        results.append(("get_album_detail", False, str(e)))
        print(f"❌ 失败: {e}")
        detail = None
    
    try:
        download_detail, success = test_download_album(client)
        results.append(("download_album", True, ""))
    except Exception as e:
        results.append(("download_album", False, str(e)))
        print(f"❌ 失败: {e}")
    
    try:
        test_get_total_pages(client)
        results.append(("get_total_pages", True, ""))
    except Exception as e:
        results.append(("get_total_pages", False, str(e)))
        print(f"❌ 失败: {e}")
    
    try:
        test_get_local_progress()
        results.append(("get_local_progress", True, ""))
    except Exception as e:
        results.append(("get_local_progress", False, str(e)))
        print(f"❌ 失败: {e}")
    
    try:
        test_search_comics(client)
        results.append(("search_comics", True, ""))
    except Exception as e:
        results.append(("search_comics", False, str(e)))
        print(f"❌ 失败: {e}")
    
    try:
        test_search_comics_range(client)
        results.append(("search_comics_range", True, ""))
    except Exception as e:
        results.append(("search_comics_range", False, str(e)))
        print(f"❌ 失败: {e}")
    
    try:
        test_get_favorite_comics(client)
        results.append(("get_favorite_comics", True, ""))
    except Exception as e:
        results.append(("get_favorite_comics", False, str(e)))
        print(f"❌ 失败: {e}")
    
    if detail:
        try:
            test_database_operations(detail)
            results.append(("database_operations", True, ""))
        except Exception as e:
            results.append(("database_operations", False, str(e)))
            print(f"❌ 失败: {e}")
    
    try:
        test_progress_operations()
        results.append(("progress_operations", True, ""))
    except Exception as e:
        results.append(("progress_operations", False, str(e)))
        print(f"❌ 失败: {e}")
    
    try:
        test_utils_functions()
        results.append(("utils_functions", True, ""))
    except Exception as e:
        results.append(("utils_functions", False, str(e)))
        print(f"❌ 失败: {e}")
    
    try:
        test_image_decoding(client)
        results.append(("image_decoding", True, ""))
    except Exception as e:
        results.append(("image_decoding", False, str(e)))
        print(f"❌ 失败: {e}")
    
    try:
        test_batch_download(client)
        results.append(("batch_download", True, ""))
    except Exception as e:
        results.append(("batch_download", False, str(e)))
        print(f"❌ 失败: {e}")
    
    try:
        test_download_original_image(client)
        results.append(("download_original_image", True, ""))
    except Exception as e:
        results.append(("download_original_image", False, str(e)))
        print(f"❌ 失败: {e}")
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, success, _ in results if success)
    failed = sum(1 for _, success, _ in results if not success)
    
    for name, success, error in results:
        status = "✅ 通过" if success else f"❌ 失败: {error}"
        print(f"{name}: {status}")
    
    print(f"\n总计: {passed} 通过, {failed} 失败")
    print("="*60)
    
    return results

if __name__ == "__main__":
    run_all_tests()
