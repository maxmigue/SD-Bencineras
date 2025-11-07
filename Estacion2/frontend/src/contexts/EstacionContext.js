"use client";

import { createContext, useContext, useState, useEffect } from "react";
import { io } from "socket.io-client";

const EstacionContext = createContext();

export function EstacionProvider({ children }) {
  const [nombreEstacion, setNombreEstacion] = useState("Estación");
  const [precios, setPrecios] = useState({
    precio_93: 1290,
    precio_95: 1350,
    precio_97: 1400,
    precio_diesel: 1120
  });

  useEffect(() => {
    // Obtener URLs desde variables de entorno o usar las del docker-compose
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "http://localhost:4002";
    
    // Cargar información de la estación desde la API
    fetch(`${apiUrl}/estado`)
      .then(res => res.json())
      .then(data => {
        setNombreEstacion(data.nombre);
        setPrecios(data.precios);
      })
      .catch(err => console.error("Error cargando estado:", err));

    // Conectar WebSocket para actualizaciones en tiempo real
    const socket = io(wsUrl, {
      reconnectionDelayMax: 10000,
      reconnectionAttempts: 5,
      transports: ["websocket", "polling"]
    });

    socket.on("connect", () => {
      console.log("✅ Conectado al WebSocket bridge");
    });

    // Escuchar actualizaciones de precios
    socket.on("actualizacionPrecios", (nuevosPrecios) => {
      console.log("💰 Precios actualizados desde Empresa:", nuevosPrecios);
      setPrecios(nuevosPrecios);
    });

    // Escuchar actualizaciones de nombre
    socket.on("actualizacionNombre", (nuevoNombre) => {
      console.log("🏷️ Nombre actualizado desde Empresa:", nuevoNombre);
      setNombreEstacion(nuevoNombre);
    });

    socket.on("disconnect", (reason) => {
      console.log("❌ Desconectado del WebSocket bridge:", reason);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <EstacionContext.Provider value={{ nombreEstacion, precios, setNombreEstacion, setPrecios }}>
      {children}
    </EstacionContext.Provider>
  );
}

export function useEstacion() {
  const context = useContext(EstacionContext);
  if (!context) {
    throw new Error("useEstacion debe usarse dentro de EstacionProvider");
  }
  return context;
}
