from django.test import SimpleTestCase

from chat.markdown import render


class MarkdownTests(SimpleTestCase):
    def test_formats_common_markdown(self):
        html = render("**bold** and `code`\n\n```py\nprint(1)\n```\n\n| a | b |\n|---|---|\n| 1 | 2 |")
        self.assertIn("<strong>bold</strong>", html)
        self.assertIn("<code>code</code>", html)
        self.assertIn('<code class="language-py">print(1)', html)
        self.assertIn("<table>", html)

    def test_raw_html_is_escaped(self):
        html = render('<script>alert(1)</script><img src=x onerror=alert(1)>')
        self.assertNotIn("<script", html)
        self.assertNotIn("<img", html)
        self.assertIn("&lt;script&gt;", html)

    def test_dangerous_links_are_removed(self):
        html = render("[click](javascript:alert(1)) [ok](https://example.com)")
        self.assertNotIn('href="javascript', html)
        self.assertIn('href="https://example.com"', html)
        self.assertIn('rel="noopener noreferrer nofollow"', html)
