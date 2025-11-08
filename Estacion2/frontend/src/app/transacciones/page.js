"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function TransaccionesPage() {
  const [transacciones, setTransacciones] = useState([
    {
      id: 1,
      surtidor: "Surtidor Norte",
      combustible: "Gasolina 95",
      litros: 32.5,
      total: 43875,
      fecha: "2025-11-05 13:22:14",
      estado: "Completada",
    },
    {
      id: 2,
      surtidor: "Surtidor Sur",
      combustible: "Diésel",
      litros: 18.2,
      total: 20384,
      fecha: "2025-11-05 12:58:09",
      estado: "Cargando",
    },
    {
      id: 3,
      surtidor: "Surtidor Norte",
      combustible: "Gasolina 93",
      litros: 25.7,
      total: 33141,
      fecha: "2025-11-05 12:45:02",
      estado: "Completada",
    },
  ]);

  // 🔄 Preparado para conexión WebSocket futura
  // useEffect(() => {
  //   const socket = io("http://localhost:4000");
  //   socket.on("nuevaTransaccion", (data) => {
  //     setTransacciones((prev) => [data, ...prev]);
  //   });
  //   return () => socket.disconnect();
  // }, []);

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col">

      {/* CONTENIDO */}
      <section className="flex-1 max-w-6xl mx-auto mt-10 px-4 w-full">
        <h2 className="font-poppins text-3xl font-bold text-gray-800 mb-6">
          Historial de Transacciones
        </h2>

        <div className="overflow-x-auto bg-white border border-gray-200 rounded-xl shadow-sm">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-[#F26E22] text-white text-sm">
              <tr>
                <th className="px-6 py-3 text-left font-semibold">ID</th>
                <th className="px-6 py-3 text-left font-semibold">Surtidor</th>
                <th className="px-6 py-3 text-left font-semibold">Combustible</th>
                <th className="px-6 py-3 text-left font-semibold">Litros</th>
                <th className="px-6 py-3 text-left font-semibold">Total ($)</th>
                <th className="px-6 py-3 text-left font-semibold">Fecha</th>
                <th className="px-6 py-3 text-left font-semibold">Estado</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-100">
              {transacciones.map((t) => (
                <tr key={t.id} className="hover:bg-gray-50 transition-all">
                  <td className="px-6 py-3 text-sm text-gray-700">{t.id}</td>
                  <td className="px-6 py-3 text-sm text-gray-800 font-medium">{t.surtidor}</td>
                  <td className="px-6 py-3 text-sm text-gray-600">{t.combustible}</td>
                  <td className="px-6 py-3 text-sm text-gray-600">{t.litros}</td>
                  <td className="px-6 py-3 text-sm text-gray-800 font-semibold">${t.total.toLocaleString()}</td>
                  <td className="px-6 py-3 text-sm text-gray-500">{t.fecha}</td>
                  <td className="px-6 py-3 text-sm">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        t.estado === "Completada"
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

          {transacciones.length === 0 && (
            <p className="text-center py-6 text-gray-500">
              No hay transacciones registradas aún.
            </p>
          )}
        </div>
      </section>
    </main>
  );
}
