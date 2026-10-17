"use strict";

const transcript = document.querySelector("#transcript");
const form = document.querySelector("#chat-form");
const input = document.querySelector("#message");
const sendButton = document.querySelector("#send-button");
const status = document.querySelector("#status");
const count = document.querySelector("#character-count");

function addMessage(role, text) {
  const article = document.createElement("article");
  article.className = `message ${role === "user" ? "user-message" : "assistant-message"}`;

  const label = document.createElement("span");
  label.className = "message-label";
  label.textContent = role === "user" ? "YOU" : "DOLOS ASSISTANT";

  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  article.append(label, paragraph);
  transcript.append(article);
  transcript.scrollTop = transcript.scrollHeight;
}

function updateCount() {
  count.textContent = `${input.value.length} / 500`;
}

async function postMessage(message) {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
    credentials: "same-origin",
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "The request could not be processed.");
  if (typeof result.reply !== "string" || typeof result.solved !== "boolean") {
    throw new Error("The assistant returned an invalid response.");
  }
  return result;
}

async function restoreSession() {
  try {
    const response = await fetch("/api/session", { credentials: "same-origin" });
    const session = await response.json();
    if (!response.ok || typeof session.guidance?.hint !== "string") {
      throw new Error("The current investigation could not be restored.");
    }
    status.textContent = session.solved
      ? "Challenge complete. Your investigation progress has been restored."
      : `Current lead: ${session.guidance.hint}`;
  } catch (error) {
    status.textContent = error instanceof Error ? error.message : "Could not restore this session.";
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message || sendButton.disabled) return;

  addMessage("user", message);
  input.value = "";
  updateCount();
  status.textContent = "";
  sendButton.disabled = true;
  input.disabled = true;

  try {
    const result = await postMessage(message);
    addMessage("assistant", result.reply);
    if (result.solved) {
      status.textContent = "Challenge complete. Copy the mock flag from the diagnostic report.";
    } else if (typeof result.guidance?.hint === "string") {
      status.textContent = `Current lead: ${result.guidance.hint}`;
    }
  } catch (error) {
    status.textContent = error instanceof Error ? error.message : "Connection error. Please try again.";
  } finally {
    sendButton.disabled = false;
    input.disabled = false;
    input.focus();
  }
});

input.addEventListener("input", updateCount);
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

updateCount();
restoreSession();
