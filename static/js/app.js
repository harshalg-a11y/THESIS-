document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.querySelector(".chat-box");
  if (!chatBox) return;

  const threadId = chatBox.getAttribute("data-thread-id");
  const refresh = async () => {
    const res = await fetch(`/messages/${threadId}/json/`);
    const data = await res.json();
    chatBox.innerHTML = data.messages
      .map(m => `<div class="chat-msg"><strong>${m.sender}:</strong> ${m.content}</div>`)
      .join("");
  };

  setInterval(refresh, 5000);
});
