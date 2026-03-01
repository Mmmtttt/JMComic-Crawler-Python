# JMComic API 测试文档

## 测试文件说明

`test_api.py` 是JMComic API的综合测试文件，包含以下测试内容：

| 测试函数 | 测试内容 | 所在行 |
|---------|---------|-------|
| `test_load_config()` | 测试配置加载 | 第50行 |
| `test_get_client()` | 测试客户端初始化 | 第65行 |
| `test_get_option()` | 测试配置选项 | 第75行 |
| `test_get_album_detail()` | 测试获取漫画详情 | 第85行 |
| `test_download_album()` | 测试漫画下载功能 | 第100行 |
| `test_get_total_pages()` | 测试获取网络端图片总数 | 第150行 |
| `test_get_local_progress()` | 测试获取本地下载进度 | 第160行 |
| `test_search_comics()` | 测试漫画搜索功能 | 第170行 |
| `test_search_comics_range()` | 测试范围搜索功能 | 第190行 |
| `test_get_favorite_comics()` | 测试获取收藏漫画 | 第210行 |
| `test_database_operations()` | 测试数据库操作 | 第230行 |
| `test_progress_operations()` | 测试下载进度保存 | 第250行 |
| `test_utils_functions()` | 测试工具函数 | 第270行 |
| `test_image_decoding()` | 测试图片解密功能 | 第300行 |
| `test_batch_download()` | 测试批量下载功能 | 第320行 |

## 测试结果

### 最新测试结果（2026-03-01）
- ✅ 通过: 14项
- ❌ 失败: 1项（收藏功能需要登录）

### 失败说明
- `test_get_favorite_comics()`: 需要登录JMComic账号才能访问收藏功能

## 运行测试

```bash
# 运行所有测试
python test/test_api.py

# 运行特定测试
python test/test_api.py -k "test_image_decoding"
```

## 测试环境

- Python 3.13.5
- JMComic库版本: 最新版
- 依赖库: requests, pillow, jmcomic

## 注意事项

1. 测试会自动下载漫画到 `test/pictures` 目录
2. 测试数据会保存在 `test/test_database.json` 和 `test/test_progress.json`
3. 收藏功能测试需要配置用户名和密码
4. 图片解密功能测试包含算法验证