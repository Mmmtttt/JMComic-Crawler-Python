"""
JMComic API 模块
提供漫画搜索、下载、收藏管理等API接口
"""

import os
import jmcomic
import json
from typing import Dict, List, Optional, Tuple, Generator
from datetime import datetime
from PIL import Image
from io import BytesIO
import hashlib

_config = None
_client = None
_option = None

def load_config() -> Dict:
    """加载配置文件"""
    global _config
    if _config is not None:
        return _config
    
    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            _config = json.load(f)
    else:
        _config = {
            "username": "",
            "password": "",
            "download_dir": "pictures",
            "output_json": "comics_database.json",
            "progress_file": "download_progress.json",
            "favorite_list_file": "favorite_comics.txt",
            "consecutive_hit_threshold": 10,
            "collection_name": "我的最爱"
        }
    return _config

def get_client(username: str = None, password: str = None) -> jmcomic.JmHtmlClient:
    """获取JMComic客户端"""
    global _client, _option
    if _client is not None and username is None:
        return _client
    
    config = load_config()
    username = username or config.get("username", "")
    password = password or config.get("password", "")
    
    _option = jmcomic.JmOption.construct({
        'download': {
            'dir': config.get("download_dir", "pictures"),
            'image': {
                'suffix': '.jpg'
            }
        },
        'dir_rule': {
            'base_dir': config.get("download_dir", "pictures"),
            'rule': 'Bd_Aid'
        }
    })
    
    _client = _option.build_jm_client()
    
    if username and password:
        _client.login(username, password)
    
    return _client

def get_option() -> jmcomic.JmOption:
    """获取JMComic配置选项"""
    global _option
    if _option is not None:
        return _option
    
    config = load_config()
    _option = jmcomic.JmOption.construct({
        'download': {
            'dir': config.get("download_dir", "pictures"),
            'image': {
                'decode': True,
                'suffix': '.jpg'
            }
        },
        'dir_rule': {
            'base_dir': config.get("download_dir", "pictures"),
            'rule': 'Bd_Aid'
        }
    })
    return _option

def get_scramble_id(album_id: int or str, client: jmcomic.JmHtmlClient = None) -> str:
    """
    获取漫画的真实scramble_id
    
    Args:
        album_id: 漫画ID
        client: JMComic客户端
    
    Returns:
        scramble_id
    """
    if client is None:
        client = get_client()
    
    album = client.get_album_detail(album_id)
    scramble_id = album.scramble_id
    
    # 如果获取到的scramble_id无效，使用默认值
    if scramble_id is None or scramble_id == 0 or scramble_id == '':
        scramble_id = 220980
    
    return str(scramble_id)

class JmMagicConstants:
    """JMComic魔法常量"""
    SCRAMBLE_268850 = 268850
    SCRAMBLE_421926 = 421926

class JmImageTool:
    """JMComic图片解密工具"""
    
    @classmethod
    def decode_and_save(cls,
                        num: int,
                        img_src: Image,
                        decoded_save_path: str
                        ) -> None:
        """
        解密图片并保存
        :param num: 分割数
        :param img_src: 原始图片
        :param decoded_save_path: 解密图片的保存路径
        """

        # 无需解密，直接保存
        if num == 0:
            cls.save_image(img_src, decoded_save_path)
            return

        import math
        w, h = img_src.size

        # 创建新的解密图片，使用与源图片相同的模式以支持透明通道
        img_decode = Image.new(img_src.mode, (w, h))
        over = h % num
        for i in range(num):
            move = math.floor(h / num)
            y_src = h - (move * (i + 1)) - over
            y_dst = move * i

            if i == 0:
                move += over
            else:
                y_dst += over

            img_decode.paste(
                img_src.crop((
                    0, y_src,
                    w, y_src + move
                )),
                (
                    0, y_dst,
                    w, y_dst + move
                )
            )

        # 保存到新的解密文件
        cls.save_image(img_decode, decoded_save_path)

    @classmethod
    def save_image(cls, image: Image, filepath: str):
        """
        保存图片

        :param image: PIL.Image对象
        :param filepath: 保存文件路径
        """
        image.save(filepath)

    @classmethod
    def open_image(cls, fp):
        """
        打开图片

        :param fp: 文件路径或字节数据
        """
        fp = fp if isinstance(fp, str) else BytesIO(fp)
        return Image.open(fp)

    @classmethod
    def get_num(cls, scramble_id, aid, filename: str) -> int:
        """
        获得图片分割数
        """

        scramble_id = int(scramble_id)
        aid = int(aid)

        if aid < scramble_id:
            return 0
        elif aid < JmMagicConstants.SCRAMBLE_268850:
            return 10
        else:
            x = 10 if aid < JmMagicConstants.SCRAMBLE_421926 else 8
            s = f"{aid}{filename}"  # 拼接
            s = s.encode()
            s = hashlib.md5(s).hexdigest()
            num = ord(s[-1])
            num %= x
            num = num * 2 + 2
            return num

    @classmethod
    def get_num_by_url(cls, scramble_id, url) -> int:
        """
        获得图片分割数
        """
        return cls.get_num(
            scramble_id,
            aid=jmcomic.JmcomicText.parse_to_jm_id(url),
            filename=os.path.basename(url).split('.')[0],
        )


def get_album_detail(album_id: int or str, client: jmcomic.JmHtmlClient = None) -> Dict:
    """
    获取漫画详情
    
    Args:
        album_id: 漫画ID
        client: JMComic客户端（可选）
    
    Returns:
        漫画详情字典
    """
    if client is None:
        client = get_client()
    
    album = client.get_album_detail(album_id)
    
    total_pages = album.page_count
    if total_pages == 0:
        total_pages = 0
        for i in range(len(album)):
            try:
                photo = album[i]
                photo_detail = client.get_photo_detail(photo.photo_id)
                if photo_detail.page_arr:
                    total_pages += len(photo_detail.page_arr)
            except:
                pass
    
    return {
        "album_id": int(album.id),
        "title": album.name,
        "title_jp": getattr(album, 'name_jp', ""),
        "author": album.author if album.author else "未知",
        "pages": total_pages,
        "cover_url": f"https://cdn-msp3.18comic.vip/media/albums/{album.id}.jpg",
        "album_url": f"https://18comic.vip/album/{album.id}",
        "tags": list(album.tags) if album.tags else [],
        "category_tags": list(album.category_tags) if hasattr(album, 'category_tags') and album.category_tags else [],
        "upload_date": str(getattr(album, 'pub_date', '0')),
        "update_date": str(getattr(album, 'update_date', '0')),
        "episode_count": len(album),
        "likes": getattr(album, 'likes', ''),
        "views": getattr(album, 'views', '')
    }

class ProgressDownloader(jmcomic.JmDownloader):
    """
    带进度回调的下载器
    """
    
    def __init__(self, option=None, progress_callback=None, decode_images=True):
        super().__init__(option)
        self.progress_callback = progress_callback
        self.decode_images = decode_images
        self.current_image = 0
        self.total_images = 0
    
    def before_album(self, album):
        super().before_album(album)
        self.total_images = 0
        self.current_image = 0
        for i in range(len(album)):
            photo = album[i]
            if hasattr(photo, 'page_arr') and photo.page_arr:
                self.total_images += len(photo.page_arr)
    
    def before_image(self, image, img_save_path):
        super().before_image(image, img_save_path)
        if self.progress_callback:
            self.progress_callback(
                current=image.index,
                total=len(image.from_photo) if image.from_photo else 0,
                image_filename=f"{image.img_file_name}{image.img_file_suffix}",
                status="downloading"
            )
    
    def after_image(self, image, img_save_path):
        """
        图片下载完成后解密
        """
        super().after_image(image, img_save_path)
        
        if not self.decode_images:
            return
        
        # 获取真实scramble_id
        scramble_id = None
        if hasattr(image, 'scramble_id') and image.scramble_id is not None:
            scramble_id = str(image.scramble_id)
        elif hasattr(image.from_photo, 'scramble_id') and image.from_photo.scramble_id is not None:
            scramble_id = str(image.from_photo.scramble_id)
        
        # 如果无法从image对象获取，尝试从album获取
        if not scramble_id or scramble_id == '0' or scramble_id == '':
            try:
                scramble_id = get_scramble_id(image.aid)
            except:
                pass
        
        # 如果无法获取scramble_id，使用默认值
        if not scramble_id or scramble_id == '0' or scramble_id == '':
            scramble_id = '220980'
        
        # 计算分割数
        num = JmImageTool.get_num(
            scramble_id,
            aid=jmcomic.JmcomicText.parse_to_jm_id(image.aid),
            filename=image.img_file_name
        )
        
        # 解密图片
        if num > 0:
            try:
                img = JmImageTool.open_image(img_save_path)
                JmImageTool.decode_and_save(num, img, img_save_path)
            except Exception as e:
                print(f"图片解密失败: {img_save_path}, 错误: {e}")

def get_total_pages(album_id: int or str, client: jmcomic.JmHtmlClient = None) -> int:
    """
    获取漫画的网络端图片总数
    
    Args:
        album_id: 漫画ID
        client: JMComic客户端（可选）
    
    Returns:
        网络端图片总数
    """
    if client is None:
        client = get_client()
    
    album = client.get_album_detail(album_id)
    total_pages = 0
    
    for episode in album.episode_list:
        photo_id = episode[0]
        try:
            photo_detail = client.get_photo_detail(photo_id)
            if photo_detail.page_arr:
                total_pages += len(photo_detail.page_arr)
        except:
            pass
    
    return total_pages

def download_album(album_id: int or str, download_dir: str = None, 
                   client: jmcomic.JmHtmlClient = None, 
                   show_progress: bool = True,
                   progress_callback: callable = None,
                   decode_images: bool = True) -> Tuple[Dict, bool]:
    """
    下载漫画
    
    Args:
        album_id: 漫画ID
        download_dir: 下载目录（可选）
        client: JMComic客户端（可选）
        show_progress: 是否显示进度（可选，默认True）
        progress_callback: 进度回调函数（可选），参数: (current, total, image_filename, status)
        decode_images: 是否解密图片（可选，默认True）
    
    Returns:
        (漫画详情字典, 是否成功)
        详情字典包含:
        - total_pages: 网络端图片总数
        - local_pages: 本地已下载图片数
        - downloaded: 是否下载成功
    """
    config = load_config()
    download_dir = download_dir or config.get("download_dir", "pictures")
    
    if client is None:
        client = get_client()
    
    if show_progress:
        print(f"正在获取漫画 {album_id} 的信息...")
    
    total_pages = get_total_pages(album_id, client)
    
    if show_progress:
        print(f"网络端图片总数: {total_pages}")
    
    option = get_option()
    if download_dir != config.get("download_dir", "pictures"):
        option = jmcomic.JmOption.construct({
            'download': {
                'dir': download_dir,
                'image': {
                    'decode': decode_images,
                    'suffix': '.jpg'
                }
            },
            'dir_rule': {
                'base_dir': download_dir,
                'rule': 'Bd_Aid'
            }
        })
    
    if show_progress:
        print(f"开始下载漫画 {album_id}...")
    
    downloader = ProgressDownloader(option, progress_callback=progress_callback, decode_images=decode_images)
    album = downloader.download_album(album_id)
    
    success = not downloader.has_download_failures
    local_pages = get_local_progress(album_id, download_dir)
    
    if show_progress:
        print(f"下载完成: {local_pages}/{total_pages} 张图片")
    
    detail = get_album_detail(album_id, client)
    detail['downloaded'] = success
    detail['local_pages'] = local_pages
    detail['total_pages'] = total_pages
    
    return detail, success

def get_local_progress(album_id: int or str, download_dir: str = None) -> int:
    """
    获取本地已下载的图片数量
    
    Args:
        album_id: 漫画ID
        download_dir: 下载目录
    
    Returns:
        已下载图片数量
    """
    config = load_config()
    download_dir = download_dir or config.get("download_dir", "pictures")
    
    comic_dir = os.path.join(download_dir, str(album_id))
    if not os.path.exists(comic_dir):
        return 0
    
    image_files = []
    for file in os.listdir(comic_dir):
        if file.endswith('.jpg') or file.endswith('.webp') or file.endswith('.png'):
            image_files.append(file)
    
    return len(image_files)


def search_comics(query: str, page: int = 1, max_pages: int = None,
                  client: jmcomic.JmHtmlClient = None,
                  start_index: int = None, end_index: int = None) -> Dict:
    """
    搜索漫画
    
    Args:
        query: 搜索关键词
        page: 起始页码 (从1开始)
        max_pages: 最大页数（None表示获取所有结果）
        client: JMComic客户端
        start_index: 起始个数索引 (从0开始，如70表示从第70个开始)
        end_index: 结束个数索引 (如80表示到第80个结束，不包含)
        注意: start_index和end_index优先于page和max_pages
    
    Returns:
        搜索结果字典:
        {
            "query": str,           # 搜索关键词
            "total": int,           # 总结果数
            "page_count": int,      # 总页数
            "page_size": int,       # 每页数量
            "start_index": int,    # 实际起始索引
            "end_index": int,      # 实际结束索引(不包含)
            "results": list        # 搜索结果列表
        }
    """
    if client is None:
        client = get_client()
    
    first_page = client.search_site(
        search_query=query,
        page=page,
        order_by=jmcomic.JmMagicConstants.ORDER_BY_LATEST
    )
    
    total_results = first_page.total
    page_size = first_page.page_size if hasattr(first_page, 'page_size') else 30
    total_pages = first_page.page_count
    
    if start_index is not None or end_index is not None:
        start_idx = start_index if start_index is not None else 0
        end_idx = end_index if end_index is not None else total_results
        
        start_idx = max(0, min(start_idx, total_results))
        end_idx = max(start_idx, min(end_idx, total_results))
        
        start_page = start_idx // page_size + 1
        end_page = (end_idx + page_size - 1) // page_size
        
        all_results = []
        current_page = start_page
        
        while current_page <= end_page:
            if current_page == start_page:
                search_page = first_page if current_page == page else client.search_site(
                    search_query=query,
                    page=current_page,
                    order_by=jmcomic.JmMagicConstants.ORDER_BY_LATEST
                )
            else:
                search_page = client.search_site(
                    search_query=query,
                    page=current_page,
                    order_by=jmcomic.JmMagicConstants.ORDER_BY_LATEST
                )
            
            if not search_page.content:
                break
            
            for album_id, album_info in search_page.content:
                all_results.append({
                    "album_id": int(album_id),
                    "title": album_info.get('name', ''),
                    "tags": album_info.get('tags', [])
                })
            
            current_page += 1
        
        results = all_results[start_idx % page_size:]
        results = results[:end_idx - start_idx]
        
        return {
            "query": query,
            "total": total_results,
            "page_count": total_pages,
            "page_size": page_size,
            "start_index": start_idx,
            "end_index": end_idx,
            "results": results
        }
    
    all_results = []
    current_page = page
    
    while True:
        if current_page == page:
            search_page = first_page
        else:
            search_page = client.search_site(
                search_query=query,
                page=current_page,
                order_by=jmcomic.JmMagicConstants.ORDER_BY_LATEST
            )
        
        if not search_page.content:
            break
        
        for album_id, album_info in search_page.content:
            all_results.append({
                "album_id": int(album_id),
                "title": album_info.get('name', ''),
                "tags": album_info.get('tags', [])
            })
        
        if max_pages and current_page >= max_pages:
            break
        
        if current_page >= search_page.page_count:
            break
        
        current_page += 1
    
    return {
        "query": query,
        "total": total_results,
        "page_count": total_pages,
        "page_size": page_size,
        "start_index": 0,
        "end_index": len(all_results),
        "results": all_results
    }

def search_comics_full(query: str, page: int = 1, max_pages: int = None,
                       client: jmcomic.JmHtmlClient = None,
                       start_index: int = None, end_index: int = None) -> Dict:
    """
    搜索漫画并获取详细信息
    
    Args:
        query: 搜索关键词
        page: 起始页码 (从1开始)
        max_pages: 最大页数
        client: JMComic客户端
        start_index: 起始个数索引 (从0开始)
        end_index: 结束个数索引 (不包含)
    
    Returns:
        搜索结果字典（包含详细信息）
    """
    result = search_comics(query, page, max_pages, client, start_index, end_index)
    
    if client is None:
        client = get_client()
    
    detailed_results = []
    for i, item in enumerate(result['results'], 1):
        try:
            detail = get_album_detail(item['album_id'], client)
            detail['rank'] = i
            detailed_results.append(detail)
        except Exception as e:
            detailed_results.append({
                **item,
                'rank': i,
                'error': str(e)
            })
    
    result['results'] = detailed_results
    return result


def get_favorite_comics(username: str = None, password: str = None,
                        client: jmcomic.JmHtmlClient = None) -> Dict:
    """
    获取用户收藏夹
    
    Args:
        username: 用户名
        password: 密码
        client: JMComic客户端
    
    Returns:
        收藏夹信息字典
    """
    if client is None:
        client = get_client(username, password)
    
    favorite_page = client.favorite_folder(page=1, order_by=jmcomic.JmMagicConstants.ORDER_BY_LATEST, folder_id='0')
    
    total = favorite_page.total
    comic_ids = []
    
    for album_id, album_info in favorite_page.content:
        comic_ids.append({
            "album_id": int(album_id),
            "title": album_info.get('name', ''),
            "tags": album_info.get('tags', [])
        })
    
    if favorite_page.page_count > 1:
        for page in range(2, favorite_page.page_count + 1):
            page_result = client.favorite_folder(page=page, order_by=jmcomic.JmMagicConstants.ORDER_BY_LATEST, folder_id='0')
            for album_id, album_info in page_result.content:
                comic_ids.append({
                    "album_id": int(album_id),
                    "title": album_info.get('name', ''),
                    "tags": album_info.get('tags', [])
                })
    
    return {
        "total": total,
        "comics": comic_ids
    }

def get_favorite_comics_full(username: str = None, password: str = None,
                             client: jmcomic.JmHtmlClient = None) -> Dict:
    """
    获取用户收藏夹并获取详细信息
    
    Args:
        username: 用户名
        password: 密码
        client: JMComic客户端
    
    Returns:
        收藏夹信息字典（包含详细信息）
    """
    result = get_favorite_comics(username, password, client)
    
    if client is None:
        client = get_client(username, password)
    
    detailed_comics = []
    for i, item in enumerate(result['comics'], 1):
        try:
            detail = get_album_detail(item['album_id'], client)
            detail['rank'] = i
            detailed_comics.append(detail)
        except Exception as e:
            detailed_comics.append({
                **item,
                'rank': i,
                'error': str(e)
            })
    
    result['comics'] = detailed_comics
    return result


def load_database() -> Dict:
    """加载数据库"""
    config = load_config()
    db_file = config.get("output_json", "comics_database.json")
    
    if os.path.exists(db_file):
        with open(db_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "collection_name": config.get("collection_name", "我的最爱"),
            "user": config.get("username", ""),
            "total_favorites": 0,
            "last_updated": "",
            "albums": []
        }

def save_database(database: Dict) -> None:
    """保存数据库"""
    config = load_config()
    db_file = config.get("output_json", "comics_database.json")
    
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)

def add_to_database(album_detail: Dict, database: Dict = None) -> Dict:
    """
    添加漫画到数据库
    
    Args:
        album_detail: 漫画详情
        database: 数据库对象（可选）
    
    Returns:
        更新后的数据库
    """
    if database is None:
        database = load_database()
    
    album_id = album_detail['album_id']
    
    existing_index = None
    for i, a in enumerate(database["albums"]):
        if a["album_id"] == album_id:
            existing_index = i
            break
    
    album_info = {
        "rank": len(database["albums"]) + 1 if existing_index is None else database["albums"][existing_index]["rank"],
        "album_id": album_id,
        "title": album_detail.get("title", ""),
        "title_jp": album_detail.get("title_jp", ""),
        "author": album_detail.get("author", "未知"),
        "pages": album_detail.get("pages", 0),
        "cover_url": album_detail.get("cover_url", ""),
        "album_url": album_detail.get("album_url", ""),
        "tags": album_detail.get("tags", []),
        "category_tags": album_detail.get("category_tags", []),
        "upload_date": album_detail.get("upload_date", "0"),
        "update_date": album_detail.get("update_date", "0")
    }
    
    if existing_index is not None:
        database["albums"][existing_index] = album_info
    else:
        database["albums"].append(album_info)
        database["total_favorites"] = len(database["albums"])
    
    database["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    save_database(database)
    
    return database


def load_progress() -> Dict:
    """加载下载进度"""
    config = load_config()
    progress_file = config.get("progress_file", "download_progress.json")
    
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

def save_progress(progress: Dict) -> None:
    """保存下载进度"""
    config = load_config()
    progress_file = config.get("progress_file", "download_progress.json")
    
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def batch_download(album_ids: List[int or str], skip_existing: bool = True,
                   database: Dict = None, client: jmcomic.JmHtmlClient = None,
                   progress_callback: callable = None) -> Dict:
    """
    批量下载漫画
    
    Args:
        album_ids: 漫画ID列表
        skip_existing: 是否跳过已存在的漫画
        database: 数据库对象
        client: JMComic客户端
        progress_callback: 进度回调函数
    
    Returns:
        下载结果统计
    """
    if client is None:
        client = get_client()
    if database is None:
        database = load_database()
    
    progress = load_progress()
    config = load_config()
    
    stats = {
        "total": len(album_ids),
        "success": 0,
        "skipped": 0,
        "failed": 0,
        "results": []
    }
    
    album_dict = {a["album_id"]: a for a in database["albums"]}
    
    for i, album_id in enumerate(album_ids, 1):
        album_id = int(album_id)
        
        if progress_callback:
            progress_callback(i, len(album_ids), album_id, "starting")
        
        local_pages = get_local_progress(album_id)
        existing = album_dict.get(album_id)
        
        if skip_existing and existing and existing.get("pages", 0) > 0 and local_pages == existing["pages"]:
            stats["skipped"] += 1
            stats["results"].append({
                "album_id": album_id,
                "status": "skipped",
                "reason": "already_downloaded"
            })
            if progress_callback:
                progress_callback(i, len(album_ids), album_id, "skipped")
            continue
        
        try:
            detail, success = download_album(album_id, client=client)
            
            if success:
                stats["success"] += 1
                detail["status"] = "success"
                add_to_database(detail, database)
            else:
                stats["failed"] += 1
                detail["status"] = "partial"
            
            stats["results"].append(detail)
            
            if progress_callback:
                progress_callback(i, len(album_ids), album_id, "success" if success else "failed")
                
        except Exception as e:
            stats["failed"] += 1
            stats["results"].append({
                "album_id": album_id,
                "status": "error",
                "error": str(e)
            })
            if progress_callback:
                progress_callback(i, len(album_ids), album_id, "error")
    
    return stats


def sync_favorites(username: str = None, password: str = None,
                   threshold: int = None, download: bool = True,
                   client: jmcomic.JmHtmlClient = None) -> Dict:
    """
    同步收藏夹并下载新漫画
    
    Args:
        username: 用户名
        password: 密码
        threshold: 连续命中阈值
        download: 是否下载新漫画
        client: JMComic客户端
    
    Returns:
        同步结果统计
    """
    config = load_config()
    threshold = threshold or config.get("consecutive_hit_threshold", 10)
    
    if client is None:
        client = get_client(username, password)
    
    favorites = get_favorite_comics(username, password, client)
    database = load_database()
    
    album_dict = {a["album_id"]: a for a in database["albums"]}
    
    stats = {
        "total_favorites": favorites["total"],
        "existing": 0,
        "new": 0,
        "downloaded": 0,
        "failed": 0,
        "early_stop": False,
        "new_albums": []
    }
    
    consecutive_hits = 0
    new_album_ids = []
    
    for item in favorites["comics"]:
        album_id = item["album_id"]
        
        if album_id in album_dict:
            consecutive_hits += 1
            stats["existing"] += 1
            
            if consecutive_hits >= threshold:
                stats["early_stop"] = True
                break
        else:
            consecutive_hits = 0
            stats["new"] += 1
            new_album_ids.append(album_id)
    
    if download and new_album_ids:
        download_stats = batch_download(new_album_ids, client=client, database=database)
        stats["downloaded"] = download_stats["success"]
        stats["failed"] = download_stats["failed"]
        stats["new_albums"] = [r for r in download_stats["results"] if r.get("status") == "success"]
    
    return stats
