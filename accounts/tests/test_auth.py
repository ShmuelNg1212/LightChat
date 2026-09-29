from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AuthFlowTests(TestCase):
    def test_pages_require_login(self):
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, f"{reverse('login')}?next=/")

    def test_signup_creates_user_and_signs_in(self):
        response = self.client.post(
            reverse("signup"),
            {"username": "ana", "password1": "correct-horse-9", "password2": "correct-horse-9"},
        )
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(get_user_model().objects.filter(username="ana").exists())
        self.assertContains(self.client.get(reverse("home")), "ana")

    def test_signup_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("signup"),
            {"username": "ana", "password1": "correct-horse-9", "password2": "other-horse-9"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user_model().objects.exists())

    def test_login_and_logout(self):
        get_user_model().objects.create_user("ben", password="correct-horse-9")
        response = self.client.post(
            reverse("login"), {"username": "ben", "password": "correct-horse-9"}
        )
        self.assertRedirects(response, reverse("home"))
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
        self.assertEqual(self.client.get(reverse("home")).status_code, 302)

    def test_login_page_is_public(self):
        self.assertEqual(self.client.get(reverse("login")).status_code, 200)
        self.assertEqual(self.client.get(reverse("signup")).status_code, 200)

    def test_entry_pages_carry_the_identity(self):
        login = self.client.get(reverse("login")).content.decode()
        self.assertIn("Sign in to LightChat", login)
        self.assertIn('class="brand-mark"', login)
        signup = self.client.get(reverse("signup")).content.decode()
        self.assertIn("You start with <strong>5.00</strong> demo credits", signup)
