# 测试目录

本目录包含 API 测试脚本。

## 文件说明

| 文件 | 说明 |
|------|------|
| `test_api.py` | 主要测试脚本，包含所有API功能测试 |
| `test_config.json` | 测试配置文件 |
| `README.md` | 本文件 |

## 运行测试

```bash
python test/test_api.py
```

## 测试内容

`test_api.py` 包含以下测试：
1. `load_config` - 配置加载
2. `get_client` - 客户端获取
3. `get_option` - 配置选项获取
4. `get_album_detail` - 漫画详情
5. `download_album` - 漫画下载
6. `get_total_pages` - 获取网络端图片总数
7. `get_local_progress` - 获取本地下载进度
8. `search_comics` - 搜索功能
9. `search_comics_range` - 范围搜索
10. `get_favorite_comics` - 获取收藏列表
11. `database_operations` - 数据库操作
12. `progress_operations` - 进度操作
13. `utils_functions` - 工具函数
14. `image_decoding` - 图片解密功能
15. `batch_download` - 批量下载
16. `download_original_image` - 下载原始图片并手动解密
