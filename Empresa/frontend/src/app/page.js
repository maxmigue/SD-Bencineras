"use client"

import { useState, useEffect } from "react";
import { Button } from "../components/ui/button";
import Link from "next/link";
import { 
  RocketIcon, 
  ActivityLogIcon, 
  GearIcon,
  BarChartIcon 
} from "@radix-ui/react-icons";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function HomePage() {
  const [estadisticas, setEstadisticas] = useState(null);
  const [estaciones, setEstaciones] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarDatos();
    const interval = setInterval(cargarDatos, 30000);
    return () => clearInterval(interval);
  }, []);

  const cargarDatos = async () => {
    try {
      const responseStats = await fetch(`${API_URL}/api/estadisticas`);
      if (responseStats.ok) {
        const dataStats = await responseStats.json();
        setEstadisticas(dataStats);
      }

      const responseEstaciones = await fetch(`${API_URL}/api/estaciones`);
      if (responseEstaciones.ok) {
        const dataEstaciones = await responseEstaciones.json();
        setEstaciones(dataEstaciones.slice(0, 6));
      }
    } catch (error) {
      console.error("Error cargando datos:", error);
    } finally {
      setLoading(false);
    }
  };

  const getEstadoBadgeClass = (estado) => {
    switch (estado?.toLowerCase()) {
      case "activa":
        return "bg-green-100 text-green-700";
      case "inactiva":
        return "bg-yellow-100 text-yellow-700";
      case "desconectada":
        return "bg-red-100 text-red-700";
      default:
        return "bg-gray-100 text-gray-700";
    }
  };

  return (
    <main className="min-h-screen bg-gray-50">
      <section className="bg-gradient-to-r from-[#F26E22] to-[#d65e1d] text-white py-16">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center gap-4 mb-4">
            <RocketIcon className="w-12 h-12" />
            <h1 className="text-4xl font-bold">
              Sistema de Gestión Empresarial
            </h1>
          </div>
          <p className="text-xl text-white/90 max-w-2xl">
            Panel de control centralizado para administrar estaciones de servicio, 
            actualizar precios en tiempo real y monitorear el sistema.
          </p>
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-6 -mt-8">
        {loading ? (
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <p className="text-gray-500">Cargando datos...</p>
          </div>
        ) : estadisticas ? (
          <div className="grid gap-6 md:grid-cols-4 mb-8">
            <div className="bg-white rounded-lg shadow-lg p-6 border-t-4 border-blue-500">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-gray-600">Total Estaciones</h3>
                <BarChartIcon className="w-8 h-8 text-blue-500" />
              </div>
              <p className="text-3xl font-bold text-gray-800">
                {estadisticas.total_estaciones}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6 border-t-4 border-green-500">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-gray-600">Activas</h3>
                <ActivityLogIcon className="w-8 h-8 text-green-500" />
              </div>
              <p className="text-3xl font-bold text-gray-800">
                {estadisticas.activas}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6 border-t-4 border-yellow-500">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-gray-600">Inactivas</h3>
                <GearIcon className="w-8 h-8 text-yellow-500" />
              </div>
              <p className="text-3xl font-bold text-gray-800">
                {estadisticas.inactivas}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6 border-t-4 border-red-500">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-gray-600">Desconectadas</h3>
                <ActivityLogIcon className="w-8 h-8 text-red-500" />
              </div>
              <p className="text-3xl font-bold text-gray-800">
                {estadisticas.desconectadas}
              </p>
            </div>
          </div>
        ) : null}
      </section>

      <section className="max-w-7xl mx-auto px-6 mb-12">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Accesos Rápidos</h2>
        <div className="grid gap-6 md:grid-cols-3">
          <Link href="/estaciones">
            <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-8 cursor-pointer border-l-4 border-[#F26E22]">
              <GearIcon className="w-12 h-12 text-[#F26E22] mb-4" />
              <h3 className="text-xl font-bold text-gray-800 mb-2">
                Gestión de Estaciones
              </h3>
              <p className="text-gray-600">
                Crear, editar y administrar estaciones de servicio
              </p>
            </div>
          </Link>

          <Link href="/estaciones">
            <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-8 cursor-pointer border-l-4 border-blue-500">
              <BarChartIcon className="w-12 h-12 text-blue-500 mb-4" />
              <h3 className="text-xl font-bold text-gray-800 mb-2">
                Actualizar Precios
              </h3>
              <p className="text-gray-600">
                Modificar precios y sincronizar con las estaciones
              </p>
            </div>
          </Link>

          <Link href="/transacciones">
            <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-8 cursor-pointer border-l-4 border-green-500">
              <ActivityLogIcon className="w-12 h-12 text-green-500 mb-4" />
              <h3 className="text-xl font-bold text-gray-800 mb-2">
                Ver Transacciones
              </h3>
              <p className="text-gray-600">
                Consultar historial de cambios y operaciones
              </p>
            </div>
          </Link>
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-6 pb-12">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Estaciones Registradas</h2>
          <Link href="/estaciones">
            <Button className="bg-[#F26E22] hover:bg-[#d65e1d] text-white">
              Ver Todas
            </Button>
          </Link>
        </div>

        {estaciones.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-500 mb-4">No hay estaciones registradas</p>
            <Link href="/estaciones">
              <Button className="bg-[#F26E22] hover:bg-[#d65e1d] text-white">
                Crear Primera Estación
              </Button>
            </Link>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {estaciones.map((estacion) => (
              <div
                key={estacion.id_estacion}
                className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-all p-6"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-1">
                      {estacion.nombre}
                    </h3>
                    <p className="text-sm text-gray-500">ID: {estacion.id_estacion}</p>
                  </div>
                  <span
                    className={`px-3 py-1 text-xs font-semibold rounded-full ${getEstadoBadgeClass(
                      estacion.estado
                    )}`}
                  >
                    {estacion.estado}
                  </span>
                </div>

                <div className="mb-4 pb-4 border-b">
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">IP:</span> {estacion.ip}
                  </p>
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Puerto:</span> {estacion.puerto}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                  <div>Precio 93: ${estacion.precios_actuales.precio_93}</div>
                  <div>Precio 95: ${estacion.precios_actuales.precio_95}</div>
                  <div>Precio 97: ${estacion.precios_actuales.precio_97}</div>
                  <div>Precio Diesel: ${estacion.precios_actuales.precio_diesel}</div>
                </div>

                <Link href={`/estaciones`}>
                  <Button
                    className="w-full mt-4 bg-[#F26E22] hover:bg-[#d65e1d] text-white"
                    size="sm"
                  >
                    Ver Detalles
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

