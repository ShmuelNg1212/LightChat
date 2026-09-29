from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from chat.models import Conversation, Message


class ConversationViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.ana = User.objects.create_user("ana", password="x")
        self.ben = User.objects.create_user("ben", password="x")
        self.convo = Conversation.objects.create(owner=self.ana, title="Trip ideas")
        Message.objects.create(conversation=self.convo, role="user", content="Where should I go?")
        Message.objects.create(conversation=self.convo, role="assistant", content="Try Siargao.")
        self.client.force_login(self.ana)

    def test_home_lists_only_own_conversations(self):
        Conversation.objects.create(owner=self.ben, title="Ben's secret")
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Trip ideas")
        self.assertNotContains(response, "Ben&#x27;s secret")
        self.assertNotContains(response, "Ben's secret")

    def test_conversation_shows_messages(self):
        response = self.client.get(reverse("conversation", args=[self.convo.pk]))
        self.assertContains(response, "Where should I go?")
        self.assertContains(response, "Try Siargao.")

    def test_other_users_get_404_everywhere(self):
        self.client.force_login(self.ben)
        pk = self.convo.pk
        self.assertEqual(self.client.get(reverse("conversation", args=[pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("rename", args=[pk]), {"title": "x"}).status_code, 404)
        self.assertEqual(self.client.get(reverse("delete", args=[pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("delete", args=[pk])).status_code, 404)
        self.convo.refresh_from_db()
        self.assertEqual(self.convo.title, "Trip ideas")

    def test_rename(self):
        self.client.post(reverse("rename", args=[self.convo.pk]), {"title": "  Beach   trip "})
        self.convo.refresh_from_db()
        self.assertEqual(self.convo.title, "Beach trip")

    def test_rename_rejects_blank(self):
        self.client.post(reverse("rename", args=[self.convo.pk]), {"title": "   "})
        self.convo.refresh_from_db()
        self.assertEqual(self.convo.title, "Trip ideas")

    def test_delete_requires_confirmation_then_removes_messages(self):
        response = self.client.get(reverse("delete", args=[self.convo.pk]))
        self.assertContains(response, "Delete this chat?")
        self.assertTrue(Conversation.objects.filter(pk=self.convo.pk).exists())
        self.client.post(reverse("delete", args=[self.convo.pk]))
        self.assertFalse(Conversation.objects.filter(pk=self.convo.pk).exists())
        self.assertFalse(Message.objects.exists())

    def test_title_from_prompt(self):
        self.assertEqual(Conversation.title_from("  hello \n world "), "hello world")
        long = Conversation.title_from("word " * 40)
        self.assertLessEqual(len(long), 60)
        self.assertTrue(long.endswith("…"))
