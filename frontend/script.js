// ============================================================
// Eurus AI Employee Copilot — frontend logic
// Talks to the FastAPI backend endpoints:
//   GET  /health
//   POST /ingest
//   POST /chat
//   POST /proposal
//   POST /email
//   POST /meeting/summarize
// ============================================================

const DEFAULT_API_BASE = "http://localhost:8000/api/v1";
const STORAGE_KEY = "eurus_copilot_api_base";

let API_BASE = localStorage.getItem(STORAGE_KEY) || DEFAULT_API_BASE;

// ---------- small utilities ----------

function logLine(text, type = "") {
  const el = document.getElementById("consoleLines");
  const span = document.createElement("span");
  if (type) span.classList.add(type);
  const time = new Date().toLocaleTimeString([], { hour12: false });
  span.textContent = `[${time}] ${text}`;
  el.innerHTML = "";
  el.appendChild(span);
}

function setBtnLoading(button, loading) {
  const label = button.querySelector(".btn-label");
  const spinner = button.querySelector(".spinner");
  button.disabled = loading;
  if (spinner) spinner.hidden = !loading;
  if (label) label.style.opacity = loading ? 0.6 : 1;
}

async function apiPost(path, body) {
  const url = `${API_BASE}${path}`;
  logLine(`POST ${path} …`);
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const errJson = await res.json();
      detail = errJson.detail ? JSON.stringify(errJson.detail) : detail;
    } catch (_) {}
    logLine(`POST ${path} failed — ${detail}`, "err");
    throw new Error(detail);
  }
  logLine(`POST ${path} succeeded`, "ok");
  return res.json();
}

function copyToClipboard(text, button) {
  navigator.clipboard.writeText(text).then(() => {
    const original = button.textContent;
    button.textContent = "Copied";
    setTimeout(() => (button.textContent = original), 1400);
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// Shared browser speech-recognition check — used by both the chat mic
// button and the meeting live-recording panel.
const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;

// ------------------------------------------------------------
// Sticky-scroll helpers
//
// FIX HISTORY: the first version did an unconditional
// `container.scrollTop = container.scrollHeight` on every reveal tick,
// which yanked the view back down even if the user had scrolled up to
// read from the start.
//
// A second attempt tried tracking a "shouldAutoScroll" flag updated via
// a `scroll` event listener — but that has a race condition: the typing
// loop forces scrollTop to the bottom roughly every 20ms, so a user's
// manual scroll gets overwritten by the very next tick before the
// `scroll` event even has a chance to update the flag. It felt "stuck".
//
// THE ACTUAL FIX: don't cache a flag at all. Check the container's LIVE
// scroll position fresh, every single frame, immediately before deciding
// whether to auto-scroll. Since this check happens synchronously right
// before the DOM mutation (no async event in between), it always sees
// exactly where the user currently is — including a scroll they made a
// few milliseconds ago. If they're not near the bottom, we skip
// scrolling that frame, full stop. If they scroll back down to the
// bottom themselves, auto-follow naturally resumes — same as
// ChatGPT/Claude's own chat windows.
// ------------------------------------------------------------
const NEAR_BOTTOM_PX = 120;

function isNearBottom(container, threshold = NEAR_BOTTOM_PX) {
  if (!container) return true;
  return container.scrollHeight - container.scrollTop - container.clientHeight < threshold;
}

function scrollToBottom(container) {
  if (!container) return;
  container.scrollTop = container.scrollHeight;
}

// ------------------------------------------------------------
// typeText — reveals text word by word with a visible cursor.
//
// Uses requestAnimationFrame and measures real elapsed time each frame,
// so the reveal rate is tied to a clock instead of a chain of timers —
// it can't bunch up (setTimeout can get throttled and cause the text to
// "jump" in all at once instead of animating).
// ------------------------------------------------------------
function typeText(el, fullText, scrollContainer = null, { msPerToken = 26 } = {}) {
  el.textContent = "";
  const cursor = document.createElement("span");
  cursor.className = "typing-cursor";

  // Splitting on whitespace-as-its-own-token keeps spacing exact while
  // still giving us discrete steps to animate through.
  const tokens = fullText.split(/(\s+)/);
  let shown = 0;
  let startTime = null;

  return new Promise((resolve) => {
    function frame(timestamp) {
      if (startTime === null) startTime = timestamp;
      const elapsed = timestamp - startTime;
      const target = Math.min(tokens.length, Math.floor(elapsed / msPerToken));

      if (target > shown) {
        // Live check, right before mutating — this is the fix. No
        // cached flag, no event listener, no race window.
        const nearBottom = isNearBottom(scrollContainer);

        shown = target;
        el.textContent = tokens.slice(0, shown).join("");
        el.appendChild(cursor);

        if (nearBottom) {
          scrollToBottom(scrollContainer);
        }
      }

      if (shown < tokens.length) {
        requestAnimationFrame(frame);
      } else {
        cursor.remove();
        resolve();
      }
    }
    requestAnimationFrame(frame);
  });
}

// ---------- navigation ----------

const navItems = document.querySelectorAll(".nav-item");
const views = document.querySelectorAll(".view");

navItems.forEach((item) => {
  item.addEventListener("click", () => {
    navItems.forEach((n) => n.classList.remove("active"));
    views.forEach((v) => v.classList.remove("active"));
    item.classList.add("active");
    document.getElementById(`view-${item.dataset.view}`).classList.add("active");
  });
});

// ---------- connection / settings ----------

const connDot = document.getElementById("connDot");
const connLabel = document.getElementById("connLabel");
const settingsBtn = document.getElementById("settingsBtn");
const settingsModal = document.getElementById("settingsModal");
const apiBaseInput = document.getElementById("apiBaseInput");
const settingsSave = document.getElementById("settingsSave");
const settingsCancel = document.getElementById("settingsCancel");
const modalStatus = document.getElementById("modalStatus");

async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`, { method: "GET" });
    if (!res.ok) throw new Error("bad status");
    connDot.className = "dot online";
    connLabel.textContent = "Backend connected";
    return true;
  } catch (e) {
    connDot.className = "dot offline";
    connLabel.textContent = "Backend unreachable";
    return false;
  }
}

settingsBtn.addEventListener("click", () => {
  apiBaseInput.value = API_BASE;
  modalStatus.textContent = "";
  settingsModal.hidden = false;
  apiBaseInput.focus();
});

settingsCancel.addEventListener("click", () => (settingsModal.hidden = true));

settingsSave.addEventListener("click", async () => {
  const newBase = apiBaseInput.value.trim().replace(/\/$/, "");
  if (!newBase) return;
  modalStatus.textContent = "Testing connection…";
  const previous = API_BASE;
  API_BASE = newBase;
  const ok = await checkHealth();
  if (ok) {
    localStorage.setItem(STORAGE_KEY, API_BASE);
    modalStatus.textContent = "Connected. Saved.";
    setTimeout(() => (settingsModal.hidden = true), 700);
  } else {
    API_BASE = previous;
    modalStatus.textContent = "Could not reach that URL — reverted.";
  }
});

// initial health check + periodic re-check
checkHealth();
setInterval(checkHealth, 20000);

// ============================================================
// Chat / RAG
// ============================================================

const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatWindow = document.getElementById("chatWindow");
const chatEmpty = document.getElementById("chatEmpty");

function appendMessage(role, text, sources) {
  if (chatEmpty) chatEmpty.remove();

  // Live check, taken right before we add anything — decides whether
  // appending this message should pull the view down or leave it alone.
  const nearBottomBeforeAppend = isNearBottom(chatWindow);

  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;

  const roleLabel = document.createElement("div");
  roleLabel.className = "msg-role";
  roleLabel.textContent = role === "user" ? "You" : "Copilot";

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";

  wrap.appendChild(roleLabel);
  wrap.appendChild(bubble);

  if (sources && sources.length) {
    const src = document.createElement("div");
    src.className = "msg-sources";
    src.textContent = `Sources: ${sources.join(", ")}`;
    wrap.appendChild(src);
  }

  chatWindow.appendChild(wrap);

  if (role === "user") {
    // The user just sent this themselves — always follow it down,
    // same as any messaging app. There's nothing above worth protecting
    // a scroll position for in this specific case.
    scrollToBottom(chatWindow);
    bubble.textContent = text;
  } else {
    // Assistant message: respect whatever the user was doing a moment
    // ago. If they'd scrolled up to reread something, don't yank them
    // back down just because a reply arrived. typeText() then takes
    // over with its own live, per-frame check for the rest of the
    // animation — see the comment above typeText's definition.
    if (nearBottomBeforeAppend) {
      scrollToBottom(chatWindow);
    }
    typeText(bubble, text, chatWindow, { msPerToken: 22 });
  }
}

async function askQuestion(question) {
  appendMessage("user", question);
  const button = chatForm.querySelector("button");
  setBtnLoading(button, true);
  try {
    const data = await apiPost("/chat", { question });
    appendMessage("assistant", data.answer, data.sources);
  } catch (err) {
    appendMessage("assistant", `Error: ${err.message}`);
  } finally {
    setBtnLoading(button, false);
  }
}

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const q = chatInput.value.trim();
  if (!q) return;
  chatInput.value = "";
  askQuestion(q);
});

document.querySelectorAll(".suggestion").forEach((btn) => {
  btn.addEventListener("click", () => askQuestion(btn.dataset.q));
});

// ---- Voice input for chat: speak the question, it fills the input and
// auto-sends once you stop talking. Uses the same browser Speech API as
// the meeting recorder, but in single-utterance mode (stops itself after
// a pause, instead of listening continuously).

const chatMicBtn = document.getElementById("chatMicBtn");
let chatRecognition = null;
let chatListening = false;

if (!SpeechRecognitionAPI) {
  chatMicBtn.disabled = true;
  chatMicBtn.title = "Voice input isn't supported in this browser — use Chrome or Edge";
} else {
  chatRecognition = new SpeechRecognitionAPI();
  chatRecognition.continuous = false;   // stop automatically after one utterance
  chatRecognition.interimResults = true; // show partial text while speaking
  chatRecognition.lang = "en-US";

  chatRecognition.onresult = (event) => {
    let text = "";
    for (let i = 0; i < event.results.length; i++) {
      text += event.results[i][0].transcript;
    }
    chatInput.value = text;
  };

  chatRecognition.onerror = (event) => {
    if (event.error !== "no-speech") logLine(`Voice input error — ${event.error}`, "err");
    setChatMicListening(false);
  };

  chatRecognition.onend = () => {
    setChatMicListening(false);
    const q = chatInput.value.trim();
    if (q) {
      chatInput.value = "";
      askQuestion(q); // auto-send, no need to press Ask
    }
  };

  chatMicBtn.addEventListener("click", () => {
    if (chatListening) {
      chatRecognition.stop();
    } else {
      chatInput.value = "";
      chatRecognition.start();
      setChatMicListening(true);
    }
  });
}

function setChatMicListening(listening) {
  chatListening = listening;
  chatMicBtn.classList.toggle("listening", listening);
  chatMicBtn.title = listening ? "Listening… click to stop" : "Ask by voice";
}

// ============================================================
// Proposal generator
// ============================================================

const proposalForm = document.getElementById("proposalForm");
const proposalResult = document.getElementById("proposalResult");
const proposalText = document.getElementById("proposalText");
const proposalCopy = document.getElementById("proposalCopy");
const proposalPdfLink = document.getElementById("proposalPdfLink");
const mainPanel = document.querySelector(".main");

proposalForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const button = proposalForm.querySelector("button");
  const client_name = document.getElementById("proposalClient").value.trim();
  const requirement = document.getElementById("proposalRequirement").value.trim();

  setBtnLoading(button, true);
  try {
    const data = await apiPost("/proposal", { client_name, requirement });
    proposalResult.hidden = false;

    let fullText = data.proposal_text;
    if (data.pdf_path && !/^https?:\/\//.test(data.pdf_path)) {
      fullText += `\n\n---\nPDF saved on server at: ${data.pdf_path}`;
    }
    await typeText(proposalText, fullText, mainPanel);

    if (data.pdf_path && /^https?:\/\//.test(data.pdf_path)) {
      proposalPdfLink.href = data.pdf_path;
      proposalPdfLink.hidden = false;
    }
  } catch (err) {
    proposalText.textContent = `Error: ${err.message}`;
    proposalResult.hidden = false;
  } finally {
    setBtnLoading(button, false);
  }
});

proposalCopy.addEventListener("click", () => copyToClipboard(proposalText.textContent, proposalCopy));

// ============================================================
// Email drafting
// ============================================================

const emailForm = document.getElementById("emailForm");
const emailResult = document.getElementById("emailResult");
const emailText = document.getElementById("emailText");
const emailCopy = document.getElementById("emailCopy");
const emailType = document.getElementById("emailType");
const incomingEmailWrap = document.getElementById("incomingEmailWrap");

function toggleIncomingField() {
  incomingEmailWrap.style.display = emailType.value === "reply" ? "flex" : "none";
}
emailType.addEventListener("change", toggleIncomingField);
toggleIncomingField();

emailForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const button = emailForm.querySelector("button");
  const email_type = emailType.value;
  const context = document.getElementById("emailContext").value.trim();
  const incoming_email = document.getElementById("emailIncoming").value.trim() || null;

  setBtnLoading(button, true);
  try {
    const data = await apiPost("/email", { email_type, context, incoming_email });
    emailResult.hidden = false;
    await typeText(emailText, data.draft, mainPanel);
  } catch (err) {
    emailText.textContent = `Error: ${err.message}`;
    emailResult.hidden = false;
  } finally {
    setBtnLoading(button, false);
  }
});

emailCopy.addEventListener("click", () => copyToClipboard(emailText.textContent, emailCopy));

// ============================================================
// Meeting summarizer
// ============================================================

const meetingForm = document.getElementById("meetingForm");
const meetingResult = document.getElementById("meetingResult");
const meetingText = document.getElementById("meetingText");
const meetingCopy = document.getElementById("meetingCopy");
const meetingTranscriptEl = document.getElementById("meetingTranscript");

meetingForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const button = meetingForm.querySelector("button");
  const transcript = meetingTranscriptEl.value.trim();

  setBtnLoading(button, true);
  try {
    const data = await apiPost("/meeting/summarize", { transcript });
    meetingResult.hidden = false;
    await typeText(meetingText, data.summary, mainPanel);
  } catch (err) {
    meetingText.textContent = `Error: ${err.message}`;
    meetingResult.hidden = false;
  } finally {
    setBtnLoading(button, false);
  }
});

meetingCopy.addEventListener("click", () => copyToClipboard(meetingText.textContent, meetingCopy));

// ============================================================
// Upload full recording — captures every participant (Zoom/Teams/Meet)
// Sends the file to /meeting/summarize-from-recording, which extracts
// audio (ffmpeg), transcribes it (Groq Whisper), then summarizes it.
// ============================================================

const uploadBtn = document.getElementById("uploadBtn");
const uploadSpinner = document.getElementById("uploadSpinner");
const uploadDot = document.getElementById("uploadDot");
const uploadStatus = document.getElementById("uploadStatus");
const recordingFileInput = document.getElementById("recordingFile");

uploadBtn.addEventListener("click", async () => {
  const file = recordingFileInput.files[0];
  if (!file) {
    uploadStatus.textContent = "Choose a recording file first.";
    return;
  }

  uploadBtn.disabled = true;
  uploadSpinner.hidden = false;
  uploadDot.classList.add("recording");
  uploadStatus.textContent = `Processing "${file.name}" — extracting audio, transcribing, summarizing… this can take a minute for longer recordings.`;
  logLine(`Uploading recording ${file.name} …`);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${API_BASE}/meeting/summarize-from-recording`, {
      method: "POST",
      body: formData, // no Content-Type header — the browser sets the multipart boundary
    });

    if (!res.ok) {
      let detail = res.statusText;
      try {
        const errJson = await res.json();
        detail = errJson.detail || detail;
      } catch (_) {}
      throw new Error(detail);
    }

    const data = await res.json();
    logLine("Recording processed successfully", "ok");

    if (data.transcript) {
      meetingTranscriptEl.value = data.transcript; // let the user see/edit what Whisper heard
    }
    meetingResult.hidden = false;
    await typeText(meetingText, data.summary, mainPanel);

    uploadStatus.textContent = `Done — "${file.name}" processed. Transcript filled in above, summary below.`;
  } catch (err) {
    logLine(`Recording upload failed — ${err.message}`, "err");
    uploadStatus.textContent = `Failed: ${err.message}`;
  } finally {
    uploadBtn.disabled = false;
    uploadSpinner.hidden = true;
    uploadDot.classList.remove("recording");
  }
});

// ============================================================
// Live meeting recording (browser Web Speech API — Chrome/Edge)
// Fills the transcript textarea above in real time, like live captions.
// ============================================================

const recStartBtn = document.getElementById("recStartBtn");
const recStopBtn = document.getElementById("recStopBtn");
const recDot = document.getElementById("recDot");
const recStatus = document.getElementById("recStatus");
const livePreview = document.getElementById("livePreview");

let recognition = null;
let recFinalTranscript = "";
let isRecording = false;

if (!SpeechRecognitionAPI) {
  recStartBtn.disabled = true;
  recStatus.textContent = "Live transcript isn't supported in this browser — use Chrome or Edge, or paste a transcript below.";
} else {
  recognition = new SpeechRecognitionAPI();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = "en-US";

  recognition.onresult = (event) => {
    let interim = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const chunk = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        recFinalTranscript += chunk + " ";
      } else {
        interim += chunk;
      }
    }
    const nearBottomBeforeUpdate = isNearBottom(livePreview);
    livePreview.classList.add("has-content");
    livePreview.innerHTML =
      escapeHtml(recFinalTranscript) + '<span class="interim">' + escapeHtml(interim) + "</span>";
    if (nearBottomBeforeUpdate) {
      scrollToBottom(livePreview);
    }
    meetingTranscriptEl.value = recFinalTranscript;
  };

  recognition.onerror = (event) => {
    logLine(`Live transcript error — ${event.error}`, "err");
    if (event.error !== "no-speech") stopRecording();
  };

  recognition.onend = () => {
    // the API sometimes stops itself after a pause — restart if the
    // user hasn't explicitly clicked Stop
    if (isRecording) recognition.start();
  };
}

function startRecording() {
  recFinalTranscript = meetingTranscriptEl.value ? meetingTranscriptEl.value.trim() + " " : "";
  isRecording = true;
  recognition.start();
  recStartBtn.disabled = true;
  recStopBtn.disabled = false;
  recDot.classList.add("recording");
  recStatus.textContent = "Recording live…";
  logLine("Live transcript started");
}

function stopRecording() {
  isRecording = false;
  recStopBtn.disabled = true;
  try { recognition.stop(); } catch (_) {}
  recStartBtn.disabled = false;
  recDot.classList.remove("recording");
  recStatus.textContent = "Stopped — transcript ready below, edit if needed then Summarize.";
  logLine("Live transcript stopped", "ok");
}

recStartBtn?.addEventListener("click", startRecording);
recStopBtn?.addEventListener("click", stopRecording);

// ============================================================
// Knowledge base ingestion
// ============================================================

const ingestForm = document.getElementById("ingestForm");
const ingestLog = document.getElementById("ingestLog");
let ingestEmptyRemoved = false;

function addIngestRow(source, status, chunks) {
  if (!ingestEmptyRemoved) {
    ingestLog.innerHTML = "";
    ingestEmptyRemoved = true;
  }
  const row = document.createElement("div");
  row.className = "log-row";

  const src = document.createElement("span");
  src.className = "src";
  src.textContent = source;
  src.title = source;

  const chunkSpan = document.createElement("span");
  chunkSpan.textContent = chunks ?? "—";

  const pill = document.createElement("span");
  pill.className = `status-pill ${status}`;
  pill.textContent = status === "ok" ? "Indexed" : status === "fail" ? "Failed" : "Pending";

  row.appendChild(src);
  row.appendChild(chunkSpan);
  row.appendChild(pill);
  ingestLog.prepend(row);
  return row;
}

ingestForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const button = ingestForm.querySelector("button");
  const urlInput = document.getElementById("ingestUrl");
  const url = urlInput.value.trim();
  if (!url) return;

  setBtnLoading(button, true);
  const row = addIngestRow(url, "pending", null);

  try {
    const data = await apiPost("/ingest", { url });
    row.remove();
    addIngestRow(data.source, "ok", data.chunks_indexed);
    urlInput.value = "";
  } catch (err) {
    row.remove();
    addIngestRow(url, "fail", null);
  } finally {
    setBtnLoading(button, false);
  }
});