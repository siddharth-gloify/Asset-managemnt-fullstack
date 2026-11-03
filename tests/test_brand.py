from fastapi.testclient import TestClient

from app.main import app


def test_favicon_and_brand_assets_are_public():
    c = TestClient(app, follow_redirects=False)
    ico = c.get("/favicon.ico")
    assert ico.status_code == 200 and ico.headers["content-type"] == "image/x-icon"
    for path in (
        "/static/brand/favicon.svg",
        "/static/brand/logo.svg",
        "/static/brand/apple-touch-icon.png",
        "/static/brand/og-image.png",
        "/static/brand/site.webmanifest",
    ):
        assert c.get(path).status_code == 200, path


def test_login_page_links_icons_and_logo():
    html = TestClient(app).get("/login").text
    for needle in ('rel="icon"', "apple-touch-icon", "site.webmanifest", "og:image", "/static/brand/logo.svg"):
        assert needle in html, needle
