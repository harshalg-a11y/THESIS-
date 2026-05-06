document.addEventListener("DOMContentLoaded", () => {
  // ── Chat auto-scroll ────────────────────────────────────────
  const chatBox = document.getElementById("chatBox") || document.querySelector(".chat-box");
  if (chatBox) {
    // Scroll to bottom on load
    chatBox.scrollTop = chatBox.scrollHeight;

    const threadId = chatBox.getAttribute("data-thread-id");
    if (threadId) {
      const refresh = async () => {
        try {
          const res = await fetch(`/messages/${threadId}/json/`);
          if (!res.ok) return;
          const data = await res.json();
          const wasAtBottom =
            chatBox.scrollHeight - chatBox.scrollTop - chatBox.clientHeight < 60;

          chatBox.innerHTML = data.messages
            .map(m => `
              <div class="chat-msg ${m.is_me ? "me" : ""}">
                <span class="msg-sender">${m.sender}</span>
                <div class="msg-bubble">${m.content}</div>
              </div>`)
            .join("");

          if (wasAtBottom) {
            chatBox.scrollTop = chatBox.scrollHeight;
          }
        } catch (_) { /* silent */ }
      };
      setInterval(refresh, 5000);
    }
  }

  // ── Chat textarea auto-resize ────────────────────────────────
  const chatInput = document.getElementById("chatInput");
  if (chatInput) {
    chatInput.addEventListener("input", () => {
      chatInput.style.height = "auto";
      chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + "px";
    });

    // Submit on Ctrl/Cmd+Enter
    chatInput.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        const form = document.getElementById("chatForm");
        if (form) form.submit();
      }
    });
  }

  // ── Navbar hamburger ─────────────────────────────────────────
  // (handled inline in nav.html, but keep here as fallback)
  const toggle = document.getElementById("navToggle");
  const links  = document.getElementById("navLinks");
  if (toggle && links) {
    toggle.addEventListener("click", () => links.classList.toggle("open"));
  }
});
