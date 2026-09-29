// LightChat chat page behaviour. No framework; progressive enhancement over server-rendered HTML.
(function () {
  "use strict";

  // ---- Sidebar toggle (phones) ----
  const toggle = document.querySelector("[data-sidebar-toggle]");
  const sidebar = document.getElementById("sidebar");
  if (toggle && sidebar) {
    const setOpen = (open) => {
      sidebar.classList.toggle("open", open);
      toggle.setAttribute("aria-expanded", String(open));
    };
    toggle.addEventListener("click", () => setOpen(!sidebar.classList.contains("open")));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && sidebar.classList.contains("open")) {
        setOpen(false);
        toggle.focus();
      }
    });
  }

  // ---- Composer ----
  const form = document.getElementById("composer");
  if (!form) return;

  const textarea = form.querySelector("textarea[name=prompt]");
  const modelSelect = form.querySelector("select[name=model]");
  const conversationInput = form.querySelector("input[name=conversation]");
  const sendButton = document.getElementById("send");
  const stopButton = document.getElementById("stop");
  const scroller = document.getElementById("messages");
  const list = document.getElementById("messages-inner");
  const live = document.getElementById("live");
  const csrf = form.querySelector("input[name=csrfmiddlewaretoken]").value;

  let busy = false;
  let cancelUrl = null;
  let controller = null;
  let stopping = false;
  // One ID per message: a repeated submit of the same message reuses it, so the
  // server can refuse the duplicate instead of charging twice.
  let requestId = crypto.randomUUID();

  const announce = (text) => { live.textContent = ""; setTimeout(() => { live.textContent = text; }, 50); };

  const nearBottom = () => scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight < 80;
  const scrollToBottom = () => { scroller.scrollTop = scroller.scrollHeight; };

  const rate = document.getElementById("model-rate");
  const example = document.getElementById("model-example");
  const showPrice = () => {
    const option = modelSelect.selectedOptions[0];
    rate.textContent = option.dataset.price + ".";
    example.textContent = option.dataset.example;
  };
  modelSelect.addEventListener("change", showPrice);
  showPrice();

  function autosize() {
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, window.innerHeight * 0.4) + "px";
  }
  textarea.addEventListener("input", autosize);

  textarea.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
      e.preventDefault();
      form.requestSubmit();
    }
  });

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function fromHTML(html) {
    const t = document.createElement("template");
    t.innerHTML = html.trim();
    return t.content.firstElementChild;
  }

  function setBusy(value) {
    busy = value;
    sendButton.disabled = value;
    if (!value) {
      stopButton.hidden = true;
      stopButton.disabled = false;
      cancelUrl = null;
    }
    textarea.setAttribute("aria-busy", String(value));
  }

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  // The settle: count the available figure to its new value and close the held segment.
  function countTo(node, target) {
    const from = parseFloat(node.textContent.replace(/,/g, ""));
    const to = parseFloat(target.replace(/,/g, ""));
    if (reducedMotion.matches || !isFinite(from) || !isFinite(to) || from === to) {
      node.textContent = target;
      return;
    }
    const start = performance.now();
    const duration = 520;
    const step = (now) => {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 4);
      node.textContent = t < 1 ? (from + (to - from) * eased).toFixed(4) : target;
      if (t < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  function setBalance(event, { settle = false } = {}) {
    const available = document.getElementById("balance-available");
    const held = document.getElementById("balance-held");
    const heldValue = document.getElementById("balance-held-value");
    if (available && event.available) {
      if (settle) countTo(available, event.available);
      else available.textContent = event.available;
    }
    if (!held || !heldValue) return;
    if (event.held) {
      held.classList.remove("is-settling");
      held.hidden = false;
      heldValue.textContent = event.held;
    } else if (!held.hidden) {
      if (settle && !reducedMotion.matches) {
        held.classList.add("is-settling");
        held.addEventListener("animationend", () => { held.hidden = true; held.classList.remove("is-settling"); }, { once: true });
      } else {
        held.hidden = true;
      }
    }
  }

  function adoptConversation(start) {
    conversationInput.value = start.conversation;
    if (!start.created) return;
    history.replaceState(null, "", start.url);
    document.title = start.title + " · LightChat";
    if (start.header_html && !document.querySelector(".chat-header")) {
      scroller.before(fromHTML(start.header_html));
    }
    const empty = document.getElementById("sidebar-empty");
    if (empty) empty.remove();
    const convoList = document.getElementById("convo-list");
    const item = el("li");
    const link = el("a", "", start.title);
    link.href = start.url;
    link.setAttribute("aria-current", "page");
    item.appendChild(link);
    convoList.prepend(item);
  }

  function pendingReply() {
    const article = el("article", "msg msg-assistant");
    article.dataset.status = "streaming";
    const content = el("div", "content streaming is-waiting", "Waiting for the first words…");
    const reading = el("p", "reading");
    reading.appendChild(el("span", "reading-model", modelSelect.selectedOptions[0].textContent));
    article.append(content, reading);
    return { article, content, reading };
  }

  function holding(reserved) {
    const state = el("span", "reading-state is-held");
    const light = el("span", "pulse-light is-live");
    light.setAttribute("aria-hidden", "true");
    const amount = el("strong", "", reserved);
    state.append(light, document.createTextNode("Holding up to "), amount, document.createTextNode(" credits"));
    return state;
  }

  function showRejection(article, message, url, code) {
    article.replaceChildren();
    article.dataset.status = "rejected";
    const box = el("p", "reading-note is-danger");
    box.append(el("strong", "", "Not sent."), document.createTextNode(" " + message + " "));
    if (url) {
      const link = el("a", "", "Open the chat");
      link.href = url;
      box.appendChild(link);
    }
    if (code === "insufficient_credit") {
      const link = el("a", "", "Add demo credits");
      link.href = form.dataset.creditsUrl;
      box.appendChild(link);
    }
    article.appendChild(box);
    announce("Message not sent. " + message);
  }

  async function send({ prompt, retry }) {
    if (busy) return;
    setBusy(true);
    stopping = false;
    const empty = document.getElementById("empty-state");
    if (empty) empty.remove();

    let userBubble = null;
    if (!retry) {
      userBubble = el("div", "msg msg-user");
      userBubble.appendChild(el("div", "prompt", prompt));
      list.appendChild(userBubble);
    }
    const reply = pendingReply();
    list.appendChild(reply.article);
    scrollToBottom();

    const body = {
      prompt: prompt || "",
      model: modelSelect.value,
      request_id: requestId,
      conversation: conversationInput.value || null,
      retry: retry || null,
    };

    let response;
    controller = new AbortController();
    try {
      response = await fetch(form.dataset.sendUrl, {
        signal: controller.signal,
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
        body: JSON.stringify(body),
      });
    } catch (err) {
      // Nothing reached the server, or we can't tell. Keep the same request ID so
      // sending again can't be charged twice.
      showRejection(reply.article, "Couldn't reach LightChat. Check your connection and send again.");
      if (userBubble) { userBubble.remove(); textarea.value = prompt; autosize(); }
      setBusy(false);
      return;
    }

    if (!response.ok) {
      let data = {};
      try { data = await response.json(); } catch (_) { /* not JSON */ }
      const error = data.error || { message: "Something went wrong. Try again." };
      showRejection(reply.article, error.message, error.url, error.code);
      if (userBubble && error.code !== "duplicate") {
        userBubble.remove();
        textarea.value = prompt || "";
        autosize();
      }
      if (error.code === "duplicate") requestId = crypto.randomUUID();
      setBusy(false);
      return;
    }

    // Accepted: this request ID is spent.
    requestId = crypto.randomUUID();
    if (!retry) { textarea.value = ""; autosize(); }

    let received = "";
    let ended = false;
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    const handle = (event) => {
      if (event.type === "start") {
        adoptConversation(event);
        cancelUrl = event.cancel_url;
        stopButton.hidden = false;
        if (userBubble && event.user_message) userBubble.dataset.message = event.user_message;
        reply.reading.appendChild(holding(event.reserved));
        setBalance(event);
      } else if (event.type === "delta") {
        const follow = nearBottom();
        if (!received) reply.content.classList.remove("is-waiting");
        received += event.text;
        reply.content.textContent = received;
        if (follow) scrollToBottom();
      } else if (event.type === "end") {
        ended = true;
        const follow = nearBottom();
        const finished = fromHTML(event.html);
        reply.article.replaceWith(finished);
        setBalance(event, { settle: true });
        if (follow) scrollToBottom();
        announce(event.status === "completed" ? "Reply finished." : "Reply did not finish.");
      }
    };

    try {
      for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        let newline;
        while ((newline = buffer.indexOf("\n")) >= 0) {
          const line = buffer.slice(0, newline).trim();
          buffer = buffer.slice(newline + 1);
          if (line) handle(JSON.parse(line));
        }
      }
    } catch (err) {
      /* connection dropped; handled below */
    }

    if (!ended) {
      // The stream broke before the server finished. Never present it as complete.
      reply.article.dataset.status = "needs_reconciliation";
      reply.content.classList.remove("streaming");
      const warn = el("p", "reading-note", stopping
        ? "Stopped. Reload the page to see what was saved and any credit held for review."
        : "The connection dropped before this reply finished. Reload the page to see its final state.");
      reply.article.appendChild(warn);
      announce("Connection lost before the reply finished.");
    }
    setBusy(false);
    textarea.focus();
  }

  stopButton.addEventListener("click", async () => {
    if (!cancelUrl) return;
    stopping = true;
    stopButton.disabled = true;
    announce("Stopping reply.");
    try {
      await fetch(cancelUrl, { method: "POST", headers: { "X-CSRFToken": csrf } });
    } catch (_) { /* fall through to abort */ }
    // If the service is silent, the server only notices the stop on the next chunk;
    // give it a moment, then drop the connection so the page is usable again.
    const pending = controller;
    setTimeout(() => { if (busy && controller === pending) pending.abort(); }, 5000);
  });

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const prompt = textarea.value.trim();
    if (!prompt || busy) return;
    send({ prompt });
  });

  // Retry buttons are rendered by the server on failed replies.
  list.addEventListener("click", (e) => {
    const button = e.target.closest("[data-retry]");
    if (!button || busy) return;
    button.closest(".msg").remove();
    send({ retry: button.dataset.retry });
  });

  autosize();
  scrollToBottom();
})();
