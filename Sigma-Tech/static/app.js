(() => {
  const data = document.getElementById("baseline-data");
  const canvas = document.getElementById("pixel-grid");
  if (!data || !canvas) return;

  const original = JSON.parse(data.textContent);
  const pixels = original.map((row) => row.slice());
  const context = canvas.getContext("2d", { alpha: false });
  const cell = canvas.width / 32;
  const rowSelect = document.getElementById("selected-row");
  const columnSelect = document.getElementById("selected-column");
  const count = document.querySelector("#edit-count strong");
  const result = document.getElementById("result");
  const resultTitle = document.getElementById("result-title");
  const resultMessage = document.getElementById("result-message");
  const announcer = document.getElementById("announcer");
  const checkButton = document.getElementById("check-image");
  let selectedRow = 10;
  let selectedColumn = 10;

  for (let index = 0; index < 32; index += 1) {
    rowSelect.add(new Option(String(index), String(index)));
    columnSelect.add(new Option(String(index), String(index)));
  }
  rowSelect.value = String(selectedRow);
  columnSelect.value = String(selectedColumn);

  const editCount = () => pixels.reduce(
    (total, row, rowIndex) => total + row.reduce(
      (rowTotal, value, columnIndex) => rowTotal + Number(value !== original[rowIndex][columnIndex]), 0
    ), 0
  );

  function draw() {
    for (let row = 0; row < 32; row += 1) {
      for (let column = 0; column < 32; column += 1) {
        context.fillStyle = pixels[row][column] ? "#d9f2dc" : "#18211c";
        context.fillRect(column * cell, row * cell, cell, cell);
        context.strokeStyle = "#344239";
        context.lineWidth = 0.55;
        context.strokeRect(column * cell, row * cell, cell, cell);
      }
    }
    context.strokeStyle = "#f3c77b";
    context.lineWidth = 2;
    context.strokeRect(selectedColumn * cell + 1, selectedRow * cell + 1, cell - 2, cell - 2);
    count.textContent = String(editCount());
    rowSelect.value = String(selectedRow);
    columnSelect.value = String(selectedColumn);
  }

  function setResult(title, message, state = "") {
    resultTitle.textContent = title;
    resultMessage.textContent = message;
    result.dataset.state = state;
    announcer.textContent = `${title}. ${message}`;
  }

  function togglePixel(row = selectedRow, column = selectedColumn) {
    const wasEdited = pixels[row][column] !== original[row][column];
    if (!wasEdited && editCount() >= 5) {
      setResult("Edit limit reached", "Reset a changed pixel before adding another one.", "error");
      return;
    }
    pixels[row][column] = 1 - pixels[row][column];
    selectedRow = row;
    selectedColumn = column;
    draw();
    setResult("Image changed", `Pixel row ${row}, column ${column} is now ${pixels[row][column] ? "white" : "black"}.`);
  }

  canvas.addEventListener("pointerup", (event) => {
    const bounds = canvas.getBoundingClientRect();
    const column = Math.min(31, Math.floor(((event.clientX - bounds.left) / bounds.width) * 32));
    const row = Math.min(31, Math.floor(((event.clientY - bounds.top) / bounds.height) * 32));
    togglePixel(row, column);
    canvas.focus();
  });

  canvas.addEventListener("keydown", (event) => {
    const movement = {
      ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1]
    };
    if (movement[event.key]) {
      event.preventDefault();
      selectedRow = Math.max(0, Math.min(31, selectedRow + movement[event.key][0]));
      selectedColumn = Math.max(0, Math.min(31, selectedColumn + movement[event.key][1]));
      draw();
      announcer.textContent = `Selected row ${selectedRow}, column ${selectedColumn}, ${pixels[selectedRow][selectedColumn] ? "white" : "black"}.`;
    } else if (event.key === " " || event.key === "Enter") {
      event.preventDefault();
      togglePixel();
    }
  });

  rowSelect.addEventListener("change", () => { selectedRow = Number(rowSelect.value); draw(); });
  columnSelect.addEventListener("change", () => { selectedColumn = Number(columnSelect.value); draw(); });
  document.getElementById("toggle-pixel").addEventListener("click", () => togglePixel());
  document.getElementById("reset-image").addEventListener("click", () => {
    for (let row = 0; row < 32; row += 1) pixels[row] = original[row].slice();
    draw();
    setResult("Image reset", "The original badge image has been restored.");
  });

  checkButton.addEventListener("click", async () => {
    checkButton.disabled = true;
    setResult("Reviewing image", "The classifier is checking the submitted badge.");
    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pixels })
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.error || "The image could not be reviewed.");
      if (body.solved) {
        setResult("Audit complete", `The model returned ${body.prediction} at ${(body.confidence * 100).toFixed(1)}% confidence. ${body.flag}`, "success");
      } else {
        setResult("Model prediction", `${body.prediction} at ${(body.confidence * 100).toFixed(1)}% confidence. ${body.edits} of 5 changed pixels used.`);
      }
    } catch (error) {
      setResult("Review failed", error.message, "error");
    } finally {
      checkButton.disabled = false;
    }
  });

  draw();
})();
