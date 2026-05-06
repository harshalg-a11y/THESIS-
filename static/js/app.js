/* ============================================================
   THESIS PORTAL — App JS
   Navigation · Chat · Scroll animations · Micro-interactions
   ============================================================ */

document.addEventListener("DOMContentLoaded", () => {

  /* ---- Hamburger menu ---- */
  const navToggle = document.getElementById("navToggle");
  const navLinks  = document.getElementById("navLinks");
  if (navToggle && navLinks) {
    navToggle.addEventListener("click", () => {
      navLinks.classList.toggle("open");
      navToggle.classList.toggle("active");
    });
    // Close on outside click
    document.addEventListener("click", (e) => {
      if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
        navLinks.classList.remove("open");
        navToggle.classList.remove("active");
      }
    });
  }

  /* ---- Active nav link ---- */
  const currentPath = window.location.pathname;
  document.querySelectorAll(".nav-links a").forEach(a => {
    if (a.getAttribute("href") === currentPath ||
        (a.getAttribute("href") !== "/" && currentPath.startsWith(a.getAttribute("href")))) {
      a.classList.add("nav-active");
    }
  });

  /* ---- Scroll-reveal (fade-in class) ---- */
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add("visible");
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.1, rootMargin: "0px 0px -40px 0px" });

  document.querySelectorAll(".fade-in").forEach(el => observer.observe(el));

  /* ---- Auto-dismiss alerts ---- */
  document.querySelectorAll(".alert").forEach(el => {
    setTimeout(() => {
      el.style.transition = "opacity 0.5s";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 500);
    }, 4000);
  });

  /* ---- Chat: auto-scroll to bottom ---- */
  const chatBox = document.querySelector(".chat-box");
  if (!chatBox) return;

  const scrollToBottom = () => {
    chatBox.scrollTop = chatBox.scrollHeight;
  };

  scrollToBottom();

  /* ---- Chat: live refresh every 5s ---- */
  const threadId = chatBox.getAttribute("data-thread-id");
  if (!threadId) return;

  const currentUser = chatBox.getAttribute("data-current-user") || "";

  const renderMessages = (messages) => {
    chatBox.innerHTML = messages.map(m => {
      const isOwn = m.sender === currentUser;
      return `
        <div class="chat-msg ${isOwn ? "own" : ""}">
          <div class="sender">${m.sender}</div>
          <div class="bubble">${escapeHtml(m.content)}</div>
          <div class="time">${m.timestamp || ""}</div>
        </div>`;
    }).join("");
    scrollToBottom();
  };

  let lastCount = 0;

  const refresh = async () => {
    try {
      const res = await fetch(`/messages/${threadId}/json/`);
      if (!res.ok) return;
      const data = await res.json();
      if (data.messages.length !== lastCount) {
        lastCount = data.messages.length;
        renderMessages(data.messages);
      }
    } catch (_) { /* silent */ }
  };

  refresh();
  setInterval(refresh, 5000);

  /* ---- Chat: send on Enter (not Shift+Enter) ---- */
  const chatInput = document.querySelector(".chat-send-input");
  if (chatInput) {
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        chatInput.closest("form").submit();
      }
    });
  }

  /* ---- Password toggle ---- */
  document.querySelectorAll(".pwd-toggle").forEach(btn => {
    btn.addEventListener("click", () => {
      const input = btn.previousElementSibling || btn.parentElement.querySelector("input");
      if (!input) return;
      if (input.type === "password") {
        input.type = "text";
        btn.innerHTML = '<i class="fa-solid fa-eye-slash"></i>';
      } else {
        input.type = "password";
        btn.innerHTML = '<i class="fa-solid fa-eye"></i>';
      }
    });
  });

  /* ---- Auth form: loading progress on submit ---- */
  const authForm = document.querySelector(".auth-submit-form");
  if (authForm) {
    authForm.addEventListener("submit", () => {
      const bar = document.querySelector(".auth-progress");
      if (bar) bar.classList.add("visible");
      const btn = authForm.querySelector(".auth-submit");
      if (btn) { btn.disabled = true; btn.textContent = "Please wait…"; }
    });
  }

  /* ---- Stat counter animation ---- */
  document.querySelectorAll(".stat strong, .ds-num, .dash-stat .ds-num").forEach(el => {
    const target = parseInt(el.textContent, 10);
    if (isNaN(target) || target === 0) return;
    let start = 0;
    const duration = 1200;
    const step = Math.ceil(target / (duration / 16));
    const timer = setInterval(() => {
      start = Math.min(start + step, target);
      el.textContent = start;
      if (start >= target) clearInterval(timer);
    }, 16);
  });

});

/* ---- Utility: escape HTML ---- */
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
