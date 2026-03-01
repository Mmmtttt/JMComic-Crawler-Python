"""
测试API的解混淆功能 - 逐张解密所有图片
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jmcomic_api import download_album, get_scramble_id, get_client, JmImageTool

# 测试目录
test_dir = r"D:\code\JMComic-Crawler-Python\test\pictures\test_api_decode_v2"
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

# 测试2: 下载漫画1323910（不解密）
print("\n=== 测试2: API下载漫画1323910（不解密）===")
detail2, success2 = download_album(
    1323910, 
    download_dir=test_dir, 
    client=client, 
    decode_images=False
)
print(f"下载成功: {success2}")

# 测试3: 手动解密1323910的所有图片
print("\n=== 测试3: 手动解密1323910的图片 ===")

scramble_id = get_scramble_id(1323910, client)
print(f"scramble_id: {scramble_id}")

comic_dir2 = os.path.join(test_dir, "1323910")
if os.path.exists(comic_dir2):
    images = sorted(os.listdir(comic_dir2))
    print(f"图片数量: {len(images)}")
    
    # 解密前3张图片
    for img_name in images[:3]:
        img_path = os.path.join(comic_dir2, img_name)
        
        # 提取文件名（不含后缀）
        filename = os.path.splitext(img_name)[0]
        
        # 计算分割数
        num = JmImageTool.get_num(scramble_id, 1323910, filename)
        
        print(f"\n{img_name}:")
        print(f"  分割数: {num}")
        
        # 打开图片
        img = JmImageTool.open_image(img_path)
        print(f"  尺寸: {img.size}")
        
        # 解密并保存
        output_path = os.path.join(comic_dir2, f"{filename}_decoded.jpg")
        JmImageTool.decode_and_save(num, img, output_path)
        print(f"  解密成功: {output_path}")

print("\n=== 测试完成 ===")
