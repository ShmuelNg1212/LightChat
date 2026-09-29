# Features

What Litechat does today, from the user's point of view.

## Accounts

- Sign up with a username and password, then sign in and out. Every page other than sign-up and sign-in requires an account.
- Each user sees only their own chats, messages and credit.

## Credits (demo, not real money)

- New accounts receive **5.00 demo credits**.
- **Add demo credits** on the Credits page adds 1.00, up to 10.00 available. No payment is taken.
- The top bar always shows available credit to 4 decimal places, and links to the Credits page.
- The Credits page shows available and held credit, a table of models and prices, and the full history of every grant, top-up, hold, charge and release.

## Models and prices

| Model (as shown) | Interface | Input / 1M tokens | Output / 1M tokens | Longest reply |
|---|---|---|---|---|
| GPT-5.6 Luna · OpenAI interface | OpenAI Chat Completions | 5.00 | 20.00 | 25,000 tokens |
| Claude Haiku 4.5 · Anthropic interface | Anthropic Messages | 5.00 | 20.00 | 25,000 tokens |
| Gemini 3.8 Flash · Google interface | Google generateContent | 5.00 | 20.00 | 25,000 tokens |

A reply's writing therefore costs at most **0.50 credits**. Reading the conversation is charged on top, and only tokens actually used are charged. A reply can stream for up to 20 minutes; at the observed ~135 tokens/s a full-length reply takes about 3 minutes.

All three are answered by **DeepSeek Flash** behind different provider interfaces, and the app says so below the message box and on the Credits page. Rates are editable in the admin (Catalog → Model offerings). Past charges keep the rate in force when they were made.

## Chatting

- Type a message, pick a model and send it with **Enter** (**Shift+Enter** adds a new line). The reply streams in as it is written.
- Models can be switched at any point in a chat. Each reply records the model that wrote it, and the conversation context carries over.
- Replies are formatted (lists, bold, code blocks, tables). Model output can't inject HTML or scripts.
- Under each reply: model name, input and output tokens, and cost ("Charged"). While a reply is in progress it shows "Up to X credits held · Estimate".
- A new chat is titled from its first message (no paid call). Chats can be renamed or deleted (with confirmation) from the **⋯** menu. Deleting a chat keeps the credit history.
- Chats persist across reloads and sign-ins. On phones, the chat list opens from the ☰ button.

## When things go wrong

| Situation | What the user sees | Credit |
|---|---|---|
| Not enough credit | "Not sent. Not enough credit…" with an **Add demo credits** link; the message goes back into the box | Nothing held |
| Service busy (429), bad key, bad request | "No reply. … You were not charged." with **Retry** | Hold released |
| Reply hit the length limit | Reply kept, plus "hit the 25,000-token limit and was cut off" | Charged for actual usage |
| **Stop** pressed, connection dropped, service error (5xx) or timeout | Partial reply kept, marked **Under review**, explaining that up to X credits stay held | Held until an admin charges or releases it; the outcome is then shown on the reply |
| Same message sent twice (double click, two tabs) | Only one reply is produced | Charged once |

Retry is always explicit and only offered on the latest message. Nothing is retried automatically.

## Admin (`/admin/`)

- **Generations:** every metered request with status, hold, charge and tokens. Actions: *Reconcile: charge the held amount* and *Reconcile: release the hold*.
- **Wallets / Ledger entries:** read-only. Users with credit history can't be deleted, because the ledger protects that history.
- **Model offerings:** enable or disable models, and edit rates and the reply limit (max output tokens).
- **Conversations:** metadata only; message contents aren't shown.

## Not included yet

Attachments, web search, Google sign-in, password reset by email, real payments, and a public deployment.
