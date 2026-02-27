# JMComic-Crawler-Python 脚本使用说明

## 目录结构

```
JMComic-Crawler-Python/
├── config.json                    # 统一配置文件
├── comics_database.json           # 漫画数据库
├── download_progress.json         # 下载进度记录
├── favorite_comics.txt            # 收藏漫画ID列表
├── search_result.json             # 搜索结果
├── temp/                          # 临时文件夹
│   └── search_ids.txt             # 搜索结果ID
├── pictures/                      # 下载的漫画图片
├── lib/                           # 核心库文件
│   └── src/jmcomic/               # jmcomic库源码
│
├── get_comic_detail_and_download.py   # 获取单个漫画详情并下载
├── get_favorite_comics.py             # 获取用户收藏的漫画ID
├── batch_download_comics.py           # 批量下载漫画
├── update_database_pages.py           # 更新数据库页数
├── sync_favorites_and_download.py     # 同步收藏夹并下载新漫画
└── search_comics.py                   # 搜索漫画并获取详细信息
```

---

## 配置文件 (config.json)

所有脚本统一从 `config.json` 读取配置：

```json
{
    "username": "your_username",           # 禁漫账号用户名
    "password": "your_password",           # 禁漫账号密码
    "download_dir": "pictures",            # 下载目录
    "output_json": "comics_database.json", # 数据库文件路径
    "progress_file": "download_progress.json", # 进度文件路径
    "favorite_list_file": "favorite_comics.txt", # 收藏ID列表文件
    "consecutive_hit_threshold": 10,       # 连续命中阈值
    "collection_name": "我的最爱"           # 收藏夹名称
}
```

---

## 脚本详细说明

### 1. get_comic_detail_and_download.py

**用途**: 获取单个漫画的详情信息并下载

**用法**: 直接运行，修改脚本中的 `comic_id` 变量

```bash
python get_comic_detail_and_download.py
```

**示例输出**:
```
漫画详情信息:
ID: 542774
标题: [漫画标题]
作者: [作者名]
章节数: 1
总页数: 30
关键词: ['标签1', '标签2']

章节信息:
章节 1: [章节名] (ID: 542774, 图片数: 30)

下载成功！
所有图片已下载完成，共 30 张图片
```

**注意事项**:
- 需要手动修改脚本中的 `comic_id` 变量来指定要下载的漫画
- 下载的图片保存在 `pictures/[漫画ID]/` 目录下

---

### 2. get_favorite_comics.py

**用途**: 获取用户收藏夹中的所有漫画ID，保存到文件

**用法**: 
```bash
python get_favorite_comics.py
```

**输出文件**: `favorite_comics.txt`（每行一个漫画ID）

**示例输出**:
```
正在登录...
登录成功！
正在获取收藏夹...
共收藏了 598 本漫画
正在获取第 2 页...
正在获取第 3 页...
...

收藏的漫画ID列表:
1. 1024707
2. 427136
3. 449314
...

漫画ID已保存到 favorite_comics.txt 文件中
共获取到 598 个漫画ID
```

**注意事项**:
- 需要在 `config.json` 中配置正确的用户名和密码
- 获取的ID列表供 `batch_download_comics.py` 使用

---

### 3. batch_download_comics.py

**用途**: 批量下载 `favorite_comics.txt` 中的所有漫画

**用法**: 
```bash
python batch_download_comics.py
```

**功能特性**:
- 从数据库检查下载进度，跳过已完成的漫画
- 支持断点续传
- 维护下载进度记录
- 自动更新数据库信息

**示例输出**:
```
共找到 599 个漫画ID

初始下载进度:
总漫画数: 599
已下载漫画: 0
下载中漫画: 599
未下载漫画: 0
已下载图片: 42068

[1/599] 漫画 1024707 已下载完成，跳过
[2/599] 漫画 427136 已下载完成，跳过
[3/599] 正在获取漫画 449314 的信息...
  正在下载漫画 449314...
  开始下载，已完成 0/16 张图片
...
```

**输出文件**:
- `pictures/[漫画ID]/` - 下载的图片
- `comics_database.json` - 漫画信息数据库
- `download_progress.json` - 下载进度记录

---

### 4. update_database_pages.py

**用途**: 更新数据库中漫画的总页数

**用法**: 
```bash
# 简单模式（默认）：以本地已下载的图片数量为准
python update_database_pages.py

# 精确模式：从网页获取实际页数
python update_database_pages.py --mode precise
```

**参数说明**:
| 参数 | 说明 |
|------|------|
| `--mode` | 更新模式：`simple`（默认）或 `precise` |

**模式区别**:
- **simple**: 统计本地已下载的图片数量，更新数据库
- **precise**: 从网页获取漫画的实际页数，更精确但速度较慢

**示例输出**:
```
加载数据库: comics_database.json
数据库中共有 600 个漫画

模式: simple（以本地下载数量为准）

[1/600] 漫画 1024707: 本地 199 张，数据库 199 张，无需更新
[2/600] 漫画 427136: 本地 172 张，数据库 172 张，无需更新
...

更新完成！
共更新了 5 个漫画的页数
```

---

### 5. sync_favorites_and_download.py

**用途**: 同步收藏夹并下载新漫画（整合了获取收藏和下载功能）

**用法**: 
```bash
# 使用配置文件中的账号密码
python sync_favorites_and_download.py

# 命令行指定账号密码
python sync_favorites_and_download.py --username "用户名" --password "密码"

# 指定连续命中阈值
python sync_favorites_and_download.py --threshold 15
```

**参数说明**:
| 参数 | 说明 |
|------|------|
| `--username` | 用户名（默认从配置文件读取） |
| `--password` | 密码（默认从配置文件读取） |
| `--threshold` | 连续命中阈值（默认10） |

**功能特性**:
- 获取用户收藏夹中的所有漫画ID
- 在数据库中查找，跳过已存在的漫画
- **连续命中检测**: 如果连续N个漫画ID都在数据库中找到，则提前终止检索
- 只下载数据库中不存在的新漫画

**示例输出**:
```
============================================================
同步收藏夹并下载新漫画
用户: mt1511318385
连续命中阈值: 10
============================================================

数据库中已有 600 个漫画记录
正在获取用户 mt1511318385 的收藏夹...
正在登录...
登录成功！
正在获取收藏夹...
共收藏了 598 本漫画

开始检查漫画ID...
策略: 连续 10 个漫画ID在数据库中找到则终止检索

[1/598] 漫画 1024707 在数据库中找到 (连续命中: 1/10)
[2/598] 漫画 427136 在数据库中找到 (连续命中: 2/10)
...
[10/598] 漫画 1215258 在数据库中找到 (连续命中: 10/10)

连续 10 个漫画ID都在数据库中找到，终止检索
跳过剩余 588 个漫画

============================================================
同步完成！
原有漫画: 600
新增漫画: 0
跳过漫画: 0
失败漫画: 0
============================================================
```

---

### 6. search_comics.py

**用途**: 在禁漫网站搜索漫画，获取搜索结果的详细信息

**用法**: 
```bash
# 基本搜索
python search_comics.py "关键词"

# 限制搜索页数
python search_comics.py "砂漠" --max-pages 2

# 只保存ID，不获取详细信息
python search_comics.py "砂漠" --skip-detail

# 精确获取页数（较慢）
python search_comics.py "砂漠" --precise-pages

# 指定输出文件
python search_comics.py "砂漠" --output my_search.json

# 交互式输入关键词
python search_comics.py
```

**参数说明**:
| 参数 | 说明 |
|------|------|
| `query` | 搜索关键词（必填，或交互输入） |
| `--max-pages` | 最大搜索页数（默认获取所有结果） |
| `--output` | 输出文件路径（默认 search_result.json） |
| `--temp` | 临时ID文件路径（默认 temp/search_ids.txt） |
| `--skip-detail` | 只保存ID，不获取详细信息 |
| `--precise-pages` | 精确获取页数（较慢，需获取每个章节详情） |

**输出文件**:
- `temp/search_ids.txt` - 搜索结果的漫画ID列表（每行一个ID）
- `search_result.json` - 详细信息，格式与数据库一致

**示例输出**:
```
正在登录...
登录成功！

正在搜索: 砂漠
正在获取第 1 页...
第 1 页: 获取到 77 个结果
已到达最后一页 (1 页)

共搜索到 77 个漫画
搜索结果ID已保存到: temp/search_ids.txt

正在获取漫画详细信息...
[1/77] 获取漫画 1190059 详情...
[2/77] 获取漫画 1250038 详情...
...

搜索结果已保存到: search_result.json
```

**search_result.json 格式**:
```json
{
  "search_query": "砂漠",
  "total_results": 77,
  "search_time": "2026-02-28 03:07:08",
  "albums": [
    {
      "album_id": "1190059",
      "title": "石庭酱与我-我与小石庭 全集无修正版...",
      "author": "砂漠",
      "pages": 0,
      "tags": ["纯爱", "单行本", ...],
      ...
    }
  ]
}
```

---

## 工作流程推荐

### 日常同步收藏夹
```bash
# 一键同步收藏夹并下载新漫画
python sync_favorites_and_download.py
```

### 首次使用/完整下载
```bash
# 1. 获取收藏的漫画ID
python get_favorite_comics.py

# 2. 批量下载所有漫画
python batch_download_comics.py

# 3. 更新数据库页数（可选）
python update_database_pages.py --mode precise
```

### 搜索并下载特定漫画
```bash
# 1. 搜索漫画
python search_comics.py "作者名或关键词"

# 2. 查看搜索结果
# 编辑 temp/search_ids.txt，保留想要下载的ID

# 3. 将ID添加到下载列表
# 将 temp/search_ids.txt 中的ID追加到 favorite_comics.txt

# 4. 批量下载
python batch_download_comics.py
```

---

## 常见问题

### Q: 登录失败怎么办？
A: 检查 `config.json` 中的用户名和密码是否正确。部分脚本支持通过命令行参数指定账号密码。

### Q: 下载中断了怎么办？
A: 重新运行 `batch_download_comics.py`，脚本会自动跳过已下载的漫画，从中断处继续。

### Q: 如何查看下载进度？
A: 查看 `download_progress.json` 文件，或运行 `update_database_pages.py` 查看统计信息。

### Q: 搜索结果的页数为什么是0？
A: 网页解析问题导致。使用 `--precise-pages` 参数可以获取精确页数，但速度较慢。

### Q: 连续命中阈值是什么意思？
A: 在 `sync_favorites_and_download.py` 中，如果连续N个漫画ID都在数据库中找到，则认为后面的漫画也都在数据库中，提前终止检索以节省时间。
