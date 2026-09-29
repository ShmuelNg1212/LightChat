"""Every user-facing page says LightChat, never the reference product's name."""

import json
from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from chat.models import Conversation

from .helpers import FakeProxy, keys, make_user, openai_reply, rid

OLD_NAME = "Litechat"


@keys
class BrandNameTests(TestCase):
    def assert_branded(self, html, where):
        self.assertIn("LightChat", html, where)
        self.assertNotIn(OLD_NAME, html, where)

    def test_public_pages(self):
        for name in ("login", "signup"):
            html = self.client.get(reverse(name)).content.decode()
            self.assert_branded(html, name)
            self.assertIn("<title>", html)
            self.assertRegex(html, r"<title>[^<]*· LightChat</title>")

    def test_signed_in_pages_and_streamed_reply(self):
        self.client.force_login(make_user())
        payload = {"prompt": "Hi", "model": "gpt-5-6-luna", "request_id": rid()}
        with FakeProxy(openai_reply("Hello")):
            body = b"".join(
                self.client.post(reverse("send"), json.dumps(payload), content_type="application/json").streaming_content
            ).decode()
        self.assertNotIn(OLD_NAME, body)
        convo = Conversation.objects.get()
        for url in (reverse("home"), reverse("conversation", args=[convo.pk]), reverse("credits"), reverse("delete", args=[convo.pk])):
            self.assert_branded(self.client.get(url).content.decode(), url)

    def test_shipped_static_text_is_renamed(self):
        root = Path(settings.BASE_DIR) / "static"
        for path in [root / "js" / "chat.js", root / "css" / "app.css", root / "brand" / "site.webmanifest"]:
            self.assertNotIn(OLD_NAME, path.read_text(), path)
