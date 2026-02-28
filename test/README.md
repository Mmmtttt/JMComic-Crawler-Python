# JMComic API 测试说明

## 测试文件

- `test_api.py` - 主测试脚本

## 运行测试

```bash
python test/test_api.py
```

## 测试的API接口

### jmcomic_api 模块

| API函数 | 测试函数 | 行号 | 说明 |
|---------|----------|------|------|
| `load_config()` | `test_load_config()` | 第62-70行 | 加载配置文件，验证返回字段 |
| `get_client()` | `test_get_client()` | 第72-77行 | 获取JMComic客户端 |
| `get_option()` | `test_get_option()` | 第79-84行 | 获取配置选项 |
| `get_album_detail()` | `test_get_album_detail()` | 第86-105行 | 获取漫画详情，验证返回字段完整性 |
| `download_album()` | `test_download_album()` | 第107-132行 | 下载漫画，验证下载结果、本地图片数和网络端图片总数 |
| `get_total_pages()` | `test_get_total_pages()` | 第134-145行 | 获取网络端图片总数 |
| `get_local_progress()` | `test_get_local_progress()` | 第147-152行 | 获取本地已下载图片数量 |
| `search_comics()` | `test_search_comics()` | 第154-174行 | 搜索漫画，验证返回格式 |
| `load_database()` | `test_database_operations()` | 第176-196行 | 加载数据库 |
| `add_to_database()` | `test_database_operations()` | 第176-196行 | 添加漫画到数据库 |
| `load_progress()` | `test_progress_operations()` | 第198-216行 | 加载下载进度 |
| `save_progress()` | `test_progress_operations()` | 第198-216行 | 保存下载进度 |
| `batch_download()` | `test_batch_download()` | 第238-258行 | 批量下载漫画 |

### utils 模块

| API函数 | 测试函数 | 行号 | 说明 |
|---------|----------|------|------|
| `get_download_stats()` | `test_utils_functions()` | 第218-237行 | 获取下载统计信息 |
| `format_file_size()` | `test_utils_functions()` | 第218-237行 | 格式化文件大小 |
| `parse_album_ids()` | `test_utils_functions()` | 第218-237行 | 解析漫画ID字符串 |
| `validate_album_id()` | `test_utils_functions()` | 第218-237行 | 验证漫画ID有效性 |

## 测试用例详情

### 1. load_config() - 第62-70行
- 验证配置文件加载
- 检查必要字段：`download_dir`, `output_json`

### 2. get_client() - 第72-77行
- 创建JMComic客户端
- 自动登录（使用配置文件中的账号密码）

### 3. get_option() - 第79-84行
- 获取JMComic配置选项对象

### 4. get_album_detail() - 第86-105行
- 测试漫画ID: 542774
- 验证返回字段：
  - `album_id` - 漫画ID
  - `title` - 标题
  - `author` - 作者
  - `pages` - 页数
  - `tags` - 标签
  - `cover_url` - 封面URL
  - `album_url` - 漫画URL

### 5. download_album() - 第107-132行
- 下载指定漫画到测试目录
- 验证下载成功状态
- 验证本地图片数量
- 验证网络端图片总数（`total_pages`字段）
- 测试进度回调功能（`progress_callback`参数）
- 显示下载进度：`下载完成: 34/34 张图片`
- 进度回调记录数应等于图片总数

### 6. get_total_pages() - 第134-145行
- 获取漫画的网络端图片总数
- 通过遍历所有章节获取准确的图片总数
- 验证返回值大于0

### 7. get_local_progress() - 第147-152行
- 统计本地已下载的图片数量

### 8. search_comics() - 第154-174行
- 搜索关键词: "砂漠"
- 验证返回字段：
  - `query` - 搜索关键词
  - `total` - 总结果数
  - `results` - 结果列表

### 9. 数据库操作 - 第176-196行
- `load_database()` - 加载数据库
- `add_to_database()` - 添加漫画到数据库
- 验证漫画是否正确添加

### 10. 进度操作 - 第198-216行
- `load_progress()` - 加载进度文件
- `save_progress()` - 保存进度文件
- 验证进度数据读写

### 11. 工具函数 - 第218-237行
- `get_download_stats()` - 获取下载统计
- `format_file_size()` - 格式化 100MB -> "100.00 MB"
- `parse_album_ids()` - 解析 "123456,789012,123460-123462"
- `validate_album_id()` - 验证ID有效性

### 12. batch_download() - 第238-258行
- 批量下载测试
- 验证返回统计：
  - `total` - 总数
  - `success` - 成功数
  - `skipped` - 跳过数
  - `failed` - 失败数

## 测试输出文件

测试过程中生成的文件（位于test目录）：

| 文件 | 说明 |
|------|------|
| `pictures/` | 测试下载的漫画图片 |
| `test_database.json` | 测试数据库文件 |
| `test_progress.json` | 测试进度文件 |
| `test_config.json` | 测试配置文件 |

## 预期输出

```
============================================================
测试结果汇总
============================================================
load_config: ✅ 通过
get_client: ✅ 通过
get_option: ✅ 通过
get_album_detail: ✅ 通过
download_album: ✅ 通过
get_total_pages: ✅ 通过
get_local_progress: ✅ 通过
search_comics: ✅ 通过
database_operations: ✅ 通过
progress_operations: ✅ 通过
utils_functions: ✅ 通过
batch_download: ✅ 通过

总计: 12 通过, 0 失败
============================================================
```
