import jmcomic

# 登录信息（需要用户填写）
username = "mt1511318385"
password = "mtly2001"

# 创建默认配置
option = jmcomic.JmModuleConfig.option_class().default()

# 构建客户端
client = option.build_jm_client()

try:
    # 登录
    print("正在登录...")
    client.login(username, password)
    print("登录成功！")
    
    # 获取收藏夹
    print("正在获取收藏夹...")
    favorite_page = client.favorite_folder(page=1, order_by=jmcomic.JmMagicConstants.ORDER_BY_LATEST, folder_id='0')
    
    # 打印收藏的漫画数量
    print(f"共收藏了 {favorite_page.total} 本漫画")
    
    # 存储所有漫画ID
    comic_ids = []
    
    # 遍历第一页的漫画
    for album_id, album_info in favorite_page.content:
        comic_ids.append(album_id)
    
    # 如果有更多页，继续获取
    if favorite_page.page_count > 1:
        for page in range(2, favorite_page.page_count + 1):
            print(f"正在获取第 {page} 页...")
            page_result = client.favorite_folder(page=page, order_by=jmcomic.JmMagicConstants.ORDER_BY_LATEST, folder_id='0')
            for album_id, album_info in page_result.content:
                comic_ids.append(album_id)
    
    # 打印所有漫画ID
    print("\n收藏的漫画ID列表:")
    for i, comic_id in enumerate(comic_ids, 1):
        print(f"{i}. {comic_id}")
    
    # 将漫画ID保存到文件
    with open('favorite_comics.txt', 'w', encoding='utf-8') as f:
        for comic_id in comic_ids:
            f.write(f"{comic_id}\n")
    
    print("\n漫画ID已保存到 favorite_comics.txt 文件中")
    
    print(f"\n共获取到 {len(comic_ids)} 个漫画ID")
    
except Exception as e:
    print(f"错误: {e}")
finally:
    # 清理资源
    if 'client' in locals():
        del client
