const { makeWASocket, useMultiFileAuthState, DisconnectReason } = require("@whiskeysockets/baileys");
const path = require("path");
const fs = require("fs");

const AUTH_DIR = path.join(__dirname, "auth_info");

function send(obj) {
  process.stdout.write(JSON.stringify(obj) + "\n");
}

// Read commands from parent process stdin
function startStdinReader(sock) {
  let buffer = "";
  process.stdin.on("data", (chunk) => {
    buffer += chunk.toString();
    const lines = buffer.split("\n");
    buffer = lines.pop();
    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const cmd = JSON.parse(line);
        if (cmd.type === "send") {
          const jid = cmd.to.includes("@s.whatsapp.net") ? cmd.to : cmd.to + "@s.whatsapp.net";
          const text = cmd.text.slice(0, 4000);
          sock.sendMessage(jid, { text }).catch((e) => send({ type: "error", msg: e.message }));
        }
        if (cmd.type === "pair") {
          const phone = cmd.phone.replace(/\D/g, "");
          sock.requestPairingCode(phone).then((code) => {
            send({ type: "pair_code", code });
          }).catch((e) => send({ type: "error", msg: "pair failed: " + e.message }));
        }
      } catch (e) {
        send({ type: "error", msg: "invalid stdin command" });
      }
    }
  });
}

async function start() {
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
  const sock = makeWASocket({
    auth: state,
    printQRInTerminal: false,
    syncFullHistory: false,
    emitOwnEvents: false,
    browser: ["Chrome", "Linux", ""],
    generateHighQualityLinkPreview: false,
    markOnlineOnConnect: false,
  });

  sock.ev.on("creds.update", saveCreds);
  process.stderr.write("sidecar: socket created\n");
  sock.ev.on("messages.upsert", () => {}); // keep ref
  sock.ev.on("connection.update", ({ connection, lastDisconnect, qr }) => {
    if (qr) {
      send({ type: "qr", qr });
    }
    if (connection === "open") {
      send({ type: "ready" });
    }
    if (connection === "close") {
      const reason = lastDisconnect?.error?.output?.statusCode || DisconnectReason.loggedOut;
      const errMsg = lastDisconnect?.error?.message || "";
      process.stderr.write(`sidecar: close reason=${reason} msg="${errMsg}"\n`);
      send({ type: "close", reason });
      if (reason === DisconnectReason.loggedOut) {
        fs.rmSync(AUTH_DIR, { recursive: true, force: true });
      }
      setTimeout(() => process.exit(0), 500);
    }
    if (connection === "connecting") {
      send({ type: "connecting" });
    }
  });

  sock.ev.on("messages.upsert", ({ messages }) => {
    for (const m of messages) {
      if (m.key.fromMe) continue;
      if (m.key.remoteJid.endsWith("@broadcast")) continue;
      const text =
        m.message?.conversation ||
        m.message?.extendedTextMessage?.text ||
        m.message?.imageMessage?.caption ||
        "";
      if (!text.trim()) continue;
      send({
        type: "message",
        from: m.key.remoteJid,
        pushName: m.pushName || "",
        text: text.trim(),
        isGroup: m.key.remoteJid.endsWith("@g.us"),
      });
    }
  });

  startStdinReader(sock);
}

start();
