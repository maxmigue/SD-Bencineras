"use client";

import { useState, useEffect } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

export default function SurtidorPage() {
  const [estado, setEstado] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  // Función para obtener el estado del backend
  const fetchEstado = async () => {
    try {
      const res = await fetch(`${API_URL}/estado`);
      if (!res.ok) {
        throw new Error("No se pudo obtener el estado del surtidor.");
      }
      const data = await res.json();
      setEstado(data);
      setError("");
    } catch (err) {
      setError(err.message);
      console.error("Error fetching estado:", err);
    } finally {
      setLoading(false);
    }
  };

  // Obtener el estado inicial y luego cada 2 segundos
  useEffect(() => {
    fetchEstado();
    const interval = setInterval(fetchEstado, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleControl = async (action) => {
    try {
      const res = await fetch(`${API_URL}/control/${action}`, { method: "POST" });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "La acción falló.");
      }
      await fetchEstado(); // Actualizar estado después de la acción
    } catch (err) {
      setError(err.message);
      console.error(`Error with ${action}:`, err);
    }
  };

  if (loading) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center bg-gray-100 p-8">
        <p className="text-xl text-gray-600">Cargando panel del surtidor...</p>
      </main>
    );
  }
  
  if (error) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center bg-red-50 p-8">
        <div className="bg-white p-8 rounded-lg shadow-md text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Error de Conexión</h1>
          <p className="text-gray-700">No se pudo conectar con el backend del surtidor.</p>
          <p className="text-sm text-gray-500 mt-2">{error}</p>
        </div>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-100 p-8">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800">{estado?.nombre}</h1>
          <p className={`text-lg font-semibold mt-2 ${
            estado?.estado_operacion === "despachando" ? "text-green-500" : "text-gray-500"
          }`}>
            {estado?.estado_operacion === "despachando" ? "Despachando" : 
             estado?.estado_operacion === "pausado" ? "Pausado" : "Disponible"}
          </p>
        </div>

        <div className="bg-gray-50 rounded-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <span className="text-gray-600">Combustible</span>
            <span className="font-bold text-gray-800">{estado?.tipo_combustible}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Precio / Litro</span>
            <span className="font-bold text-gray-800">${estado?.precio_litro}</span>
          </div>
        </div>

        <div className="text-center mb-8">
          <p className="text-xl text-gray-600">Litros Despachados</p>
          <p className="text-6xl font-bold text-blue-600 my-2">
            {estado?.litros_actuales?.toFixed(2) || "0.00"}
          </p>
          <p className="text-xl text-gray-600">Total a Pagar</p>
          <p className="text-4xl font-bold text-green-600">
            ${estado?.monto_actual?.toFixed(2) || "0.00"}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => handleControl("iniciar-carga")}
            disabled={estado?.estado_operacion === "despachando"}
            className="w-full bg-green-500 text-white font-bold py-3 px-4 rounded-lg hover:bg-green-600 disabled:bg-gray-300 transition-colors"
          >
            Iniciar Carga
          </button>
          <button
            onClick={() => handleControl("detener-carga?metodo_pago=efectivo")}
            disabled={estado?.estado_operacion !== "despachando"}
            className="w-full bg-red-500 text-white font-bold py-3 px-4 rounded-lg hover:bg-red-600 disabled:bg-gray-300 transition-colors"
          >
            Detener Carga
          </button>
        </div>
      </div>
    </main>
  );
}