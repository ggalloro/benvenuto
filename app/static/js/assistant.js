// Benvenuto Assistant chat panel.
// The backend endpoint (POST /api/assistant) is a placeholder: the onboarding
// agent is not connected yet. askAssistant() is the single integration point.

const employeeId = document.body.dataset.employeeId;
const bubble = document.getElementById("assistant-bubble");
const panel = document.getElementById("assistant-panel");
const messages = document.getElementById("assistant-messages");
const form = document.getElementById("assistant-form");
const input = document.getElementById("assistant-input");
let sessionId = null;

function formatMarkdown(text) {
  const esc = String(text || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  const inline = (s) =>
    s
      .replace(/`([^`\n]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>")
      .replace(/(^|[\s(])\*([^*\n]+)\*(?=[\s.,;:!?)]|$)/g, "$1<em>$2</em>");

  const lines = esc.split(/\r?\n/);
  const out = [];
  let listType = null;
  const closeList = () => {
    if (listType) {
      out.push(`</${listType}>`);
      listType = null;
    }
  };

  for (const raw of lines) {
    const line = raw.trim();
    if (!line) {
      closeList();
      continue;
    }
    if (/^(-{3,}|\*{3,})$/.test(line)) {
      closeList();
      out.push("<hr>");
      continue;
    }
    const h = line.match(/^#{1,4}\s+(.*)$/);
    if (h) {
      closeList();
      out.push(`<div class="msg-heading">${inline(h[1])}</div>`);
      continue;
    }
    const ul = line.match(/^[*+-]\s+(.*)$/);
    if (ul) {
      if (listType !== "ul") {
        closeList();
        listType = "ul";
        out.push("<ul>");
      }
      out.push(`<li>${inline(ul[1])}</li>`);
      continue;
    }
    const ol = line.match(/^\d+\.\s+(.*)$/);
    if (ol) {
      if (listType !== "ol") {
        closeList();
        listType = "ol";
        out.push("<ol>");
      }
      out.push(`<li>${inline(ol[1])}</li>`);
      continue;
    }
    closeList();
    out.push(`<p>${inline(line)}</p>`);
  }
  closeList();
  return out.join("");
}

function renderMessage(div, text, kind = "bot") {
  if (kind === "bot") {
    div.innerHTML = formatMarkdown(text);
  } else {
    div.textContent = text;
  }
}

function addMessage(text, kind) {
  const div = document.createElement("div");
  div.className = `msg ${kind}`;
  renderMessage(div, text, kind);
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  return div;
}

/**
 * Sends a message to the onboarding assistant and returns its reply.
 * TODO: replace with the real agent (sessions, streaming, approvals).
 */
async function askAssistant(message) {
  const res = await fetch("/api/assistant", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ employee_id: employeeId, message, session_id: sessionId }),
  });
  if (!res.ok) throw new Error(`Assistant error ${res.status}`);
  const data = await res.json();
  sessionId = data.session_id;
  return data;
}

bubble.addEventListener("click", () => {
  panel.hidden = !panel.hidden;
  if (!panel.hidden) input.focus();
});
document.getElementById("assistant-close").addEventListener("click", () => (panel.hidden = true));

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  addMessage(text, "user");
  try {
    const data = await askAssistant(text);
    addMessage(data.reply, data.available ? "bot" : "notice");
  } catch (err) {
    addMessage("Something went wrong. Please try again.", "notice");
  }
});
