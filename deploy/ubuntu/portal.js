"use strict";

const host = window.location.hostname;
const useOnDemandLauncher = window.location.port === "8080" && ["127.0.0.1", "localhost"].includes(host);
const challengeByPort = {
  "5000": "ancient-bedrock",
  "5001": "sigma-tech",
  "8000": "prompt-me-maybe",
  "8100": "dolos-lab",
};

for (const link of document.querySelectorAll("[data-port]")) {
  const slug = challengeByPort[link.dataset.port];
  if (!slug) continue;
  if (useOnDemandLauncher) {
    link.href = `/launch/${slug}`;
    link.querySelector(".url").textContent = "Start when selected";
  } else {
    const port = link.dataset.port;
    const address = `${window.location.protocol}//${host}:${port}`;
    link.href = address;
    link.querySelector(".url").textContent = address;
  }
}

for (const link of document.querySelectorAll("[data-local]")) {
  const path = new URL(link.dataset.local, window.location.href).pathname;
  const slug = path.split("/").filter(Boolean).pop();
  if (!slug) continue;
  if (useOnDemandLauncher) {
    link.href = `/open/${slug}`;
  } else {
    link.href = new URL(link.dataset.local, window.location.href).href;
  }
}
