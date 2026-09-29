# External dependencies

Every exogenous input the project relies on, with its verification status.

**Status key:** `documented` = read in official documentation · `sample-verified` = confirmed against a real response captured in `doc/fixtures/` · `assumed` = not yet verified (marked `ASSUMED` in code) · `needed` = not yet supplied.

## BUILD LLM Proxy (`https://proxy.litechat.ai`)

The designated upstream for all model calls. Docs: <https://proxy.litechat.ai/docs> (revision 2026-09-19, read 2026-09-29).

**Important:** all three interfaces are served by **DeepSeek Flash**. The named models are interface labels; the docs say they "do not reproduce the named providers' model behavior."

### Interfaces

| Interface | Base URL | Endpoint | Model | Auth header | Status |
|---|---|---|---|---|---|
| OpenAI Chat Completions | `https://proxy.litechat.ai/openai/v1` | `POST /chat/completions` | `gpt-5.6-luna` | `Authorization: Bearer <OpenAI key>` | **sample-verified** |
| OpenAI Responses | `https://proxy.litechat.ai/openai/v1` | `POST /responses` | `gpt-5.6-luna` | same OpenAI key | documented (not used by the plan) |
| Anthropic Messages | `https://proxy.litechat.ai/anthropic` | `POST /v1/messages` | `claude-haiku-4-5-20251001` | `x-api-key: <Anthropic key>` and `anthropic-version: 2023-06-01` | **sample-verified** |
| Google Gemini generateContent | `https://proxy.litechat.ai/google` | `POST /v1beta/models/gemini-3.8-flash:generateContent` (stream: `:streamGenerateContent?alt=sse`) | `gemini-3.8-flash` (in the URL) | `x-goog-api-key: <Google key>` | **sample-verified** |

All requests send JSON with `Content-Type: application/json`. `GET /v1/models` does not exist (404), so models cannot be discovered at runtime.

### OpenAI Chat Completions (sample-verified)

- Request: `model`, `messages` (`system` / `user` / `assistant` roles), `max_tokens`, `reasoning_effort` (`"none"` disables reasoning). Also `tools` and `response_format`.
- Response: text in `choices[0].message.content`. `finish_reason` is `stop` (normal), `length` (hit token limit) or `tool_calls`. Usage: `usage.prompt_tokens`, `usage.completion_tokens`, `usage.total_tokens`.
- Streaming: `"stream": true`. SSE chunks carry `choices[].delta.content`. `stream_options.include_usage: true` adds usage chunks with empty `choices`. Ends with `[DONE]`; an error or interrupted stream is not success.

### Anthropic Messages (sample-verified)

- Request: `model`, `messages` (`user` / `assistant`), separate top-level `system`, `max_tokens`, `thinking: {"type": "disabled"}`. Numeric thinking budgets are unsupported.
- Response: `content` is a list of blocks; `text` blocks carry the answer. `stop_reason` is `end_turn` (normal), `max_tokens` (truncated) or `tool_use`. Usage: `usage.input_tokens`, `usage.output_tokens`.
- Streaming: `"stream": true`. SSE with message and indexed content-block events; text arrives as `content_block_delta` with a `text_delta`. The message ends at `message_stop`; check the stop reason. A block ending is not the message ending.

### Google Gemini generateContent (sample-verified)

- Request: `contents` (roles `user` / `model`, each with `parts: [{"text": ...}]`), separate top-level `systemInstruction`, `generationConfig.maxOutputTokens`, `generationConfig.thinkingConfig.thinkingBudget: 0` (disables thinking; other numeric budgets unsupported). Only one candidate is supported.
- Response: text in `candidates[].content.parts[].text`. `finishReason` is `STOP` (normal), `MAX_TOKENS` (truncated) or `SAFETY` (filtered). Usage: `usageMetadata.promptTokenCount`, `usageMetadata.candidatesTokenCount`, `usageMetadata.totalTokenCount`.
- Streaming: replace `:generateContent` with `:streamGenerateContent?alt=sse`. SSE data carries candidate parts, finish information or usage; usage events can omit candidates. There is no `[DONE]`: read to the end of the stream and handle later errors; a finish reason alone is not enough.

### OpenAI Responses (documented, not used)

`input` + `instructions`, `max_output_tokens`, `reasoning: {"effort": "none"}`, `store: false`. `status` is `completed` / `incomplete` / `failed`. `previous_response_id`, stored responses, background mode, hosted search and code execution are unsupported. Streaming ends at `response.completed` / `response.incomplete` / `response.failed`, with no `[DONE]`.

### Verified by real samples (2026-09-29)

Captured with `python manage.py probe_proxy --bad-key`. Redacted transcripts are in [`doc/fixtures/proxy/`](../fixtures/proxy/) and replayed by `proxy/tests/test_captured.py`.

- All three streams match the documented shapes. Each streamed `Say hello in one sentence.` and returned the same text, `Hello! How can I help you today?`, confirming they share one model.
- **The proxy adds a hidden prompt of about 175 tokens.** A 6-word prompt reported `183` input tokens on every interface. Reservations must allow a fixed per-request overhead on top of the conversation text.
- OpenAI streams begin with an empty-content `role` delta and end with a usage chunk (`choices: []`) followed by `data: [DONE]`. The usage also carries `prompt_cache_hit_tokens` / `prompt_cache_miss_tokens` (both billed as input in this app).
- Anthropic streams include `ping` events and report `input_tokens` in both `message_start` and `message_delta`.
- Gemini's final chunk has an empty `parts` list, `finishReason: "STOP"` and `usageMetadata`.
- A bad key returns HTTP 401 with JSON `{"error": {"code": "Unauthorized", "message": "invalid or inactive provider key", "type": "authentication_error"}}`.
- Every response carries an `x-request-id` header.

### Output-token limit (verified 2026-09-29)

All three interfaces accept an output limit of **25,000 tokens** (`max_tokens` / `max_output_tokens` / `maxOutputTokens`), verified with `probe_proxy --no-save --max-tokens 25000`. Each returned HTTP 200 and a normal completion. The proxy's documented maximum is still unknown. Whether it actually *generates* that many tokens in one reply is checked separately (see the reply-limit plan).

### Connectivity (observed 2026-09-29)

`proxy.litechat.ai` has only an IPv4 address (`145.239.154.51`). From the development machine, about half of all TCP connection attempts time out before connecting, and occasionally four attempts in a row fail (seen twice in about ten runs on 2026-09-29), which surfaces to users as "Could not reach the model service" (not charged). The client therefore retries *connection attempts only* (httpx transport `retries=3`, 5 s connect timeout). A request that was sent is never retried.

### Errors and reliability (documented)

| Status | Meaning per docs |
|---|---|
| 400 | Correct the request |
| 401 / 403 | Check the key, its provider and its expiry |
| 429 | Reduce overlapping requests; use a bounded delay |
| 502 / 504 | Upstream request failed |
| 503 or persistent failure | Contact the administrator |

- "Do not automatically retry after partial output arrives."
- "Usage can be unknown after a failure."
- Conversation history is kept by the app and resent on every turn.

### Not published

Prices, currency, billing rules and rate-limit numbers. The app therefore uses its own demo rate table (see [features.md](features.md#models-and-prices)).

### Files (documented, not used yet)

Image inputs and provider file APIs are available. Files are private per account and provider and expire after one hour. Limits: 64 MiB per file; 100 files and 256 MiB per account/provider. No audio or video generation.

## Required secrets

Set in the untracked `.env` (template: `.env.example`).

| Variable | Purpose | Status |
|---|---|---|
| `BUILD_OPENAI_KEY` | OpenAI-interface key | verified working |
| `BUILD_ANTHROPIC_KEY` | Anthropic-interface key | verified working |
| `BUILD_GOOGLE_KEY` | Google-interface key (variable name is ours; the docs call it "YOUR_GOOGLE_KEY") | verified working |
