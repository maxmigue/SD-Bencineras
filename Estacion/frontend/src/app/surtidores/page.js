"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

const API_URL = "http://localhost:8001";

export default function SurtidoresPage() {
  const [surtidores, setSurtidores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [estadisticas, setEstadisticas] = useState(null);

  // Cargar surtidores y estadísticas
  useEffect(() => {
    const cargarDatos = async () => {
      try {
        // Cargar surtidores
        const resSurtidores = await fetch(`${API_URL}/api/surtidores`);
        if (!resSurtidores.ok) throw new Error("Error cargando surtidores");
        const dataSurtidores = await resSurtidores.json();
        setSurtidores(dataSurtidores);

        // Cargar estadísticas
        const resStats = await fetch(`${API_URL}/api/surtidores/estadisticas`);
        if (!resStats.ok) throw new Error("Error cargando estadísticas");
        const dataStats = await resStats.json();
        setEstadisticas(dataStats);

        setLoading(false);
      } catch (err) {
        console.error("Error:", err);
        setError(err.message);
        setLoading(false);
      }
    };

    cargarDatos();
    // Actualizar cada 5 segundos
    const intervalo = setInterval(cargarDatos, 5000);
    return () => clearInterval(intervalo);
  }, []);

  const getEstadoColor = (estado) => {
    const colores = {
      disponible: "bg-green-100 text-green-700",
      despachando: "bg-blue-100 text-blue-700",
      pausado: "bg-yellow-100 text-yellow-700",
      fuera_servicio: "bg-red-100 text-red-700",
    };
    return colores[estado] || "bg-gray-100 text-gray-700";
  };

  const getConexionColor = (estado) => {
    return estado === "conectado"
      ? "bg-green-500"
      : "bg-red-500";
  };

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col">
      {/* CONTENIDO */}
      <section className="flex-1 max-w-7xl mx-auto mt-10 px-4 w-full">
        <div className="mb-6">
          <h2 className="font-poppins text-3xl font-bold text-gray-800">
            Surtidores de la Estación
          </h2>
          <p className="text-gray-600 mt-2">
            Monitoreo en tiempo real del estado de los surtidores
          </p>
        </div>

        {/* ESTADÍSTICAS GENERALES */}
        {estadisticas && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <div className="text-sm text-gray-600 mb-1">Total Surtidores</div>
              <div className="text-3xl font-bold text-gray-800">
                {estadisticas.total_surtidores}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <div className="text-sm text-gray-600 mb-1">Conectados</div>
              <div className="text-3xl font-bold text-green-600">
                {estadisticas.cantidad_tcp_conectados}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <div className="text-sm text-gray-600 mb-1">Litros Totales</div>
              <div className="text-3xl font-bold text-blue-600">
                {estadisticas.litros_totales.toFixed(1)}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <div className="text-sm text-gray-600 mb-1">Ingresos Totales</div>
              <div className="text-3xl font-bold text-[#F26E22]">
                ${estadisticas.ingresos_totales.toLocaleString()}
              </div>
            </div>
          </div>
        )}

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#F26E22]"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            Error: {error}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {surtidores.map((surtidor) => (
              <div
                key={surtidor.id_surtidor}
                className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow"
              >
                {/* Header del card */}
                <div className="bg-gradient-to-r from-[#F26E22] to-[#FFA057] p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-xl font-bold text-white">
                        {surtidor.nombre}
                      </h3>
                      <p className="text-white/90 text-sm">
                        ID: {surtidor.id_surtidor}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <div
                        className={`w-3 h-3 rounded-full ${getConexionColor(
                          surtidor.estado_conexion
                        )} ${
                          surtidor.estado_conexion === "conectado"
                            ? "animate-pulse"
                            : ""
                        }`}
                      ></div>
                      <span className="text-white text-sm font-medium">
                        {surtidor.estado_conexion === "conectado"
                          ? "Online"
                          : "Offline"}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Contenido del card */}
                <div className="p-6 space-y-4">
                  {/* Estado operacional */}
                  <div>
                    <div className="text-sm text-gray-600 mb-1">Estado</div>
                    <span
                      className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${getEstadoColor(
                        surtidor.estado
                      )}`}
                    >
                      {surtidor.estado.replace("_", " ").toUpperCase()}
                    </span>
                  </div>

                  {/* Combustible actual */}
                  <div>
                    <div className="text-sm text-gray-600 mb-1">
                      Combustible Actual
                    </div>
                    <div className="text-lg font-semibold text-gray-800">
                      Gasolina {surtidor.combustible_actual}
                    </div>
                  </div>

                  {/* Estadísticas */}
                  <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
                    <div>
                      <div className="text-xs text-gray-500">Transacciones</div>
                      <div className="text-xl font-bold text-gray-800">
                        {surtidor.total_transacciones}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Litros</div>
                      <div className="text-xl font-bold text-gray-800">
                        {surtidor.litros_totales?.toFixed(1)}
                      </div>
                    </div>
                  </div>

                  {/* Ingresos */}
                  <div className="pt-4 border-t border-gray-200">
                    <div className="text-sm text-gray-600 mb-1">
                      Ingresos Generados
                    </div>
                    <div className="text-2xl font-bold text-[#F26E22]">
                      ${surtidor.ingresos_totales?.toLocaleString()}
                    </div>
                  </div>

                  {/* Combustibles soportados */}
                  <div className="pt-4 border-t border-gray-200">
                    <div className="text-sm text-gray-600 mb-2">
                      Combustibles Soportados
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {surtidor.combustibles_soportados?.map((comb) => (
                        <span
                          key={comb}
                          className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                        >
                          {comb}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Última conexión */}
                  {surtidor.ultima_conexion && (
                    <div className="text-xs text-gray-500 pt-2">
                      Última conexión:{" "}
                      {new Date(surtidor.ultima_conexion).toLocaleString(
                        "es-ES",
                        {
                          year: "numeric",
                          month: "2-digit",
                          day: "2-digit",
                          hour: "2-digit",
                          minute: "2-digit",
                        }
                      )}
                    </div>
                  )}

                  {/* Botón ver transacciones */}
                  <Link
                    href={`/transacciones?surtidor=${surtidor.id_surtidor}`}
                    className="block w-full mt-4 text-center bg-[#F26E22] hover:bg-[#d45a15] text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                  >
                    Ver Transacciones
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}

        {surtidores.length === 0 && !loading && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">
              No hay surtidores registrados en el sistema.
            </p>
          </div>
        )}
      </section>
    </main>
  );
}
