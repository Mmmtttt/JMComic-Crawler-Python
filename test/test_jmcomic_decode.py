"""
直接测试jmcomic库的图片解密功能
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jmcomic
from jmcomic_api import load_config

# 测试目录
test_dir = os.path.join(os.path.dirname(__file__), 'pictures', 'test_jmcomic')
os.makedirs(test_dir, exist_ok=True)

print(f"测试目录: {test_dir}")

# 测试1: 启用decode=True
print("\n=== 测试1: option中decode=True ===")
option1 = jmcomic.JmOption.construct({
    'download': {
        'dir': test_dir,
        'image': {
            'decode': True,
            'suffix': '.jpg'
        }
    },
    'dir_rule': {
        'base_dir': test_dir,
        'rule': 'Bd_Aid'
    }
})

downloader1 = jmcomic.JmDownloader(option1)
downloader1.download_album(1312953)

# 检查图片
comic_dir1 = os.path.join(test_dir, "1312953")
if os.path.exists(comic_dir1):
    images1 = sorted(os.listdir(comic_dir1))
    print(f"下载成功: {len(images1)} 张图片")
    print(f"前3张: {images1[:3]}")
else:
    print("目录不存在")

# 测试2: 禁用decode=False
print("\n=== 测试2: option中decode=False ===")
test_dir2 = os.path.join(os.path.dirname(__file__), 'pictures', 'test_jmcomic2')
os.makedirs(test_dir2, exist_ok=True)

option2 = jmcomic.JmOption.construct({
    'download': {
        'dir': test_dir2,
        'image': {
            'decode': False,
            'suffix': '.jpg'
        }
    },
    'dir_rule': {
        'base_dir': test_dir2,
        'rule': 'Bd_Aid'
    }
})

downloader2 = jmcomic.JmDownloader(option2)
downloader2.download_album(1323910)

# 检查图片
comic_dir2 = os.path.join(test_dir2, "1323910")
if os.path.exists(comic_dir2):
    images2 = sorted(os.listdir(comic_dir2))
    print(f"下载成功: {len(images2)} 张图片")
    print(f"前3张: {images2[:3]}")
else:
    print("目录不存在")

print("\n=== 测试完成 ===")
