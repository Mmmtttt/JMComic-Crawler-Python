from __future__ import annotations

import os
import sys
from io import BytesIO
from typing import Any, Dict, List

import requests
from PIL import Image


CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
THIRD_PARTY_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
BACKEND_ROOT = os.path.abspath(os.path.join(THIRD_PARTY_ROOT, ".."))
LIB_DIR = os.path.join(CURRENT_DIR, "lib")
LIB_SRC_DIR = os.path.join(LIB_DIR, "src")
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)
if LIB_SRC_DIR not in sys.path:
    sys.path.insert(0, LIB_SRC_DIR)

from infrastructure.logger import error_logger
from protocol.base import ProtocolProvider
from third_party.credential_guard import get_adapter_credential_status

from jmcomic_api import (
    download_album as jm_download_album,
    get_album_detail,
    get_client,
    get_favorite_comics,
    get_favorite_comics_full,
    search_comics,
    search_comics_full,
)


class JMComicProvider(ProtocolProvider):
    ADAPTER_NAME = "jmcomic"
    FAVORITES_LIST_ID = "favorites"

    def normalize_config(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(payload or {})
        normalized.setdefault("enabled", True)
        normalized.setdefault("config_path", "JMComic-Crawler-Python/config.json")
        return normalized

    def get_query_status(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return get_adapter_credential_status(self.ADAPTER_NAME, config)

    @staticmethod
    def _get_login_credentials(config: Dict[str, Any]) -> tuple[str, str]:
        username = str((config or {}).get("username") or "").strip()
        password = str((config or {}).get("password") or "").strip()
        return username, password

    def _ensure_query_ready(self, config: Dict[str, Any]) -> tuple[str, str]:
        status = self.get_query_status(config)
        if not bool(status.get("configured", False)):
            raise RuntimeError(str(status.get("message") or "JM 平台未配置账号或密码，不能使用该平台查询。"))
        return self._get_login_credentials(config)

    def _get_search_client(self, config: Dict[str, Any]):
        username, password = self._ensure_query_ready(config)
        try:
            return get_client(username=username, password=password), username
        except Exception as exc:
            raise RuntimeError("JM API 登录失败，无法执行登录态搜索。请检查账号密码或网络后重试。") from exc

    @staticmethod
    def _convert_basic_to_meta_format(albums: List[Dict[str, Any]]) -> Dict[str, Any]:
        converted_albums = []
        for album in albums:
            album_id = album.get("album_id", 0)
            raw_author = album.get("author", "")
            if isinstance(raw_author, list):
                author = ""
                for item in raw_author:
                    text = str(item or "").strip()
                    if text:
                        author = text
                        break
            else:
                author = str(raw_author or "").strip()

            raw_tags = album.get("tags", [])
            tags = raw_tags if isinstance(raw_tags, list) else []

            converted_albums.append(
                {
                    "rank": album.get("rank", 0),
                    "album_id": album_id,
                    "title": album.get("title", ""),
                    "title_jp": "",
                    "author": author,
                    "pages": 0,
                    "cover_url": f"https://cdn-msp3.18comic.vip/media/albums/{album_id}.jpg",
                    "album_url": "",
                    "tags": tags,
                    "category_tags": [],
                    "upload_date": "0",
                    "update_date": "0",
                }
            )

        return {
            "total": len(converted_albums),
            "albums": converted_albums,
        }

    @staticmethod
    def _convert_to_meta_format(albums: List[Dict[str, Any]], username: str = "") -> Dict[str, Any]:
        converted_albums = []
        for album in albums:
            converted_albums.append(
                {
                    "rank": album.get("rank", 0),
                    "album_id": album.get("album_id", 0),
                    "title": album.get("title", ""),
                    "title_jp": album.get("title_jp", ""),
                    "author": album.get("author", ""),
                    "pages": album.get("pages", 0),
                    "cover_url": album.get("cover_url", ""),
                    "album_url": album.get("album_url", ""),
                    "tags": album.get("tags", []),
                    "category_tags": album.get("category_tags", []),
                    "upload_date": album.get("upload_date", "0"),
                    "update_date": album.get("update_date", "0"),
                }
            )

        return {
            "collection_name": "JMComic 导入",
            "user": username,
            "total_favorites": len(converted_albums),
            "last_updated": "",
            "albums": converted_albums,
        }

    def _search(self, config: Dict[str, Any], keyword: str, page: int, max_pages: int, fast_mode: bool) -> Dict[str, Any]:
        client, username = self._get_search_client(config)
        if fast_mode:
            result = search_comics(
                keyword,
                page=page,
                max_pages=max_pages,
                client=client,
                enable_query_fallback=False,
            )
            albums = result.get("results", [])
            total_pages = result.get("page_count")
            has_next = page < total_pages if total_pages else len(albums) > 0
            converted = self._convert_basic_to_meta_format(albums)
            return {
                "page": page,
                "has_next": has_next,
                "total_pages": total_pages,
                "albums": converted.get("albums", []),
                "collection_name": "JMComic 导入",
                "user": username,
                "total_favorites": len(albums),
                "last_updated": "",
            }

        result = search_comics_full(
            keyword,
            page=page,
            max_pages=max_pages,
            client=client,
            enable_query_fallback=False,
        )
        albums = result.get("results", [])
        total_pages = result.get("page_count")
        has_next = page < total_pages if total_pages else len(albums) > 0
        converted = self._convert_to_meta_format(albums, username=username)
        return {
            "page": page,
            "has_next": has_next,
            "total_pages": total_pages,
            "albums": converted.get("albums", []),
            "collection_name": converted.get("collection_name", "JMComic 导入"),
            "user": converted.get("user", username),
            "total_favorites": converted.get("total_favorites", len(albums)),
            "last_updated": converted.get("last_updated", ""),
        }

    def _get_album(self, config: Dict[str, Any], album_id: str) -> Dict[str, Any]:
        username, password = self._ensure_query_ready(config)
        detail = get_album_detail(int(album_id), client=get_client(username=username, password=password))
        return self._convert_to_meta_format([detail], username=username)

    def _get_favorites_basic(self, config: Dict[str, Any]) -> Dict[str, Any]:
        username, password = self._ensure_query_ready(config)
        get_client(username=username, password=password)
        result = get_favorite_comics(username=username, password=password)
        basic_albums = result.get("comics", [])
        converted = self._convert_basic_to_meta_format(basic_albums)
        return {
            "collection_name": "JMComic 导入",
            "user": username,
            "total_favorites": converted.get("total", len(converted.get("albums", []))),
            "last_updated": "",
            "albums": converted.get("albums", []),
        }

    def _get_favorites(self, config: Dict[str, Any]) -> Dict[str, Any]:
        username, password = self._ensure_query_ready(config)
        get_client(username=username, password=password)
        result = get_favorite_comics_full(username=username, password=password)
        albums = result.get("comics", [])
        return self._convert_to_meta_format(albums, username=username)

    @staticmethod
    def _build_favorites_list_payload(total: int = 0) -> Dict[str, Any]:
        return {
            "lists": [
                {
                    "list_id": JMComicProvider.FAVORITES_LIST_ID,
                    "list_name": "我的收藏",
                    "list_desc": "平台收藏夹中的所有漫画",
                    "total": int(total or 0),
                }
            ]
        }

    def _get_user_lists(self, config: Dict[str, Any]) -> Dict[str, Any]:
        try:
            favorites = self._get_favorites_basic(config)
            total = favorites.get("total_favorites", len(favorites.get("albums", [])))
        except Exception:
            total = 0
        return self._build_favorites_list_payload(total=total)

    def _get_list_detail(self, config: Dict[str, Any], list_id: str) -> Dict[str, Any]:
        if str(list_id or "").strip() != self.FAVORITES_LIST_ID:
            raise ValueError(f"unsupported JM list: {list_id}")
        favorites = self._get_favorites_basic(config)
        return {
            "list_id": self.FAVORITES_LIST_ID,
            "list_name": "我的收藏",
            "list_desc": "平台收藏夹中的所有漫画",
            "total": len(favorites.get("albums", [])),
            "albums": favorites.get("albums", []),
        }

    @staticmethod
    def _get_cover_url(album_id: str) -> str:
        return f"https://cdn-msp3.18comic.vip/media/albums/{album_id}.jpg"

    @staticmethod
    def _get_image_url(album_id: str, page: int) -> str:
        return f"https://cdn-msp.jmapinodeudzn.net/media/photos/{album_id}/{page:05d}.webp"

    def execute(self, capability: str, params: Dict[str, Any], context: Dict[str, Any], config: Dict[str, Any]):
        if capability == "storage.comic_dir.resolve":
            base_dir = str(params.get("base_dir") or "").strip()
            album_id = str(params.get("album_id") or "").strip()
            return os.path.join(base_dir, album_id) if base_dir else album_id

        if capability == "asset.preview.resolve":
            preview_urls: List[str] = []
            for page in list(params.get("preview_pages") or []):
                try:
                    page_num = int(page or 0)
                except Exception:
                    continue
                if page_num <= 0:
                    continue
                preview_urls.append(self._get_image_url(str(params.get("album_id") or ""), page_num))
            return preview_urls

        if capability == "health.query.status":
            return self.get_query_status(config)

        if capability == "catalog.search":
            return self._search(
                config,
                keyword=str(params.get("keyword") or ""),
                page=int(params.get("page", 1) or 1),
                max_pages=int(params.get("max_pages", 1) or 1),
                fast_mode=bool(params.get("fast_mode", False)),
            )

        if capability == "catalog.detail":
            return self._get_album(config, str(params.get("album_id") or ""))

        if capability == "collection.favorites":
            return self._get_favorites(config)

        if capability == "collection.favorites_basic":
            return self._get_favorites_basic(config)

        if capability == "collection.list":
            return self._get_user_lists(config)

        if capability == "collection.detail":
            return self._get_list_detail(config, str(params.get("list_id") or ""))

        if capability == "asset.bundle.fetch":
            try:
                detail, success = jm_download_album(
                    int(str(params.get("album_id") or "0") or 0),
                    download_dir=str(params.get("download_dir") or ""),
                    show_progress=bool(params.get("show_progress", False)),
                    decode_images=bool((params.get("extra") or {}).get("decode_images", True)),
                )
                return {"detail": detail, "success": bool(success)}
            except Exception as exc:
                error_logger.error(f"下载 JM 漫画失败: {params.get('album_id')}, {exc}")
                return {"detail": {}, "success": False}

        if capability == "asset.cover.fetch":
            album_id = str(params.get("album_id") or "").strip()
            save_path = str(params.get("save_path") or "").strip()
            cover_url = self._get_cover_url(album_id)
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                }
                response = requests.get(cover_url, headers=headers, timeout=30)
                response.raise_for_status()
                with Image.open(BytesIO(response.content)) as image:
                    if image.mode in ("RGBA", "P"):
                        image = image.convert("RGB")
                    image.save(save_path, "JPEG", quality=95)
                return {"detail": {"cover_url": cover_url, "save_path": save_path}, "success": True}
            except Exception as exc:
                error_logger.error(f"下载 JM 封面失败: {album_id}, {exc}")
                return {"detail": {}, "success": False}

        raise ValueError(f"unsupported capability: {capability}")
