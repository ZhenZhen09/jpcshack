const form = document.querySelector("#chat-form");
const input = document.querySelector("#message");
const sendButton = document.querySelector("#send");
const transcript = document.querySelector("#transcript");
const welcome = document.querySelector("#welcome");
const feedback = document.querySelector("#feedback");
const completion = document.querySelector("#completion");
const promptMeter = document.querySelector("#prompt-meter");
let challengeClosed = false;
let promptStatusLoaded = false;
let requestInFlight = false;

function showProgress(result) {
  const guide = result.guidance;
  if (typeof result.solved !== "boolean" || !guide ||
      !Number.isInteger(guide.step) || guide.step < 1 || guide.step > 6 ||
      ![guide.title, guide.hint, guide.example].every(value => typeof value === "string")) {
    throw new Error("Invalid challenge progress");
  }
  completion.hidden = !result.solved;
}

function setBusy(busy) {
  requestInFlight = busy;
  const unavailable = busy || challengeClosed || !promptStatusLoaded;
  input.disabled = unavailable;
  sendButton.disabled = unavailable;
  sendButton.textContent = busy ? "…" : "↑";
  sendButton.setAttribute("aria-label", busy ? "Sending message" : "Send message");
  form.setAttribute("aria-busy", String(busy));
}

function updatePromptMeter(data) {
  if (!Number.isInteger(data.prompts_used) || !Number.isInteger(data.prompts_remaining) ||
      data.prompt_limit !== 20 || typeof data.closed !== "boolean") {
    throw new Error("Prompt limit status is invalid.");
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

function addMessage(speaker, text, className, concealFlag = false, artifact = null) {
  const article = document.createElement("article");
  article.className = `message ${className}`;
  const label = document.createElement("p");
  label.className = "speaker";
  label.textContent = speaker;
  const content = document.createElement("p");
  content.className = "message-text";
  const flag = className === "bot-message" && concealFlag ? /THM\{[^}]+\}/.exec(text) : null;
  if (flag) {
    const concealed = document.createElement("span");
    concealed.className = "concealed-flag";
    concealed.textContent = flag[0];
    content.append(text.slice(0, flag.index), concealed, text.slice(flag.index + flag[0].length));
  } else {
    content.textContent = text;
  }
  const body = document.createElement("div");
  body.className = "message-body";
  body.append(label, content);
  if (className === "bot-message" && artifact &&
      artifact.src === "/archive-clue.svg" && typeof artifact.alt === "string") {
    const image = document.createElement("img");
    image.className = "message-artifact";
    image.src = artifact.src;
    image.alt = artifact.alt;
    body.append(image);
  }
  if (className === "bot-message") {
    const avatar = document.createElement("span");
    avatar.className = "avatar";
    avatar.setAttribute("aria-hidden", "true");
    avatar.textContent = "N";
    article.append(avatar);
    label.textContent = "Northstar Assistant";
  }
  article.append(body);
  transcript.append(article);
  transcript.scrollTop = transcript.scrollHeight;
  return article;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  feedback.textContent = "";
  if (challengeClosed || requestInFlight || !promptStatusLoaded) return;
  if (!message) {
    feedback.textContent = "Enter a message before sending.";
    input.focus();
    return;
  }

  welcome.hidden = true;
  transcript.hidden = false;
  const userMessage = addMessage("You", message, "user-message");
  input.value = "";
  setBusy(true);
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const result = await response.json();
    if (!response.ok || typeof result.reply !== "string" || typeof result.solved !== "boolean") {
      throw new Error("server");
    }
    showProgress(result);
    updatePromptMeter(result);
    addMessage("Northstar Assistant", result.reply, "bot-message", result.solved, result.artifact);
  } catch {
    userMessage.remove();
    feedback.textContent = "Could not reach the assistant. Check that the local server is running, then try again.";
    input.value = message;
  } finally {
    setBusy(false);
    input.focus();
  }
});

async function restoreProgress() {
  setBusy(true);
  try {
    const response = await fetch("/api/session", { cache: "no-store" });
    if (!response.ok) throw new Error("server");
    const result = await response.json();
    showProgress(result);
    updatePromptMeter(result);
    if (result.guidance.step > 1 || result.solved) {
      welcome.hidden = true;
      transcript.hidden = false;
      addMessage("Northstar Assistant", `Your investigation progress is saved for this session. ${result.guidance.hint}`, "bot-message");
    }
  } catch {
    feedback.textContent = "Could not load your progress. Reload the page to reconnect.";
    promptMeter.textContent = "Prompt limit status unavailable. Reload this page to reconnect.";
  } finally {
    setBusy(false);
  }
}

restoreProgress();
