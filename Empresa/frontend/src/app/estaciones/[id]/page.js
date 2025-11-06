"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "../../../components/ui/button";
import { ArrowLeftIcon } from "@radix-ui/react-icons";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function HistoricoPage() {
  const params = useParams();
  const router = useRouter();
  const [estacion, setEstacion] = useState(null);
  const [historico, setHistorico] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.id) {
      cargarDatos();
    }
  }, [params.id]);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      
      // Cargar información de la estación
      const responseEstacion = await fetch(`${API_URL}/api/estaciones/${params.id}`);
      if (!responseEstacion.ok) {
        alert("Estación no encontrada");
        router.push("/estaciones");
        return;
      }
      const dataEstacion = await responseEstacion.json();
      setEstacion(dataEstacion);

      // Cargar historial
      const responseHistorico = await fetch(`${API_URL}/api/estaciones/${params.id}/historico`);
      if (responseHistorico.ok) {
        const dataHistorico = await responseHistorico.json();
        // Ordenar por fecha más reciente primero
        const ordenado = dataHistorico.sort((a, b) => 
          new Date(b.timestamp) - new Date(a.timestamp)
        );
        setHistorico(ordenado);
      }
    } catch (error) {
      console.error("Error cargando datos:", error);
      alert("Error al cargar el historial");
    } finally {
      setLoading(false);
    }
  };

  const formatearFecha = (timestamp) => {
    const fecha = new Date(timestamp);
    return fecha.toLocaleString("es-CL", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  const calcularDiferencia = (preciosActual, preciosAnterior) => {
    if (!preciosAnterior) return null;
    
    const diffs = {};
    const keys = ["precio_93", "precio_95", "precio_97", "precio_diesel"];
    
    keys.forEach(key => {
      const diff = preciosActual[key] - preciosAnterior[key];
      if (diff !== 0) {
        diffs[key] = diff;
      }
    });
    
    return Object.keys(diffs).length > 0 ? diffs : null;
  };

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Button
            onClick={() => router.push("/estaciones")}
            variant="outline"
            className="mb-4"
          >
            <ArrowLeftIcon className="mr-2" />
            Volver a Estaciones
          </Button>

          {estacion && (
            <div className="bg-white rounded-lg shadow p-6">
              <h1 className="text-3xl font-bold text-gray-800 mb-2">
                Historial de Precios
              </h1>
              <div className="flex items-center gap-4 text-gray-600">
                <p className="text-lg font-semibold">{estacion.nombre}</p>
                <span className="text-sm">
                  IP: {estacion.ip}:{estacion.puerto}
                </span>
                <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
                  estacion.estado === "Activa" 
                    ? "bg-green-100 text-green-700" 
                    : "bg-gray-100 text-gray-700"
                }`}>
                  {estacion.estado}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Contenido */}
        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-500">Cargando historial...</p>
          </div>
        ) : historico.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-500">No hay historial de precios disponible</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="bg-white rounded-lg shadow p-4 mb-4">
              <h2 className="text-sm font-semibold text-gray-700 mb-2">
                Total de actualizaciones: {historico.length}
              </h2>
            </div>

            {/* Timeline de cambios */}
            <div className="relative">
              {/* Línea vertical del timeline */}
              <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>

              {historico.map((entrada, index) => {
                const diferencia = index < historico.length - 1 
                  ? calcularDiferencia(entrada.precios, historico[index + 1].precios)
                  : null;

                return (
                  <div key={index} className="relative pl-20 pb-8">
                    {/* Punto en el timeline */}
                    <div className={`absolute left-6 w-5 h-5 rounded-full border-4 ${
                      index === 0 
                        ? "bg-blue-500 border-blue-200" 
                        : "bg-white border-gray-300"
                    }`}></div>

                    {/* Card de la entrada */}
                    <div className={`bg-white rounded-lg shadow-sm p-6 ${
                      index === 0 ? "border-2 border-blue-200" : "border border-gray-200"
                    }`}>
                      {/* Fecha y badge */}
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <p className="text-sm font-semibold text-gray-800">
                            {formatearFecha(entrada.timestamp)}
                          </p>
                          {index === 0 && (
                            <span className="inline-block mt-1 px-2 py-1 text-xs font-semibold bg-blue-100 text-blue-700 rounded">
                              Precios Actuales
                            </span>
                          )}
                        </div>
                        {diferencia && (
                          <div className="text-right">
                            <p className="text-xs text-gray-500">Cambios respecto a anterior</p>
                          </div>
                        )}
                      </div>

                      {/* Grid de precios */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-gray-50 rounded-lg p-3">
                          <p className="text-xs text-gray-600 mb-1">Gasolina 93</p>
                          <p className="text-lg font-bold text-gray-800">
                            ${entrada.precios.precio_93}
                          </p>
                          {diferencia?.precio_93 && (
                            <p className={`text-xs font-semibold ${
                              diferencia.precio_93 > 0 ? "text-red-600" : "text-green-600"
                            }`}>
                              {diferencia.precio_93 > 0 ? "+" : ""}{diferencia.precio_93}
                            </p>
                          )}
                        </div>

                        <div className="bg-gray-50 rounded-lg p-3">
                          <p className="text-xs text-gray-600 mb-1">Gasolina 95</p>
                          <p className="text-lg font-bold text-gray-800">
                            ${entrada.precios.precio_95}
                          </p>
                          {diferencia?.precio_95 && (
                            <p className={`text-xs font-semibold ${
                              diferencia.precio_95 > 0 ? "text-red-600" : "text-green-600"
                            }`}>
                              {diferencia.precio_95 > 0 ? "+" : ""}{diferencia.precio_95}
                            </p>
                          )}
                        </div>

                        <div className="bg-gray-50 rounded-lg p-3">
                          <p className="text-xs text-gray-600 mb-1">Gasolina 97</p>
                          <p className="text-lg font-bold text-gray-800">
                            ${entrada.precios.precio_97}
                          </p>
                          {diferencia?.precio_97 && (
                            <p className={`text-xs font-semibold ${
                              diferencia.precio_97 > 0 ? "text-red-600" : "text-green-600"
                            }`}>
                              {diferencia.precio_97 > 0 ? "+" : ""}{diferencia.precio_97}
                            </p>
                          )}
                        </div>

                        <div className="bg-gray-50 rounded-lg p-3">
                          <p className="text-xs text-gray-600 mb-1">Diesel</p>
                          <p className="text-lg font-bold text-gray-800">
                            ${entrada.precios.precio_diesel}
                          </p>
                          {diferencia?.precio_diesel && (
                            <p className={`text-xs font-semibold ${
                              diferencia.precio_diesel > 0 ? "text-red-600" : "text-green-600"
                            }`}>
                              {diferencia.precio_diesel > 0 ? "+" : ""}{diferencia.precio_diesel}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
