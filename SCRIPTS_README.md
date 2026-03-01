# JMComic-Crawler-Python API (v2.0)

JM漫画获取 API，支持漫画搜索、下载、收藏管理等功能。本API为jmcomic库的封装，提供了更方便的使用方式。

## 版本历史

- **v2.0 (2026-03-02)**: 新增图片解密功能
  - 新增 `JmImageTool` 图片解密工具类
  - 新增 `get_scramble_id()` 获取漫画scramble_id
  - `download_album()` 新增 `decode_images` 参数控制图片解密
  - `batch_download()` 新增 `decode_images` 和 `download_dir` 参数
  - 修复scramble_id获取逻辑（使用photo_id获取）

## 功能特性

- **漫画详情抓取**：标题、作者、标签、页数、封面等
- **漫画下载**：支持单漫画下载、批量下载、断点续传、自动图片解密
- **收藏管理**：获取收藏夹、同步收藏、智能检测新漫画
- **搜索功能**：关键词搜索、获取详细信息、分页/范围搜索
- **数据库管理**：本地数据库存储、进度追踪
- **图片解密**：自动解密、手动解密API
- **API 接口**：模块化设计，可直接作为库使用

## 目录结构

```
JMComic-Crawler-Python/
├── config.json                    # 统一配置文件
├── jmcomic_api.py                 # 核心 API 模块 (v2.0)
├── utils.py                       # 工具函数模块
├── requirements.txt               # 依赖列表
├── comics_database.json           # 漫画数据库
├── download_progress.json         # 下载进度记录
├── favorite_comics.txt            # 收藏漫画ID列表
├── search_result.json             # 搜索结果
├── lib/                           # 核心库文件（jmcomic库源码备份）
│   └── src/jmcomic/
│
├── scripts/                       # 示例脚本目录
│   ├── get_comic_detail_and_download.py   # 获取单个漫画详情并下载
│   ├── get_favorite_comics.py             # 获取用户收藏的漫画ID
│   ├── batch_download_comics.py           # 批量下载漫画
│   ├── update_database_pages.py           # 更新数据库页数
│   ├── sync_favorites_and_download.py     # 同步收藏夹并下载新漫画
│   └── search_comics.py                   # 搜索漫画并获取详细信息
│
└── test/                          # 测试目录
    └── test_api.py                # API 测试脚本（包含所有功能测试）
```

## 安装

```bash
pip install -r requirements.txt
```

## 配置

编辑 `config.json` 填入你的账号信息：

```json
{
    "username": "your_username",
    "password": "your_password",
    "download_dir": "pictures",
    "output_json": "comics_database.json",
    "progress_file": "download_progress.json",
    "favorite_list_file": "favorite_comics.txt",
    "consecutive_hit_threshold": 10,
    "collection_name": "我的最爱"
}
```

---

## API 接口

### 基础接口

```python
from jmcomic_api import load_config, get_client, get_option

# 加载配置
config = load_config()
print(config['download_dir'])

# 获取客户端（自动登录）
client = get_client()

# 使用指定账号登录
client = get_client(username="user", password="pass")

# 获取配置选项
option = get_option()
```

### 漫画详情

```python
from jmcomic_api import get_album_detail

# 获取漫画详情
detail = get_album_detail(542774)
print(detail['title'])      # 标题
print(detail['author'])     # 作者
print(detail['pages'])      # 页数
print(detail['tags'])       # 标签
```

**输出格式**：
```json
{
  "album_id": 542774,
  "title": "",
  "author": "达磨さん转んだ",
  "pages": 34,
  "cover_url": "",
  "album_url": "",
  "tags": [],
  "upload_date": "2024-01-01",
  "update_date": "2024-01-15"
}
```

### 漫画下载

```python
from jmcomic_api import download_album, get_local_progress, get_total_pages

# 获取网络端图片总数
total = get_total_pages(542774)
print(f"网络端图片总数: {total}")

# 下载漫画（自动解密，默认decode_images=True）
detail, success = download_album(542774)
print(f"下载成功: {success}")
print(f"本地图片数: {detail['local_pages']}")
print(f"网络端图片总数: {detail['total_pages']}")

# 下载漫画不自动解密（保留原始混淆图片）
detail, success = download_album(542774, decode_images=False)

# 使用进度回调实时获取下载进度
def my_progress_callback(current, total, image_filename, status):
    print(f"下载进度: [{current}/{total}] {image_filename}")

detail, success = download_album(542774, progress_callback=my_progress_callback)

# 获取本地下载进度
local_count = get_local_progress(542774)
print(f"已下载 {local_count} 张图片")

# 指定下载目录
detail, success = download_album(542774, download_dir="my_comics")

# 关闭进度显示
detail, success = download_album(542774, show_progress=False)
```

**download_album 参数说明**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `album_id` | int/str | 必填 | 漫画ID |
| `download_dir` | str | config.json中的值 | 下载目录 |
| `client` | JmHtmlClient | None | JMComic客户端 |
| `show_progress` | bool | True | 是否显示进度 |
| `progress_callback` | callable | None | 进度回调函数 |
| `decode_images` | bool | True | 是否自动解密图片 |

**download_album 返回值**：
```python
{
    "album_id": 542774,
    "title": "漫画标题",
    "author": "作者",
    "pages": 34,           # 网络端页数
    "total_pages": 34,     # 网络端图片总数
    "local_pages": 34,     # 本地已下载图片数
    "downloaded": True,    # 是否下载成功
    # ... 其他字段
}
```

**进度回调参数**：
- `current`: 当前下载的图片序号
- `total`: 该章节的总图片数
- `image_filename`: 图片文件名
- `status`: 状态（"downloading"）

**下载进度输出示例**：
```
正在获取漫画 542774 的信息...
网络端图片总数: 34
开始下载漫画 542774...
下载完成: 34/34 张图片
```

### 图片解密功能 (v2.0新增)

JMComic网站的部分图片会进行混淆处理，本API已实现自动解密功能。

#### 自动解密

在`download_album`函数中，通过`decode_images`参数控制：

```python
from jmcomic_api import download_album

# 自动解密（默认）
detail, success = download_album("542774", decode_images=True)

# 不自动解密（保留原始混淆图片）
detail, success = download_album("542774", decode_images=False)
```

#### 手动解密API

如果需要手动解密图片，可以使用以下函数：

```python
from jmcomic_api import JmImageTool, get_scramble_id
from PIL import Image

# 方式1: 手动解密单张图片
img = Image.open("encrypted_image.jpg")
num = JmImageTool.get_num(scramble_id=220980, aid=542774, filename="00001")
JmImageTool.decode_and_save(num, img, "decrypted_image.jpg")

# 方式2: 获取真实scramble_id后解密
scramble_id = get_scramble_id(542774)  # 自动获取正确的scramble_id
num = JmImageTool.get_num(scramble_id, 542774, "00001")
JmImageTool.decode_and_save(num, img, "decrypted_image.jpg")
```

#### JmImageTool API

```python
from jmcomic_api import JmImageTool

# 打开图片
img = JmImageTool.open_image("image_path.jpg")

# 计算分割数
num = JmImageTool.get_num(scramble_id, aid, filename)
# 参数说明:
#   - scramble_id: 漫画的scramble_id（可通过get_scramble_id获取）
#   - aid: 漫画ID
#   - filename: 图片文件名（不含后缀），如 "00001"

# 根据URL计算分割数
num = JmImageTool.get_num_by_url(scramble_id, "https://.../photos/542774/00001.webp")

# 解密并保存
JmImageTool.decode_and_save(num, img, "output_path.jpg")

# 保存图片
JmImageTool.save_image(img, "save_path.jpg")
```

#### 注意事项

- 不同漫画的scramble_id可能不同，必须使用正确的scramble_id才能正确解密
- 每张图片的分割数可能不同，根据aid和filename通过MD5计算得出
- 如果无法获取scramble_id，会使用默认值220980
- **重要**：`filename`参数必须是**不含扩展名的纯文件名**，如 `"00001"` 而不是 `"00001.jpg"`

### 搜索功能

```python
from jmcomic_api import search_comics, search_comics_full

# 基础搜索（返回ID和标题）
result = search_comics("砂漠", max_pages=2)
print(f"共找到 {result['total']} 个结果")
for item in result['results']:
    print(f"{item['album_id']}: {item['title']}")

# 分页搜索（第3~5页）
result = search_comics("砂漠", page=3, max_pages=3)

# 范围搜索（指定个数，从第5个到第10个，索引从0开始）
result = search_comics("砂漠", start_index=5, end_index=10)

# 完整搜索（获取详细信息）
result = search_comics_full("砂漠", max_pages=1)
for album in result['results']:
    print(f"{album['album_id']}: {album['title']} ({album['pages']}页)")
```

**搜索结果格式**：
```json
{
  "query": "砂漠",
  "total": 77,
  "page_count": 3,
  "page_size": 30,
  "start_index": 5,
  "end_index": 10,
  "results": [
    {
      "album_id": 1190059,
      "title": "石庭酱与我-我与小石庭...",
      "author": "砂漠",
      "pages": 199,
      "tags": ["纯爱", "单行本", ...]
    }
  ]
}
```

**参数说明**：
| 参数 | 说明 |
|------|------|
| `query` | 搜索关键词 |
| `page` | 起始页码（从1开始） |
| `max_pages` | 最大页数（None表示获取所有） |
| `start_index` | 起始个数索引（从0开始，如5表示从第5个开始） |
| `end_index` | 结束个数索引（不包含，如10表示到第10个结束） |
| `total` | 搜索结果总数 |
| `page_count` | 总页数 |
| `page_size` | 每页数量 |

### 收藏管理

```python
from jmcomic_api import get_favorite_comics, get_favorite_comics_full

# 获取收藏列表（基础信息）
favorites = get_favorite_comics()
print(f"共收藏 {favorites['total']} 本漫画")

# 获取收藏列表（详细信息）
favorites = get_favorite_comics_full()
for album in favorites['comics']:
    print(f"{album['album_id']}: {album['title']}")
```

### 批量下载

```python
from jmcomic_api import batch_download

# 批量下载（自动解密）
album_ids = [542774, 1024707, 427136]
stats = batch_download(album_ids)
print(f"成功: {stats['success']}, 跳过: {stats['skipped']}, 失败: {stats['failed']}")

# 批量下载不自动解密
stats = batch_download(album_ids, decode_images=False)

# 指定下载目录
stats = batch_download(album_ids, download_dir="my_comics")

# 带进度回调
def on_progress(current, total, album_id, status):
    print(f"[{current}/{total}] {album_id}: {status}")

stats = batch_download(album_ids, progress_callback=on_progress)
```

**batch_download 参数说明**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `album_ids` | List | 必填 | 漫画ID列表 |
| `skip_existing` | bool | True | 是否跳过已下载的漫画 |
| `database` | Dict | None | 数据库对象 |
| `client` | JmHtmlClient | None | JMComic客户端 |
| `progress_callback` | callable | None | 进度回调函数 |
| `decode_images` | bool | True | 是否自动解密图片 |
| `download_dir` | str | config.json中的值 | 下载目录 |

### 同步收藏

```python
from jmcomic_api import sync_favorites

# 同步收藏并下载新漫画
result = sync_favorites(threshold=10, download=True)
print(f"新增: {result['new']}, 下载: {result['downloaded']}")

# 只检测新漫画，不下载
result = sync_favorites(download=False)
print(f"新增漫画: {result['new']}")
```

### 数据库操作

```python
from jmcomic_api import load_database, save_database, add_to_database

# 加载数据库
db = load_database()
print(f"数据库中有 {len(db['albums'])} 个漫画")

# 添加漫画到数据库
album_detail = get_album_detail(542774)
add_to_database(album_detail)

# 保存数据库
save_database(db)
```

---

## 工具函数

```python
from utils import (
    load_config, save_config,
    load_json_file, save_json_file,
    load_text_file, save_text_file,
    get_download_stats, print_download_stats,
    count_images, get_directory_size, format_file_size,
    parse_album_ids, validate_album_id
)

# 获取下载统计
stats = get_download_stats()
print(f"已下载 {stats['downloaded_albums']} 个漫画")
print(f"总大小 {stats['total_size_formatted']}")

# 打印下载统计
print_download_stats()

# 解析漫画ID
ids = parse_album_ids("123456,789012,123460-123470")
print(ids)  # [123456, 789012, 123460, 123461, ..., 123470]

# 验证漫画ID
valid = validate_album_id("123456")  # True
```

---

## 命令行脚本

### 1. get_comic_detail_and_download.py

获取单个漫画详情并下载。

```bash
python scripts/get_comic_detail_and_download.py
```

修改脚本中的 `comic_id` 变量指定漫画ID。

### 2. get_favorite_comics.py

获取用户收藏夹中的所有漫画ID。

```bash
python scripts/get_favorite_comics.py
```

输出文件：`favorite_comics.txt`

### 3. batch_download_comics.py

批量下载 `favorite_comics.txt` 中的所有漫画。

```bash
python scripts/batch_download_comics.py
```

功能：断点续传、进度追踪、自动更新数据库。

### 4. update_database_pages.py

更新数据库中漫画的总页数。

```bash
# 简单模式：以本地已下载数量为准
python scripts/update_database_pages.py

# 精确模式：从网页获取实际页数
python scripts/update_database_pages.py --mode precise
```

### 5. sync_favorites_and_download.py

同步收藏夹并下载新漫画。

```bash
# 使用配置文件中的账号
python scripts/sync_favorites_and_download.py

# 指定账号密码
python scripts/sync_favorites_and_download.py --username "user" --password "pass"

# 指定连续命中阈值
python scripts/sync_favorites_and_download.py --threshold 15
```

### 6. search_comics.py

搜索漫画并获取详细信息。

```bash
# 基本搜索
python scripts/search_comics.py "关键词"

# 限制搜索页数
python scripts/search_comics.py "砂漠" --max-pages 2

# 只保存ID
python scripts/search_comics.py "砂漠" --skip-detail

# 精确获取页数（较慢）
python scripts/search_comics.py "砂漠" --precise-pages

# 指定输出文件
python scripts/search_comics.py "砂漠" --output my_search.json
```

---

## 工作流程推荐

### 日常同步收藏夹
```bash
python scripts/sync_favorites_and_download.py
```

### 首次使用/完整下载
```bash
python scripts/get_favorite_comics.py
python scripts/batch_download_comics.py
python scripts/update_database_pages.py --mode precise
```

### 搜索并下载特定漫画
```bash
python scripts/search_comics.py "作者名"
# 编辑 temp/search_ids.txt
# 将ID追加到 favorite_comics.txt
python scripts/batch_download_comics.py
```

### 作为库使用
```python
from jmcomic_api import search_comics_full, download_album, add_to_database

# 搜索并下载
result = search_comics_full("砂漠", max_pages=1)
for album in result['results']:
    detail, success = download_album(album['album_id'])
    if success:
        add_to_database(detail)
```

## 运行脚本

所有脚本位于 `scripts/` 目录下：

```bash
# 获取漫画详情并下载
python scripts/get_comic_detail_and_download.py

# 搜索漫画
python scripts/search_comics.py --query "砂漠" --max-pages 1

# 获取收藏漫画
python scripts/get_favorite_comics.py

# 批量下载
python scripts/batch_download_comics.py

# 同步收藏并下载
python scripts/sync_favorites_and_download.py

# 更新数据库页数
python scripts/update_database_pages.py
```

## 测试

运行测试脚本：

```bash
python test/test_api.py
```

`test_api.py` 包含以下测试：
- `load_config` - 配置加载
- `get_client` - 客户端获取
- `get_option` - 配置选项获取
- `get_album_detail` - 漫画详情
- `download_album` - 漫画下载
- `get_total_pages` - 获取网络端图片总数
- `get_local_progress` - 获取本地下载进度
- `search_comics` - 搜索功能
- `search_comics_range` - 范围搜索
- `get_favorite_comics` - 获取收藏列表
- `database_operations` - 数据库操作
- `progress_operations` - 进度操作
- `utils_functions` - 工具函数
- `image_decoding` - 图片解密功能
- `batch_download` - 批量下载
- `download_original_image` - 下载原始图片并手动解密

---

## 常见问题

### Q: 登录失败怎么办？
A: 检查 `config.json` 中的用户名和密码是否正确。也可以通过代码传入：
```python
client = get_client(username="user", password="pass")
```

### Q: 下载中断了怎么办？
A: 重新运行 `batch_download_comics.py`，脚本会自动跳过已下载的漫画。

### Q: 如何查看下载进度？
```python
from utils import print_download_stats
print_download_stats()
```

### Q: 搜索结果的页数为什么是0？
A: 网页解析问题。使用 `--precise-pages` 参数或调用 `search_comics_full` 获取精确页数。

### Q: 连续命中阈值是什么意思？
A: 在 `sync_favorites` 中，如果连续N个漫画ID都在数据库中找到，则提前终止检索以节省时间。

### Q: 图片解密后还是乱的？
A: 
1. 确认使用的是正确的scramble_id（通过`get_scramble_id()`获取）
2. 确认分割数计算正确（每张图片的分割数可能不同）
3. 可以尝试下载不加密的图片测试：`download_album(id, decode_images=False)`，然后手动解密对比

### Q: decode_images参数有什么区别？
A: 
- `decode_images=True`（默认）：下载时自动解密
- `decode_images=False`：下载原始混淆图片，之后可用`JmImageTool`手动解密

---

## 输出格式

### 数据库格式 (comics_database.json)

```json
{
  "collection_name": "我的最爱",
  "user": "username",
  "total_favorites": 600,
  "last_updated": "2026-02-28",
  "albums": [
    {
      "rank": 1,
      "album_id": 1024707,
      "title": "",
      "author": "砂漠",
      "pages": 199,
      "cover_url": "",
      "album_url": "",
      "tags": [],
      "upload_date": "0",
      "update_date": "0"
    }
  ]
}
```

### 进度文件格式 (download_progress.json)

```json
{
  "1024707": {
    "status": "completed",
    "start_time": "2026-02-28 10:00:00",
    "end_time": "2026-02-28 10:05:00",
    "downloaded_images": 199,
    "total_images": 199
  },
  "427136": {
    "status": "downloading",
    "start_time": "2026-02-28 10:06:00",
    "downloaded_images": 50,
    "total_images": 172
  }
}
```

---

## 注意事项

- 请合理使用，避免频繁请求
- 下载的图片保存在 `pictures/[漫画ID]/` 目录
- 数据库文件会自动更新
- 支持断点续传，中断后可继续下载
- 图片解密功能默认开启，如需原始图片使用 `decode_images=False`
