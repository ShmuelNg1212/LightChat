from django.test import SimpleTestCase

from proxy.sse import SSEEvent, iter_sse


class SSETests(SimpleTestCase):
    def test_parses_events_names_and_multiline_data(self):
        lines = ["event: ping", "data: {}", "", ": comment", "data: a", "data: b", "", "data: tail"]
        self.assertEqual(
            list(iter_sse(lines)),
            [SSEEvent("ping", "{}"), SSEEvent("message", "a\nb"), SSEEvent("message", "tail")],
        )

    def test_crlf_and_no_space(self):
        self.assertEqual(list(iter_sse(["data:x\r", "\r"])), [SSEEvent("message", "x")])
