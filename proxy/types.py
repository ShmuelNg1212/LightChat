from dataclasses import dataclass, field


@dataclass(frozen=True)
class Message:
    role: str  # "user" or "assistant"
    content: str


@dataclass
class Usage:
    input_tokens: int
    output_tokens: int


class Finish:
    """Normalized finish reasons."""

    COMPLETE = "complete"  # the model finished its answer
    LENGTH = "length"  # stopped at the output token limit
    FILTERED = "filtered"  # stopped by a safety filter
    OTHER = "other"  # e.g. a tool call, which this app does not use


@dataclass(frozen=True)
class TextDelta:
    text: str


@dataclass(frozen=True)
class Done:
    """The stream reached its documented terminal point."""

    finish: str
    usage: Usage | None
    raw_reason: str = ""


@dataclass
class ProxyError(Exception):
    """A request that did not complete.

    ``nothing_generated`` is True only when the request certainly produced no
    billable output (rejected before generation, or never sent). Otherwise the
    upstream may have charged and the generation must be reconciled.
    """

    kind: str
    message: str
    status: int | None = None
    nothing_generated: bool = False
    usage: Usage | None = None
    detail: dict = field(default_factory=dict)

    def __str__(self):
        return f"{self.kind} ({self.status}): {self.message}"


class Cancelled(Exception):
    """The user stopped the reply. Final usage is unknown."""
