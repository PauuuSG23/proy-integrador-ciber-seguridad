const chatEl = document.getElementById("chat");   // contenedor de chat
const formEl = document.getElementById("form");   // formulario de entrada
const inputEl = document.getElementById("input"); // campo de texto de entrada
const history = [];

// función para agregar un mensaje al chat, con el rol (usuario o bot) y el contenido del mensaje
function addMessage(role, content) {    // agrega un mensaje al chat
  const wrap = document.createElement("div");
  wrap.className = `msg ${role === "user" ? "user" : "bot"}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = content;
  wrap.appendChild(bubble);
  chatEl.appendChild(wrap);
  chatEl.scrollTop = chatEl.scrollHeight;
}

formEl.addEventListener("submit", async (e) => {    // maneja el envío del formulario
  e.preventDefault();
  const msg = inputEl.value.trim();
  if (!msg) return;

  addMessage("user", msg);
  history.push({ role: "user", content: msg });
  inputEl.value = "";
  inputEl.focus();

  addMessage("bot", "…");
  const thinkingNode = chatEl.lastChild;

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg, history })
    });
    const data = await res.json();
    thinkingNode.querySelector(".bubble").textContent = data.reply || data.error || "(sin respuesta)";
    if (data.reply) history.push({ role: "assistant", content: data.reply });
  } catch (err) {
    thinkingNode.querySelector(".bubble").textContent = "Error: " + err;
  }
});
