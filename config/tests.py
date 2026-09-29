from django.test import SimpleTestCase


class SmokeTests(SimpleTestCase):
    def test_healthz(self):
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")


class BrandAssetTests(SimpleTestCase):
    def test_manifest_is_valid_and_its_icons_exist(self):
        import json
        from pathlib import Path

        from django.conf import settings

        brand = Path(settings.BASE_DIR) / "static" / "brand"
        manifest = json.loads((brand / "site.webmanifest").read_text())
        self.assertEqual((manifest["name"], manifest["short_name"]), ("LightChat", "LightChat"))
        self.assertEqual(manifest["start_url"], "/")
        purposes = {i["purpose"] for i in manifest["icons"]}
        self.assertEqual(purposes, {"any", "maskable"})
        for icon in manifest["icons"]:
            self.assertTrue((brand / icon["src"]).is_file(), icon["src"])
        for name in ("favicon.svg", "favicon-32.png", "apple-touch-icon.png"):
            self.assertTrue((brand / name).is_file(), name)

    def test_pages_link_favicon_and_manifest(self):
        html = self.client.get("/accounts/login/").content.decode()
        for fragment in ("brand/favicon.svg", "brand/favicon-32.png", "brand/apple-touch-icon.png", "brand/site.webmanifest"):
            self.assertIn(fragment, html)
        self.assertNotIn("data:image/svg+xml", html)
