import net from "net";
import { Server } from "socket.io";
import http from "http";

const TCP_HOST = "127.0.0.1";
const TCP_PORT = 5000;
const WS_PORT = 4000;

// Crear servidor HTTP + WebSocket
const httpServer = http.createServer();
const io = new Server(httpServer, {
  cors: { 
    origin: "http://localhost:3000", 
    methods: ["GET", "POST"],
    transports: ['websocket', 'polling']
  },
});

// ✅ Mantener un mapa global de surtidores activos
const surtidores = new Map();

// Registrar conexiones del frontend
io.on("connection", (socket) => {
  console.log("🧠 Frontend conectado:", socket.id);
  
  // Enviar estado actual apenas se conecta
  const estadoActual = Array.from(surtidores.values());
  console.log("📤 Enviando estado inicial al frontend:", estadoActual);
  socket.emit("estadoSurtidores", estadoActual);

  socket.on("disconnect", () => {
    console.log("❌ Frontend desconectado:", socket.id);
  });
});

// Iniciar servidor WebSocket
httpServer.listen(WS_PORT, () => {
  console.log(`🌐 WebSocket bridge escuchando en puerto ${WS_PORT}`);
});

// Crear cliente TCP (conexión con Python)
const tcpClient = new net.Socket();

let reconnectAttempt = 0;
const maxReconnectAttempts = 5;

function connectTCP() {
  tcpClient.connect(TCP_PORT, TCP_HOST, () => {
    console.log("✅ Conectado al servidor TCP en Python");
    reconnectAttempt = 0;
  });
}

tcpClient.on("data", (data) => {
  const mensaje = data.toString().trim();
  const partes = mensaje.split("\n").filter((p) => p.length > 0);

  partes.forEach((parte) => {
    try {
      const jsonValido = parte.replace(/'/g, '"');
      const parsed = JSON.parse(jsonValido);

      const surtidor = {
        id: parsed.id,
        nombre: parsed.nombre,
        estado: parsed.estado,
        precios: {
          gasolina93: parsed.precio_93,
          gasolina95: parsed.precio_95,
          gasolina97: parsed.precio_97,
          diesel: parsed.precio_diesel,
        },
      };

      surtidores.set(surtidor.id, surtidor);
      const estadoActual = Array.from(surtidores.values());
      console.log("📤 Enviando actualización a todos los clientes:", estadoActual);
      io.emit("estadoSurtidores", estadoActual);
    } catch (err) {
      console.error("⚠️ Error al parsear:", err.message);
    }
  });
});

// Manejo de errores y reconexión TCP
tcpClient.on("error", (err) => {
  console.error("❌ Error TCP:", err.message);
});

tcpClient.on("close", () => {
  console.log("❌ Conexión TCP cerrada");
  if (reconnectAttempt < maxReconnectAttempts) {
    reconnectAttempt++;
    console.log(`🔄 Intentando reconectar... (intento ${reconnectAttempt})`);
    setTimeout(connectTCP, 2000 * reconnectAttempt);
  }
});

// Iniciar conexión TCP
connectTCP();
