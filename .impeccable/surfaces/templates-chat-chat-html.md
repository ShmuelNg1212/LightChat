---
version: 1
slug: "templates-chat-chat-html"
primary_target: "templates/chat/chat.html"
related_targets: ["templates/base.html"]
---

# Surface brief: chat screen

- **Scope:** the signed-in chat screen (`templates/chat/chat.html` with `templates/base.html` shell), all its states. Sign-in/sign-up share the shell.
- **Visitor mode:** Operate.
- **Audience and job:** occasional, nontechnical users; have a conversation and understand what it cost (see PRODUCT.md).
- **Source brief:** doc/design/2026-09-29-1357-lightchat-identity-brief.md (approved 2026-09-29).
- **Memorable moment:** the settle: a hold becomes a charge on the readout and the rest comes back.
- **Unresolved:** per-chat spend in the rail (later slice).

## Direction contract

THESIS: Every reply is metered in plain view; the chat reads like a calm prepaid-meter faceplate with one backlit readout, refusing the category's grey-bubble, glowing-orb default.

OWN-WORLD: Faceplate grey ground (#F1F2EF / #121513), printed ink, one sage backlit readout (#DCE4D3 / #1D2A21), an amber pulse (#C27400 / #F0A93A) that only ever means credit in motion; Public Sans text, Barlow Semi Condensed readouts with tabular figures; flat planes, 1px hairlines, 6px corners, no blurred shadows; state by inversion; states printed as words.

STORY: The visitor sees what they have, picks a model with its price in view, reads the answer comfortably at a fixed measure, and watches the hold become a charge and the rest come back.

FIRST VIEWPORT: Top bar: lockup left, credit readout next to it, account right. Rail left (drawer on phones). Empty state: a first-run column at the reading measure with the balance, demo note, and three numbered steps in a margin column. Composer dock at the bottom aligned to the column, with the tariff selector, its rate and worked example, and inverted Send as the primary action.

FORM: Prepaid Meter, #5 of 7 grounded candidates (assigned), seed key 00ad6455. Signature interaction: the settle; motion grammar: pulse while held, settle on finish, drawer slide; reduced motion makes all three instant.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
