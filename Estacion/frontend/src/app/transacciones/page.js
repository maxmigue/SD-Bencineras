"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import io from "socket.io-client";

const API_URL = "http://localhost:8001";
const WS_URL = "http://localhost:4001";

export default function TransaccionesPage() {
  const [transacciones, setTransacciones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Cargar transacciones iniciales desde la API
  useEffect(() => {
    const cargarTransacciones = async () => {
      try {
        const response = await fetch(`${API_URL}/transacciones`);
        if (!response.ok) throw new Error("Error cargando transacciones");
        const data = await response.json();
        setTransacciones(data);
        setLoading(false);
      } catch (err) {
        console.error("Error:", err);
        setError(err.message);
        setLoading(false);
      }
    };

    cargarTransacciones();
  }, []);

  // Conectar a WebSocket para recibir transacciones en tiempo real
  useEffect(() => {
    const socket = io(WS_URL, {
      transports: ['websocket', 'polling']
    });

    socket.on("connect", () => {
      console.log("✅ Conectado a WebSocket de transacciones");
    });

    socket.on("nuevaTransaccion", (transaccion) => {
      console.log("💳 Nueva transacción recibida:", transaccion);
      setTransacciones((prev) => [transaccion, ...prev]);
    });

    socket.on("disconnect", () => {
      console.log("❌ Desconectado de WebSocket");
    });

    return () => socket.disconnect();
  }, []);

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col">

      {/* CONTENIDO */}
      <section className="flex-1 max-w-6xl mx-auto mt-10 px-4 w-full">
        <div className="flex justify-between items-center mb-6">
          <h2 className="font-poppins text-3xl font-bold text-gray-800">
            Historial de Transacciones
          </h2>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-600">Tiempo Real</span>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#F26E22]"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            Error: {error}
          </div>
        ) : (
          <div className="overflow-x-auto bg-white border border-gray-200 rounded-xl shadow-sm">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-[#F26E22] text-white text-sm">
                <tr>
                  <th className="px-6 py-3 text-left font-semibold">Surtidor</th>
                  <th className="px-6 py-3 text-left font-semibold">Combustible</th>
                  <th className="px-6 py-3 text-left font-semibold">Litros</th>
                  <th className="px-6 py-3 text-left font-semibold">Precio/L</th>
                  <th className="px-6 py-3 text-left font-semibold">Total ($)</th>
                  <th className="px-6 py-3 text-left font-semibold">Método</th>
                  <th className="px-6 py-3 text-left font-semibold">Fecha</th>
                  <th className="px-6 py-3 text-left font-semibold">Estado</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-100">
                {transacciones.map((t, index) => (
                  <tr 
                    key={t._id || index} 
                    className={`hover:bg-gray-50 transition-all ${index === 0 ? 'animate-pulse bg-green-50' : ''}`}
                  >
                    <td className="px-6 py-3 text-sm text-gray-800 font-medium">{t.nombre_surtidor || `Surtidor ${t.surtidor_id}`}</td>
                    <td className="px-6 py-3 text-sm text-gray-600">{t.tipo_combustible}</td>
                    <td className="px-6 py-3 text-sm text-gray-600">{t.litros?.toFixed(2)}</td>
                    <td className="px-6 py-3 text-sm text-gray-600">${t.precio_por_litro}</td>
                    <td className="px-6 py-3 text-sm text-gray-800 font-semibold">${t.monto_total?.toLocaleString()}</td>
                    <td className="px-6 py-3 text-sm text-gray-600">{t.metodo_pago}</td>
                    <td className="px-6 py-3 text-sm text-gray-500">
                      {new Date(t.fecha).toLocaleString('es-ES', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </td>
                    <td className="px-6 py-3 text-sm">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          t.estado === "completada"
                            ? "bg-green-100 text-green-700"
                            : "bg-yellow-100 text-yellow-700"
                        }`}
                      >
                        {t.estado}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {transacciones.length === 0 && !loading && (
              <p className="text-center py-6 text-gray-500">
                No hay transacciones registradas aún.
              </p>
            )}
          </div>
        )}
      </section>
    </main>
  );
}
