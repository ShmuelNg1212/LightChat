from django.contrib.auth import get_user_model
from django.test import TestCase


class UserModelTests(TestCase):
    def test_custom_user_is_active_model(self):
        user = get_user_model().objects.create_user("ana", password="pw-123456789")
        self.assertEqual(user._meta.label, "accounts.User")
        self.assertTrue(user.check_password("pw-123456789"))
