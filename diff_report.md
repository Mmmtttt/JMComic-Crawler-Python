## b8de7fb7c3df3d26bb9fdd04c236b1fdc9df1c48 vs 当前版本 jmcomic_api.py 修改内容

对比提交 b8de7fb7c3df3d26bb9fdd04c236b1fdc9df1c48，当前版本的修改如下：

---

### 新增代码（约70行）

#### 1. 新增导入（第8-14行）
```python
from PIL import Image
from io import BytesIO
import hashlib
```

#### 2. get_option() 函数修改（第82-85行）
```python
'image': {
    'decode': True,  # 新增：默认启用自动解密
    'suffix': '.jpg'
}
```

#### 3. get_scramble_id() 函数（第94-115行）
```python
def get_scramble_id(album_id: int or str, client: jmcomic.JmHtmlClient = None) -> str:
    """
    获取漫画的真实scramble_id
    """
    if client is None:
        client = get_client()
    
    album = client.get_album_detail(album_id)
    scramble_id = album.scramble_id
    
    if scramble_id is None or scramble_id == 0 or scramble_id == '':
        scramble_id = 220980
    
    return str(scramble_id)
```

#### 4. JmMagicConstants 类（第117-120行）
```python
class JmMagicConstants:
    """JMComic魔法常量"""
    SCRAMBLE_268850 = 268850
    SCRAMBLE_421926 = 421926
```

#### 5. JmImageTool 类（第122-227行）
包含图片解密工具方法：
- decode_and_save() - 解密图片并保存
- save_image() - 保存图片
- open_image() - 打开图片
- get_num() - 获取分割数
- get_num_by_url() - 通过URL获取分割数

#### 6. ProgressDownloader 类（第273-344行）
```python
class ProgressDownloader(jmcomic.JmDownloader):
    def __init__(self, option=None, progress_callback=None, decode_images=True):
        self.decode_images = decode_images
    
    def after_image(self, image, img_save_path):
        # 自动解密图片逻辑
```

#### 7. download_album() 函数修改
- 新增参数：`decode_images: bool = True`（第378行）
- 新增参数说明：`decode_images: 是否解密图片`（第388行）
- 新增配置传递（第417行）：`'decode': decode_images`
- 新增 ProgressDownloader 传递 decode_images（第430行）

---

### 影响范围

| 功能 | 影响 |
|------|------|
| download_album() | 新增 decode_images 参数控制自动解密 |
| get_scramble_id() | 新增API，可获取漫画的scramble_id |
| JmImageTool | 新增类，提供图片解密工具方法 |
| get_option() | 默认启用自动解密 |

---

### 总结

- 当前版本在 b8de7fb7c3df3d26bb9fdd04c236b1fdc9df1c48 基础上新增了约70行代码
- 主要是图片自动解密功能
- 向后兼容：默认 decode_images=True，与之前行为一致
