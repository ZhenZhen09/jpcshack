"use strict";

const host = window.location.hostname;
for (const link of document.querySelectorAll("[data-port]")) {
  const port = link.dataset.port;
  const address = `${window.location.protocol}//${host}:${port}`;
  link.href = address;
  link.querySelector(".url").textContent = address;
}
