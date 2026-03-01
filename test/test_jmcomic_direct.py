"""
直接测试jmcomic库的图片解密功能 - 使用绝对路径
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jmcomic

# 测试目录 - 使用绝对路径
test_dir = r"D:\code\JMComic-Crawler-Python\test\pictures\test_jmcomic_decode"
os.makedirs(test_dir, exist_ok=True)

print(f"测试目录: {test_dir}")

# 清空目录
for item in os.listdir(test_dir):
    item_path = os.path.join(test_dir, item)
    if os.path.isdir(item_path):
        import shutil
        shutil.rmtree(item_path)

# 测试1: 启用decode=True
print("\n=== 测试1: 下载漫画1312953, decode=True ===")
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
    
    # 打印第一张图片的详细信息
    first_img_path = os.path.join(comic_dir1, images1[0])
    from PIL import Image
    img = Image.open(first_img_path)
    print(f"第一张图片尺寸: {img.size}, 模式: {img.mode}")
else:
    print("目录不存在")

# 测试2: 禁用decode=False
print("\n=== 测试2: 下载漫画1323910, decode=False ===")
test_dir2 = r"D:\code\JMComic-Crawler-Python\test\pictures\test_jmcomic_nodecode"
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
    
    # 打印第一张图片的详细信息
    first_img_path2 = os.path.join(comic_dir2, images2[0])
    img2 = Image.open(first_img_path2)
    print(f"第一张图片尺寸: {img2.size}, 模式: {img2.mode}")
else:
    print("目录不存在")

print("\n=== 测试完成 ===")
print(f"\n结果目录:")
print(f"解密: {test_dir}")
print(f"不解密: {test_dir2}")
