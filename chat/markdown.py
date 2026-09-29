"""Model replies are untrusted: render Markdown with raw HTML disabled, then sanitize."""

import nh3
from markdown_it import MarkdownIt

_md = MarkdownIt("commonmark", {"html": False, "linkify": False, "typographer": False}).enable(
    ["table", "strikethrough"]
)

ALLOWED_TAGS = {
    "p", "br", "hr", "strong", "em", "del", "code", "pre", "blockquote",
    "ul", "ol", "li", "h1", "h2", "h3", "h4", "h5", "h6",
    "table", "thead", "tbody", "tr", "th", "td", "a",
}
ALLOWED_ATTRIBUTES = {"a": {"href", "title"}, "ol": {"start"}, "code": {"class"}, "th": {"style"}, "td": {"style"}}


def render(text: str) -> str:
    html = _md.render(text or "")
    return nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes={"http", "https", "mailto"},
        link_rel="noopener noreferrer nofollow",
        filter_style_properties={"text-align"},
    )
