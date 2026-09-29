# Features

What LightChat does today, from the user's point of view. The look and behavior of each element is specified in [DESIGN.md](../../DESIGN.md).

## Accounts

- Sign up with a username and password, then sign in and out. Every page other than sign-up and sign-in requires an account. Sign-up states the starting grant, and its help text is LightChat's own wording (Django's password rules still apply).
- Each user sees only their own chats, messages and credit.

## Credits (demo, not real money)

- New accounts receive **5.00 demo credits**.
- **Add demo credits** on the Credits page adds 1.00, up to 10.00 available. No payment is taken.
- The top bar's **credit readout** always shows available credit to 4 decimal places and links to the Credits page. While a reply holds credit, an amber *held* amount appears with a blinking light. When a reply finishes, it briefly shows the *charged* amount while the balance counts down to its new value.
- The Credits page shows available and held credit, a table of models and prices, and the full history of every grant, top-up, hold, charge and release.

## Models and prices

| Model (as shown) | Interface | Input / 1M tokens | Output / 1M tokens | Longest reply |
|---|---|---|---|---|
| GPT-5.6 Luna · OpenAI interface | OpenAI Chat Completions | 5.00 | 20.00 | 25,000 tokens |
| Claude Haiku 4.5 · Anthropic interface | Anthropic Messages | 5.00 | 20.00 | 25,000 tokens |
| Gemini 3.8 Flash · Google interface | Google generateContent | 5.00 | 20.00 | 25,000 tokens |

A reply's writing therefore costs at most **0.50 credits**. Reading the conversation is charged on top, and only tokens actually used are charged. A reply can stream for up to 20 minutes locally and **260 seconds on the live site** (Vercel's free-plan limit). At the observed ~135 tokens/s, a full-length reply takes about 3 minutes.

All three are answered by **DeepSeek Flash** behind different provider interfaces. The app says so below the message box (on phones, under **How models and prices work**) and on the Credits page. Rates are editable in the admin (Catalog → Model offerings). Past charges keep the rate in force when they were made.

## Chatting

- **First run:** a new account sees its balance and three numbered steps (pick a model, ask, see what it cost). Starting a new chat later shows a compact header instead.
- Type a message, pick a model and send it with **Enter** (**Shift+Enter** adds a new line). The reply streams in as it is written.
- Under the message box, the selected model's price, a worked example (a 1,000-token question with a 500-token answer costs 0.0150 credits), and the **minimum hold** a reply takes. If the balance can't cover that hold, a notice says so with an **Add demo credits** link, and Send is disabled.
- Models can be switched at any point in a chat. Each reply records the model that wrote it, and the conversation context carries over.
- Replies are formatted (lists, bold, code blocks, tables). Model output can't inject HTML or scripts.
- Under each reply, a **reading line**: model name, input and output tokens, and "X credits charged". While in progress it shows "Holding up to X credits". After a reload mid-reply, it notes that the reply is still being written.
- Answers keep a comfortable fixed line length (~68 characters) at any window width. Wide code and tables scroll inside the answer.
- A new chat is titled from its first message (no paid call). Chats can be renamed or deleted (with confirmation) from the **⋯** menu. Deleting a chat keeps the credit history.
- Chats persist across reloads and sign-ins. On phones, the chat list opens from the ☰ button.

## When things go wrong

| Situation | What the user sees | Credit |
|---|---|---|
| Not enough credit | Caught before sending by the minimum-hold notice. If the server refuses: "Not sent. Not enough credit: this reply could cost up to X credits and you have Y." with an **Add demo credits** link; the message goes back into the box | Nothing held |
| Service busy (429), bad key, bad request | Reading line "Not charged", then "No reply." with the reason and **Retry** | Hold released |
| Reply hit the length limit | Reply kept, plus "reached the 25,000-token limit and was cut off. Ask it to continue." | Charged for actual usage |
| **Stop** pressed, connection dropped, service error (5xx) or timeout | Partial reply kept; reading line "Under review · up to X credits held", with a plain explanation and **Retry** | Held until an admin charges or releases it; the outcome is then shown on the reply |
| No model configured | The message box is replaced by "No models are available right now, so nothing can be sent or charged." | Nothing held |
| Same message sent twice (double click, two tabs) | Only one reply is produced | Charged once |

Retry is always explicit and only offered on the latest message. Nothing is retried automatically.

## Accessibility

WCAG 2.2 AA:
- Contrast is checked for every color token in both themes.
- Everything is operable by keyboard, with visible focus. On chat pages, a *Skip to conversation* link jumps past the saved-chats rail.
- Screen readers hear reply completion and errors once each, never the streamed words.
- Reduced-motion settings stop the pulse and the count-down.
- Pages work from 360 px wide without horizontal scrolling.

The light and dark themes follow the OS.

## Admin (`/admin/`)

- **Generations:** every metered request with status, hold, charge and tokens. Actions: *Reconcile: charge the held amount* and *Reconcile: release the hold*.
- **Wallets / Ledger entries:** read-only. Users with credit history can't be deleted, because the ledger protects that history.
- **Model offerings:** enable or disable models, and edit rates and the reply limit (max output tokens).
- **Conversations:** metadata only; message contents aren't shown.

## Not included yet

Attachments, web search, Google sign-in, password reset by email, and real payments. (The app is publicly deployed at https://lightchat-five.vercel.app.) The Credits page, delete confirmation and admin use the LightChat colors and fonts but haven't been redesigned yet (planned slice 2).
