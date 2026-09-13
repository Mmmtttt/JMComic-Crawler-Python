from __future__ import annotations

import ultimate_provider as provider_module
from ultimate_provider import JMComicProvider


def test_normalize_config_removes_host_only_path_setting():
    config = JMComicProvider().normalize_config(
        {"config_path": "/host-only/config.json", "username": "user", "password": "pass"}
    )

    assert "config_path" not in config
    assert config["enabled"] is True


def test_preview_capability_builds_deterministic_page_urls():
    provider = JMComicProvider()

    assert provider.execute(
        "asset.preview.resolve",
        {"album_id": "12345", "preview_pages": [1, 0, "2", "invalid"]},
        {},
        {},
    ) == [
        "https://cdn-msp.jmapinodeudzn.net/media/photos/12345/00001.webp",
        "https://cdn-msp.jmapinodeudzn.net/media/photos/12345/00002.webp",
    ]


def test_execute_catalog_search_maps_fast_mode_and_login_client(monkeypatch):
    provider = JMComicProvider()
    client = object()
    monkeypatch.setattr(provider, "_get_search_client", lambda config: (client, "fixture-user"))
    calls = []
    monkeypatch.setattr(
        provider_module,
        "search_comics",
        lambda keyword, **kwargs: calls.append((keyword, kwargs))
        or {"results": [{"album_id": 123, "title": "Fixture"}], "page_count": 2},
    )

    result = provider.execute(
        "catalog.search",
        {"keyword": "fixture", "page": 1, "max_pages": 1, "fast_mode": True},
        {},
        {"username": "fixture-user", "password": "fixture-pass"},
    )

    assert calls == [("fixture", {"page": 1, "max_pages": 1, "client": client, "enable_query_fallback": False})]
    assert result["albums"][0]["album_id"] == 123
    assert result["has_next"] is True


def test_execute_catalog_detail_uses_numeric_album_id(monkeypatch):
    provider = JMComicProvider()
    client = object()
    monkeypatch.setattr(provider, "_get_search_client", lambda config: (client, "fixture-user"))
    calls = []
    monkeypatch.setattr(
        provider_module,
        "get_album_detail",
        lambda album_id, client: calls.append((album_id, client)) or {"album_id": album_id, "title": "Detail"},
    )

    result = provider.execute("catalog.detail", {"album_id": "456"}, {}, {})

    assert calls == [(456, client)]
    assert result["albums"][0]["album_id"] == 456


def test_execute_cover_and_storage_capabilities_are_isolated(monkeypatch, tmp_path):
    provider = JMComicProvider()
    response = type("Response", (), {"content": b"fixture", "raise_for_status": lambda self: None})()
    monkeypatch.setattr(provider_module.requests, "get", lambda *args, **kwargs: response)
    monkeypatch.setattr(provider_module.Image, "open", lambda value: type("ImageContext", (), {"__enter__": lambda self: self, "__exit__": lambda *args: None, "mode": "RGB", "save": lambda self, *args, **kwargs: None})())

    cover = provider.execute("asset.cover.fetch", {"album_id": "789", "save_path": str(tmp_path / "cover.jpg")}, {}, {})
    storage = provider.execute("storage.comic_dir.resolve", {"base_dir": str(tmp_path), "album_id": "789"}, {}, {})

    assert cover["success"] is True
    assert cover["detail"]["save_path"] == str(tmp_path / "cover.jpg")
    assert storage == str(tmp_path / "789")
