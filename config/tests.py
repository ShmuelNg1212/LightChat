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


class DatabaseConfigTests(SimpleTestCase):
    def test_sqlite_waits_for_the_write_lock(self):
        from config.deploy import database_config

        db = database_config("sqlite:////tmp/x.sqlite3", conn_max_age=60)
        self.assertEqual(db["OPTIONS"]["transaction_mode"], "IMMEDIATE")
        self.assertFalse(db.get("DISABLE_SERVER_SIDE_CURSORS"))

    def test_postgres_is_safe_behind_a_transaction_pooler(self):
        from config.deploy import database_config

        db = database_config("postgres://u:p@db.example.com:5432/app?sslmode=require", conn_max_age=0)
        self.assertEqual(db["ENGINE"], "django.db.backends.postgresql")
        self.assertTrue(db["DISABLE_SERVER_SIDE_CURSORS"])
        self.assertTrue(db["CONN_HEALTH_CHECKS"])
        self.assertEqual(db["CONN_MAX_AGE"], 0)
        self.assertEqual(db["OPTIONS"]["sslmode"], "require")
