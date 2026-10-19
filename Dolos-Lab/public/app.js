"use strict";

const transcript = document.querySelector("#transcript");
const form = document.querySelector("#chat-form");
const input = document.querySelector("#message");
const sendButton = document.querySelector("#send-button");
const status = document.querySelector("#status");
const count = document.querySelector("#character-count");
const promptMeter = document.querySelector("#prompt-meter");
let challengeClosed = false;
let promptStatusLoaded = false;
let requestInFlight = false;

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

function setBusy(busy) {
  requestInFlight = busy;
  const unavailable = busy || challengeClosed || !promptStatusLoaded;
  sendButton.disabled = unavailable;
  input.disabled = unavailable;
}

function updatePromptMeter(data) {
  if (!Number.isInteger(data.prompts_used) || !Number.isInteger(data.prompts_remaining) ||
      data.prompt_limit !== 20 || typeof data.closed !== "boolean") {
    throw new Error("The prompt limit status is invalid.");
  }
  challengeClosed = data.closed;
  promptStatusLoaded = true;
  if (challengeClosed) {
    promptMeter.textContent = `Challenge closed · ${data.prompts_used} of ${data.prompt_limit} prompts used · ${data.prompts_remaining} remaining.`;
  } else if (data.prompts_remaining === 0) {
    promptMeter.textContent = `${data.prompts_used} of ${data.prompt_limit} prompts used · 0 remaining. The next prompt will close this challenge.`;
  } else {
    promptMeter.textContent = `${data.prompts_used} of ${data.prompt_limit} prompts used · ${data.prompts_remaining} remaining.`;
  }
  setBusy(requestInFlight);
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
  if (typeof result.reply !== "string" || typeof result.solved !== "boolean" ||
      !Number.isInteger(result.prompts_used) || !Number.isInteger(result.prompts_remaining) ||
      result.prompt_limit !== 20 || typeof result.closed !== "boolean") {
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
    updatePromptMeter(session);
    status.textContent = session.closed
      ? "Challenge closed by the prompt limit."
      : session.solved
      ? "Challenge complete. Your investigation progress has been restored."
      : `Current lead: ${session.guidance.hint}`;
  } catch (error) {
    promptMeter.textContent = "Prompt limit status unavailable. Reload this page to reconnect.";
    status.textContent = error instanceof Error ? error.message : "Could not restore this session.";
  } finally {
    setBusy(false);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message || sendButton.disabled || challengeClosed || !promptStatusLoaded) return;

  addMessage("user", message);
  input.value = "";
  updateCount();
  status.textContent = "";
  setBusy(true);

  try {
    const result = await postMessage(message);
    updatePromptMeter(result);
    addMessage("assistant", result.reply);
    if (result.closed) {
      status.textContent = "Challenge closed by the prompt limit.";
    } else if (result.solved) {
      status.textContent = "Challenge complete. Copy the mock flag from the diagnostic report.";
    } else if (typeof result.guidance?.hint === "string") {
      status.textContent = `Current lead: ${result.guidance.hint}`;
    }
  } catch (error) {
    status.textContent = error instanceof Error ? error.message : "Connection error. Please try again.";
  } finally {
    setBusy(false);
    if (!challengeClosed) input.focus();
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
