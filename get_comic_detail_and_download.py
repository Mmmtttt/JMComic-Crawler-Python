import jmcomic

# 漫画ID
comic_id = 542774

# 下载漫画并获取详情信息
album, downloader = jmcomic.download_album(comic_id)

# 打印漫画详情信息
print("漫画详情信息:")
print(f"ID: {album.id}")
print(f"标题: {album.name}")
print(f"作者: {album.author}")
print(f"章节数: {len(album)}")
print(f"总页数: {album.page_count}")
print(f"关键词: {album.tags}")

# 打印章节信息
print("\n章节信息:")
for i, photo in enumerate(album):
    print(f"章节 {i+1}: {photo.name} (ID: {photo.photo_id}, 图片数: {len(photo)})")

# 检查下载是否成功
if not downloader.has_download_failures:
    print("\n下载成功！")
    print(f"所有图片已下载完成，共 {sum(len(photo) for photo in album)} 张图片")
else:
    print("\n部分下载失败！")
    if downloader.download_failed_photo:
        print(f"失败的章节: {len(downloader.download_failed_photo)}")
    if downloader.download_failed_image:
        print(f"失败的图片: {len(downloader.download_failed_image)}")
