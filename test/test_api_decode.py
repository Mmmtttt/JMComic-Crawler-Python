"""
测试API的解混淆功能
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jmcomic_api import download_album, get_scramble_id, get_client, JmImageTool

# 测试目录
test_dir = r"D:\code\JMComic-Crawler-Python\test\pictures\test_api_decode"
os.makedirs(test_dir, exist_ok=True)

print(f"测试目录: {test_dir}")

# 获取客户端
client = get_client()

# 测试1: 下载漫画1312953（自动解密）
print("\n=== 测试1: API下载漫画1312953（自动解密）===")
detail1, success1 = download_album(
    1312953, 
    download_dir=test_dir, 
    client=client, 
    decode_images=True
)
print(f"下载成功: {success1}")
print(f"本地图片数: {detail1.get('local_pages', 0)}")

comic_dir1 = os.path.join(test_dir, "1312953")
if os.path.exists(comic_dir1):
    images1 = sorted(os.listdir(comic_dir1))
    print(f"图片数量: {len(images1)}")
    print(f"前3张: {images1[:3]}")

# 测试2: 下载漫画1323910（不解密）
print("\n=== 测试2: API下载漫画1323910（不解密）===")
detail2, success2 = download_album(
    1323910, 
    download_dir=test_dir, 
    client=client, 
    decode_images=False
)
print(f"下载成功: {success2}")
print(f"本地图片数: {detail2.get('local_pages', 0)}")

comic_dir2 = os.path.join(test_dir, "1323910")
if os.path.exists(comic_dir2):
    images2 = sorted(os.listdir(comic_dir2))
    print(f"图片数量: {len(images2)}")
    print(f"前3张: {images2[:3]}")

# 测试3: 手动解密1323910的图片
print("\n=== 测试3: 手动解密1323910的图片 ===")

# 获取scramble_id
scramble_id = get_scramble_id(1323910, client)
print(f"scramble_id: {scramble_id}")

# 选择第一张图片
if images2:
    test_image = images2[0]
    test_image_path = os.path.join(comic_dir2, test_image)
    print(f"\n原始图片: {test_image_path}")
    
    # 打开图片
    img = JmImageTool.open_image(test_image_path)
    print(f"图片尺寸: {img.size}, 模式: {img.mode}")
    
    # 计算分割数
    num = JmImageTool.get_num(scramble_id, 1323910, test_image)
    print(f"计算得到的分割数: {num}")
    
    if num > 0:
        # 解密并保存
        output_path = os.path.join(comic_dir2, f"{os.path.splitext(test_image)[0]}_decoded.jpg")
        JmImageTool.decode_and_save(num, img, output_path)
        print(f"解密成功: {output_path}")
    else:
        print("该图片不需要解密")

print("\n=== 测试完成 ===")
print(f"\n结果目录:")
print(f"- 1312953 (已解密): {comic_dir1}")
print(f"- 1323910 (原始+解密): {comic_dir2}")
