"""
JMComic 工具函数模块
提供配置管理、文件操作、统计等工具函数
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional

_config = None

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

def save_config(config: Dict) -> None:
    """保存配置文件"""
    global _config
    _config = config
    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def reset_config() -> None:
    """重置配置缓存"""
    global _config
    _config = None


def ensure_dir(path: str) -> str:
    """确保目录存在，不存在则创建"""
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_file_list(directory: str, extensions: List[str] = None) -> List[str]:
    """
    获取目录下的文件列表
    
    Args:
        directory: 目录路径
        extensions: 文件扩展名列表（如 ['.jpg', '.png']）
    
    Returns:
        文件路径列表
    """
    if not os.path.exists(directory):
        return []
    
    files = []
    for file in os.listdir(directory):
        if extensions:
            if any(file.endswith(ext) for ext in extensions):
                files.append(os.path.join(directory, file))
        else:
            files.append(os.path.join(directory, file))
    
    return files

def count_images(directory: str) -> int:
    """统计目录下的图片数量"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
    return len(get_file_list(directory, image_extensions))


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"

def get_directory_size(directory: str) -> int:
    """获取目录大小（字节）"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
            except:
                pass
    return total_size


def load_json_file(filepath: str, default: any = None) -> any:
    """加载JSON文件"""
    if not os.path.exists(filepath):
        return default
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default

def save_json_file(filepath: str, data: any) -> None:
    """保存JSON文件"""
    ensure_dir(os.path.dirname(filepath))
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_text_file(filepath: str) -> List[str]:
    """加载文本文件，返回行列表"""
    if not os.path.exists(filepath):
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def save_text_file(filepath: str, lines: List[str]) -> None:
    """保存文本文件"""
    ensure_dir(os.path.dirname(filepath))
    with open(filepath, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(f"{line}\n")


def print_progress(current: int, total: int, prefix: str = "", suffix: str = ""):
    """打印进度"""
    percent = (current / total) * 100
    bar_length = 40
    filled = int(bar_length * current / total)
    bar = '█' * filled + '-' * (bar_length - filled)
    print(f"\r{prefix} |{bar}| {current}/{total} ({percent:.1f}%) {suffix}", end='', flush=True)
    if current == total:
        print()

def print_table(data: List[Dict], columns: List[str] = None, max_width: int = 50):
    """打印表格"""
    if not data:
        print("无数据")
        return
    
    if columns is None:
        columns = list(data[0].keys())
    
    col_widths = {}
    for col in columns:
        max_len = len(col)
        for row in data:
            val = str(row.get(col, ''))
            max_len = max(max_len, min(len(val), max_width))
        col_widths[col] = max_len
    
    header = " | ".join(col.ljust(col_widths[col]) for col in columns)
    print(header)
    print("-" * len(header))
    
    for row in data:
        values = []
        for col in columns:
            val = str(row.get(col, ''))
            if len(val) > max_width:
                val = val[:max_width-3] + "..."
            values.append(val.ljust(col_widths[col]))
        print(" | ".join(values))


def get_download_stats(download_dir: str = None, database_file: str = None) -> Dict:
    """
    获取下载统计信息
    
    Returns:
        统计信息字典
    """
    config = load_config()
    download_dir = download_dir or config.get("download_dir", "pictures")
    database_file = database_file or config.get("output_json", "comics_database.json")
    
    database = load_json_file(database_file, {"albums": []})
    
    total_albums = len(database.get("albums", []))
    downloaded_albums = 0
    total_images = 0
    total_size = 0
    
    if os.path.exists(download_dir):
        for album_dir in os.listdir(download_dir):
            album_path = os.path.join(download_dir, album_dir)
            if os.path.isdir(album_path):
                image_count = count_images(album_path)
                if image_count > 0:
                    downloaded_albums += 1
                    total_images += image_count
                    total_size += get_directory_size(album_path)
    
    return {
        "database_albums": total_albums,
        "downloaded_albums": downloaded_albums,
        "total_images": total_images,
        "total_size": total_size,
        "total_size_formatted": format_file_size(total_size),
        "download_dir": download_dir
    }

def print_download_stats():
    """打印下载统计信息"""
    stats = get_download_stats()
    
    print("=" * 50)
    print("下载统计")
    print("=" * 50)
    print(f"数据库漫画数: {stats['database_albums']}")
    print(f"已下载漫画数: {stats['downloaded_albums']}")
    print(f"总图片数: {stats['total_images']}")
    print(f"总大小: {stats['total_size_formatted']}")
    print(f"下载目录: {stats['download_dir']}")
    print("=" * 50)


def merge_databases(db1: Dict, db2: Dict) -> Dict:
    """合并两个数据库"""
    merged = {
        "collection_name": db1.get("collection_name", "合并收藏"),
        "user": db1.get("user", ""),
        "total_favorites": 0,
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "albums": []
    }
    
    album_dict = {}
    
    for album in db1.get("albums", []):
        album_dict[album["album_id"]] = album
    
    for album in db2.get("albums", []):
        if album["album_id"] not in album_dict:
            album_dict[album["album_id"]] = album
    
    merged["albums"] = list(album_dict.values())
    merged["albums"].sort(key=lambda x: x.get("rank", 0))
    
    for i, album in enumerate(merged["albums"], 1):
        album["rank"] = i
    
    merged["total_favorites"] = len(merged["albums"])
    
    return merged


def export_album_list(database: Dict, output_file: str, format: str = "txt") -> None:
    """
    导出漫画列表
    
    Args:
        database: 数据库对象
        output_file: 输出文件路径
        format: 格式 (txt, csv, json)
    """
    albums = database.get("albums", [])
    
    if format == "txt":
        lines = [str(album["album_id"]) for album in albums]
        save_text_file(output_file, lines)
    elif format == "csv":
        lines = ["album_id,title,author,pages"]
        for album in albums:
            title = album.get("title", "").replace(",", "，")
            author = album.get("author", "").replace(",", "，")
            lines.append(f"{album['album_id']},{title},{author},{album.get('pages', 0)}")
        save_text_file(output_file, lines)
    elif format == "json":
        save_json_file(output_file, albums)


def validate_album_id(album_id: str or int) -> bool:
    """验证漫画ID是否有效"""
    try:
        aid = int(album_id)
        return aid > 0
    except:
        return False


def parse_album_ids(input_str: str) -> List[int]:
    """
    解析漫画ID字符串
    
    支持格式:
    - 单个ID: "123456"
    - 多个ID: "123456,789012"
    - 范围: "123456-123460"
    - 混合: "123456,789012,123460-123470"
    """
    ids = []
    
    for part in input_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            try:
                start_id = int(start.strip())
                end_id = int(end.strip())
                ids.extend(range(start_id, end_id + 1))
            except:
                pass
        else:
            try:
                ids.append(int(part))
            except:
                pass
    
    return list(set(ids))
