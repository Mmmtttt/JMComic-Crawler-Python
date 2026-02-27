import jmcomic
import json

# 测试配置
option_dict = {
    'download': {
        'dir': 'pictures',
        'image': {
            'suffix': '.jpg'
        }
    },
    'dir_rule': {
        'base_dir': 'pictures',
        'rule': 'Bd_Aid'
    }
}

option = jmcomic.JmOption.construct(option_dict)

print("配置对象创建成功")
print(f"下载目录: {option.download.dir}")
print(f"路径规则: {option.dir_rule}")
print(f"路径规则基础目录: {option.dir_rule.base_dir}")
print(f"路径规则规则: {option.dir_rule.rule_dsl}")

# 创建客户端测试
client = option.build_jm_client()
print(f"客户端创建成功: {client.client_key}")

# 测试获取漫画详情并查看路径
album = client.get_album_detail(1024707)
print(f"\n漫画ID: {album.album_id}")
print(f"漫画标题: {album.name}")
print(f"漫画作者: {album.author}")
print(f"漫画页数: {album.page_count}")

# 测试路径规则
photo = album[0]
save_dir = option.decide_image_save_dir(photo)
print(f"\n图片保存目录: {save_dir}")
