from __future__ import annotations

import os
import sys
from typing import Any, Dict


CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
THIRD_PARTY_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
BACKEND_ROOT = os.path.abspath(os.path.join(THIRD_PARTY_ROOT, ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from protocol.base import ProtocolProvider
from third_party.adapter_factory import AdapterFactory
from third_party.credential_guard import ensure_adapter_query_ready, get_adapter_credential_status


class JMComicProvider(ProtocolProvider):
    ADAPTER_NAME = "jmcomic"

    def normalize_config(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(payload or {})
        normalized.setdefault("enabled", True)
        normalized.setdefault("config_path", "JMComic-Crawler-Python/config.json")
        return normalized

    def get_query_status(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return get_adapter_credential_status(self.ADAPTER_NAME, config)

    def _get_storage_client(self, config: Dict[str, Any]):
        return AdapterFactory.get_adapter(self.ADAPTER_NAME, dict(config or {}))

    def get_legacy_client(self, config: Dict[str, Any], *args, **kwargs):
        ensure_adapter_query_ready(self.ADAPTER_NAME, config)
        return AdapterFactory.get_adapter(self.ADAPTER_NAME, dict(config or {}))

    def execute(self, capability: str, params: Dict[str, Any], context: Dict[str, Any], config: Dict[str, Any]):
        if capability == "storage.comic_dir.resolve":
            adapter = self._get_storage_client(config)
            return adapter.get_comic_dir(
                str(params.get("album_id") or ""),
                author=params.get("author"),
                title=params.get("title"),
                base_dir=params.get("base_dir"),
            )
        if capability == "asset.preview.resolve":
            adapter = self._get_storage_client(config)
            return adapter.get_preview_image_urls(
                str(params.get("album_id") or ""),
                list(params.get("preview_pages") or []),
            )
        if capability == "health.query.status":
            return self.get_query_status(config)

        adapter = self.get_legacy_client(config)
        if capability == "catalog.search":
            return adapter.search_albums(
                params.get("keyword", ""),
                page=int(params.get("page", 1) or 1),
                max_pages=int(params.get("max_pages", 1) or 1),
                fast_mode=bool(params.get("fast_mode", False)),
            )
        if capability == "catalog.detail":
            return adapter.get_album_by_id(str(params.get("album_id") or ""))
        if capability == "collection.favorites":
            return adapter.get_favorites()
        if capability == "collection.favorites_basic":
            return adapter.get_favorites_basic()
        if capability == "collection.list":
            return adapter.get_user_lists()
        if capability == "collection.detail":
            return adapter.get_list_detail(str(params.get("list_id") or ""))
        if capability == "asset.bundle.fetch":
            detail, success = adapter.download_album(
                str(params.get("album_id") or ""),
                str(params.get("download_dir") or ""),
                bool(params.get("show_progress", False)),
                **dict(params.get("extra") or {}),
            )
            return {"detail": detail, "success": success}
        if capability == "asset.cover.fetch":
            detail, success = adapter.download_cover(
                str(params.get("album_id") or ""),
                str(params.get("save_path") or ""),
                bool(params.get("show_progress", False)),
            )
            return {"detail": detail, "success": success}
        raise ValueError(f"unsupported capability: {capability}")
