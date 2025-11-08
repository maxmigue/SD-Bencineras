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
    origin: ["http://localhost:3000", "http://localhost:3001"], 
    methods: ["GET", "POST"],
    transports: ['websocket', 'polling']
  },
});

// ✅ Mantener un mapa global de surtidores activos
const surtidores = new Map();

// ✅ Mantener precios actuales de la estación
let preciosActuales = {
  precio_93: 1290,
  precio_95: 1350,
  precio_97: 1400,
  precio_diesel: 1120
};

// ✅ Mantener nombre de la estación
let nombreEstacion = "Estación Local";

// Registrar conexiones del frontend
io.on("connection", (socket) => {
  console.log("🧠 Frontend conectado:", socket.id);
  
  // Enviar estado actual apenas se conecta
  const estadoActual = Array.from(surtidores.values());
  console.log("📤 Enviando estado inicial al frontend:", estadoActual);
  socket.emit("estadoSurtidores", estadoActual);
  
  // Enviar precios actuales
  console.log("💰 Enviando precios actuales al frontend:", preciosActuales);
  socket.emit("actualizacionPrecios", preciosActuales);

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

      // 🔍 Detectar actualización de precios desde Empresa
      if (parsed.tipo === "actualizacion_precios") {
        console.log("💰 Actualización de precios recibida desde Empresa");
        preciosActuales = parsed.precios;
        console.log("✅ Precios actualizados:", preciosActuales);
        
        // Actualizar nombre si viene en el mensaje
        if (parsed.nombre_estacion) {
          nombreEstacion = parsed.nombre_estacion;
          console.log("✅ Nombre actualizado:", nombreEstacion);
        }
        
        // 📡 Propagar los nuevos precios y nombre a todos los clientes conectados
        io.emit("actualizacionPrecios", preciosActuales);
        if (parsed.nombre_estacion) {
          io.emit("actualizacionNombre", nombreEstacion);
        }
        console.log("📤 Precios propagados al frontend");
        return;
      }

      // 🔍 Detectar nueva transacción desde Surtidor
      if (parsed.tipo === "nueva_transaccion") {
        console.log("💳 Nueva transacción recibida:", parsed.transaccion);
        
        // 📡 Propagar la transacción a todos los clientes conectados
        io.emit("nuevaTransaccion", parsed.transaccion);
        console.log("📤 Transacción propagada al frontend");
        return;
      }

      // Mensaje normal de surtidor
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
