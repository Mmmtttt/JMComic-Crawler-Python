from __future__ import annotations

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
