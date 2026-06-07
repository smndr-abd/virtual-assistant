/* ═══════════════════════════════════════════════════════
   VPA — script.js
   Custom cursor · Nav scroll · Counters · Pipeline reveal
   · Hero chat animation · Demo chatbot
═══════════════════════════════════════════════════════ */

"use strict";

/* ── CUSTOM CURSOR ──────────────────────────────────── */
const cursor      = document.getElementById("cursor");
const cursorTrail = document.getElementById("cursorTrail");
let mx = 0, my = 0, tx = 0, ty = 0;

document.addEventListener("mousemove", e => {
  mx = e.clientX; my = e.clientY;
  cursor.style.left = mx + "px";
  cursor.style.top  = my + "px";
});

(function animTrail() {
  tx += (mx - tx) * 0.18;
  ty += (my - ty) * 0.18;
  cursorTrail.style.left = tx + "px";
  cursorTrail.style.top  = ty + "px";
  requestAnimationFrame(animTrail);
})();

document.querySelectorAll("a, button, .sugg, .feat-card, .pillar").forEach(el => {
  el.addEventListener("mouseenter", () => cursor.style.transform = "translate(-50%,-50%) scale(2.5)");
  el.addEventListener("mouseleave", () => cursor.style.transform = "translate(-50%,-50%) scale(1)");
});

/* ── NAV SCROLL ─────────────────────────────────────── */
const nav = document.getElementById("nav");
window.addEventListener("scroll", () => {
  nav.classList.toggle("scrolled", window.scrollY > 60);
});

/* ── COUNTER ANIMATION ──────────────────────────────── */
function animateCounter(el, target, duration = 1400) {
  let start = null;
  const step = ts => {
    if (!start) start = ts;
    const progress = Math.min((ts - start) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 4);
    el.textContent = Math.floor(ease * target);
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = target;
  };
  requestAnimationFrame(step);
}

const counterObs = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const el = entry.target;
      animateCounter(el, parseInt(el.dataset.target));
      counterObs.unobserve(el);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll(".counter, .stat-num[data-target]").forEach(el => counterObs.observe(el));

/* ── PIPELINE STEPS REVEAL ──────────────────────────── */
const pipeObs = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const step = entry.target;
      const delay = (parseInt(step.dataset.step) - 1) * 120;
      setTimeout(() => step.classList.add("visible"), delay);
      pipeObs.unobserve(step);
    }
  });
}, { threshold: 0.2 });

document.querySelectorAll(".pipe-step").forEach(el => pipeObs.observe(el));

/* ── SPEED BARS ANIMATION ───────────────────────────── */
const speedObs = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.querySelectorAll(".speed-fill").forEach((bar, i) => {
        setTimeout(() => bar.classList.add("animated"), i * 150);
      });
      speedObs.unobserve(entry.target);
    }
  });
}, { threshold: 0.3 });

const speedSection = document.querySelector(".speed-breakdown");
if (speedSection) speedObs.observe(speedSection);

/* ── HERO CHAT ANIMATION ─────────────────────────────── */
const heroResponses = [
  "The current time is 3:45 PM 🕐",
  "Searching for Python tutorials… 🔍",
  "The answer is 42 🧮",
  "Defect logged on Line 3. Report ID: #0047 ✅",
  "Maintenance ticket submitted for Machine 7 🔧",
];
const heroQueries = [
  "What time is it?",
  "Search for Python tutorials",
  "Calculate 15 plus 27",
  "Report defect on line 3",
  "Maintenance for machine 7",
];

let heroIndex = 0;

function runHeroChat() {
  const chat   = document.getElementById("heroChat");
  const typing = document.getElementById("typingMsg");
  if (!chat || !typing) return;

  const query    = heroQueries[heroIndex % heroQueries.length];
  const response = heroResponses[heroIndex % heroResponses.length];
  heroIndex++;

  // Add user message
  const userMsg = document.createElement("div");
  userMsg.className = "msg msg-user";
  userMsg.textContent = query;
  chat.insertBefore(userMsg, typing);

  // Show typing
  typing.style.display = "flex";

  setTimeout(() => {
    typing.style.display = "none";
    const botMsg = document.createElement("div");
    botMsg.className = "msg msg-bot";
    botMsg.textContent = response;
    chat.insertBefore(botMsg, typing);

    // Trim old messages
    const msgs = chat.querySelectorAll(".msg:not(.typing)");
    if (msgs.length > 6) msgs[0].remove();
  }, 1200);
}

setInterval(runHeroChat, 3200);
setTimeout(runHeroChat, 1000);

/* ── DEMO CHATBOT ─────────────────────────────────────── */

// Simple in-browser intent classifier (keyword matching)
const INTENTS = [
  { name: "time",          keys: ["time","clock","hour","what time"],       icon: "⏰" },
  { name: "date",          keys: ["date","day","today","what day"],         icon: "📅" },
  { name: "search",        keys: ["search","google","find","look up"],      icon: "🔍" },
  { name: "calculate",     keys: ["calculate","plus","minus","times","add","subtract","multiply","divided","compute","math"],icon:"🧮"},
  { name: "joke",          keys: ["joke","funny","laugh","humor"],          icon: "😄" },
  { name: "weather",       keys: ["weather","rain","sunny","forecast","temperature"],icon:"🌤️"},
  { name: "greeting",      keys: ["hello","hi","hey","morning","evening","afternoon","greet"],icon:"👋"},
  { name: "report_defect", keys: ["defect","quality","issue","problem","fault","error","gap","alignment"],icon:"🏭"},
  { name: "check_status",  keys: ["status","count","production","units","output","line","how many"],icon:"📊"},
  { name: "maintenance",   keys: ["maintenance","repair","technician","machine","broken","fix","noise"],icon:"🔧"},
  { name: "shift_log",     keys: ["shift","handover","log","notes","report end"],icon:"📝"},
  { name: "email",         keys: ["email","send","notify","alert","message manager"],icon:"✉️"},
  { name: "farewell",      keys: ["bye","goodbye","exit","quit","see you"],  icon: "👋" },
];

const RESPONSES = {
  time:          () => `The current time is ${new Date().toLocaleTimeString("en-US",{hour:"2-digit",minute:"2-digit"})} ⏰`,
  date:          () => `Today is ${new Date().toLocaleDateString("en-US",{weekday:"long",year:"numeric",month:"long",day:"numeric"})} 📅`,
  search:        cmd => { const q = cmd.replace(/search|for|google|find|look\s*up/gi,"").trim(); return `Searching for "${q || "your query"}" on Google 🔍\n(In the real app, this opens your browser)` },
  calculate:     cmd => {
    try {
      let expr = cmd.replace(/calculate|compute|what\s*is|solve/gi,"")
        .replace(/plus/gi,"+").replace(/minus/gi,"-")
        .replace(/times|multiplied\s*by/gi,"*").replace(/divided\s*by/gi,"/")
        .replace(/[^0-9+\-*/.() ]/g,"").trim();
      if(!expr) return "Please say the numbers, e.g. 'calculate 15 plus 27' 🧮";
      const result = eval(expr);
      return `The answer is **${result}** 🧮`;
    } catch { return "I couldn't calculate that. Try: 'calculate 10 plus 5' 🧮"; }
  },
  joke:          () => {
    const jokes = [
      "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
      "How many data scientists to change a bulb? Just one, but they need 10,000 examples first! 💡",
      "Why did the ML model go to therapy? Too many issues with its training data! 🛋️",
      "What's a programmer's favorite place? The Foo Bar! 🍺",
    ];
    return jokes[Math.floor(Math.random()*jokes.length)];
  },
  weather:       cmd => {
    const city = cmd.replace(/weather|in|for|what|how|is|the|forecast/gi,"").trim() || "Seoul";
    return `Weather in ${city}: 22°C, partly cloudy ⛅\n(In the real app, this calls OpenWeatherMap API)`;
  },
  greeting:      () => {
    const h = new Date().getHours();
    const g = h<12?"Good morning":h<18?"Good afternoon":"Good evening";
    return `${g}! I'm your Virtual Personal Assistant. How can I help you today? 😊`;
  },
  report_defect: cmd => {
    const line = (cmd.match(/line\s*(\d+)/i)||[])[1]||"(unspecified)";
    const id   = Math.floor(Math.random()*9000+1000);
    return `✅ Defect reported!\n📍 Location: Line ${line}\n🔖 Report ID: #${id}\n🕐 Timestamp: ${new Date().toLocaleTimeString()}\n\n(In the real app, this saves to the factory database)`;
  },
  check_status:  cmd => {
    const line = (cmd.match(/line\s*(\d+)/i)||[])[1];
    const count = Math.floor(Math.random()*400+500);
    return line
      ? `📊 Line ${line} Status:\n✅ Units completed: ${count}\n⏱️ Last updated: ${new Date().toLocaleTimeString()}`
      : `📊 Total Production Today:\n✅ Total units: ${Math.floor(Math.random()*2000+2000)}\n(Connect to PO system for real data)`;
  },
  maintenance:   cmd => {
    const m = (cmd.match(/machine\s*(\d+)/i)||[])[1]||(cmd.match(/line\s*(\d+)/i)||[])[1]||"(unspecified)";
    const t = Math.floor(Math.random()*9000+1000);
    return `🔧 Maintenance request submitted!\n🖥️ Machine: ${m}\n🎫 Ticket ID: #${t}\n⚡ Priority: Normal\n\n(In the real app, this creates a ticket in your ERP)`;
  },
  shift_log:     () => `📝 Shift log saved!\n⏰ Timestamp: ${new Date().toLocaleString()}\n🔄 Shift: ${new Date().getHours()<14?"Morning":new Date().getHours()<22?"Afternoon":"Night"}\n\n(In the real app, this saves to the shift_logs.txt file)`,
  email:         () => `✉️ Email alert queued!\n📧 To: manager@company.com\n⏰ Time: ${new Date().toLocaleTimeString()}\n\n(In the real app, this sends via Gmail SMTP)`,
  farewell:      () => "Goodbye! Have a great day! 👋\n\nRefresh the page to start a new session.",
};

function classifyIntent(cmd) {
  const lower = cmd.toLowerCase();
  let best = { score: 0, intent: null };
  for (const intent of INTENTS) {
    const score = intent.keys.filter(k => lower.includes(k)).length;
    if (score > best.score) best = { score, intent: intent.name };
  }
  if (!best.intent) return null;
  return { intent: best.intent, icon: INTENTS.find(i=>i.name===best.intent).icon };
}

function addDemoMsg(text, isUser, intent) {
  const chat = document.getElementById("demoChat");
  const wrap = document.createElement("div");
  wrap.className = "demo-msg " + (isUser ? "user-msg" : "bot-msg");

  if (!isUser) {
    const av = document.createElement("div");
    av.className = "bot-avatar";
    av.textContent = "AI";
    wrap.appendChild(av);
  }

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";
  bubble.style.whiteSpace = "pre-wrap";

  // Bold **text**
  bubble.innerHTML = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  if (intent && !isUser) {
    const badge = document.createElement("div");
    badge.className = "intent-badge";
    badge.textContent = `Intent: ${intent.icon} ${intent.intent.replace(/_/g," ").toUpperCase()}`;
    bubble.appendChild(badge);
  }

  wrap.appendChild(bubble);
  chat.appendChild(wrap);
  chat.scrollTop = chat.scrollHeight;
}

function addTypingIndicator() {
  const chat = document.getElementById("demoChat");
  const wrap = document.createElement("div");
  wrap.className = "demo-msg bot-msg";
  wrap.id = "demoTyping";

  const av = document.createElement("div");
  av.className = "bot-avatar";
  av.textContent = "AI";

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";
  bubble.innerHTML = '<div style="display:flex;gap:5px;align-items:center"><span style="width:7px;height:7px;background:#64748B;border-radius:50%;animation:typingDot 1.2s ease-in-out infinite"></span><span style="width:7px;height:7px;background:#64748B;border-radius:50%;animation:typingDot 1.2s ease-in-out 0.2s infinite"></span><span style="width:7px;height:7px;background:#64748B;border-radius:50%;animation:typingDot 1.2s ease-in-out 0.4s infinite"></span></div>';

  wrap.appendChild(av);
  wrap.appendChild(bubble);
  chat.appendChild(wrap);
  chat.scrollTop = chat.scrollHeight;
}

function removeTyping() {
  const el = document.getElementById("demoTyping");
  if (el) el.remove();
}

function handleDemoInput() {
  const input = document.getElementById("demoInput");
  const cmd = input.value.trim();
  if (!cmd) return;
  input.value = "";

  addDemoMsg(cmd, true);

  addTypingIndicator();

  setTimeout(() => {
    removeTyping();
    const classified = classifyIntent(cmd);
    if (!classified) {
      addDemoMsg(
        "I'm not sure what you mean. Try saying:\n• \"What time is it?\"\n• \"Report defect on line 3\"\n• \"Calculate 15 plus 27\"",
        false, null
      );
    } else {
      const respFn = RESPONSES[classified.intent];
      const response = respFn ? respFn(cmd) : "Got it!";
      addDemoMsg(response, false, classified);
    }
  }, 700 + Math.random() * 400);
}

document.getElementById("demoSend").addEventListener("click", handleDemoInput);
document.getElementById("demoInput").addEventListener("keydown", e => {
  if (e.key === "Enter") handleDemoInput();
});
document.querySelectorAll(".sugg").forEach(btn => {
  btn.addEventListener("click", () => {
    document.getElementById("demoInput").value = btn.dataset.msg;
    handleDemoInput();
  });
});

/* ── SMOOTH SECTION FADE-IN ─────────────────────────── */
const fadeObs = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = "1";
      entry.target.style.transform = "translateY(0)";
      fadeObs.unobserve(entry.target);
    }
  });
}, { threshold: 0.08 });

document.querySelectorAll(".pillar, .feat-card, .ml-card, .metric-card").forEach(el => {
  el.style.opacity = "0";
  el.style.transform = "translateY(24px)";
  el.style.transition = "opacity 0.6s ease, transform 0.6s ease";
  fadeObs.observe(el);
});

/* ── HAMBURGER ──────────────────────────────────────── */
const hamburger = document.getElementById("hamburger");
hamburger?.addEventListener("click", () => {
  const links = nav.querySelector(".nav-links");
  if (!links) return;
  links.style.display = links.style.display === "flex" ? "none" : "flex";
  links.style.flexDirection = "column";
  links.style.position = "absolute";
  links.style.top = "70px";
  links.style.left = "0";
  links.style.right = "0";
  links.style.background = "rgba(13,21,32,0.97)";
  links.style.padding = "20px 32px";
  links.style.gap = "16px";
  links.style.borderBottom = "1px solid rgba(255,255,255,0.07)";
});