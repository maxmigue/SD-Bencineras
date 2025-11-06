"use client";

import { useState, useEffect } from "react";
import { Button } from "../../components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "../../components/ui/dialog";
import { Input } from "../../components/ui/input";
import { PlusIcon, Pencil1Icon, TrashIcon, UpdateIcon } from "@radix-ui/react-icons";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function EstacionesPage() {
  const [estaciones, setEstaciones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openEdit, setOpenEdit] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);
  const [openPrecios, setOpenPrecios] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteId, setDeleteId] = useState(null);
  const [preciosEstacion, setPreciosEstacion] = useState(null);
  
  const [form, setForm] = useState({
    nombre: "",
    ip: "",
    puerto: 5000,
    precios_actuales: {
      precio_93: 1290,
      precio_95: 1350,
      precio_97: 1400,
      precio_diesel: 1120,
    },
  });

  const [formPrecios, setFormPrecios] = useState({
    precio_93: 0,
    precio_95: 0,
    precio_97: 0,
    precio_diesel: 0,
  });

  // Cargar estaciones al iniciar
  useEffect(() => {
    cargarEstaciones();
  }, []);

  const cargarEstaciones = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/estaciones`);
      const data = await response.json();
      setEstaciones(data);
    } catch (error) {
      console.error("Error cargando estaciones:", error);
      alert("Error al cargar estaciones");
    } finally {
      setLoading(false);
    }
  };

  // Abrir modal de crear/editar
  const handleOpenEdit = (estacion = null) => {
    if (estacion) {
      setEditing(estacion);
      setForm({
        nombre: estacion.nombre,
        ip: estacion.ip,
        puerto: estacion.puerto,
        precios_actuales: estacion.precios_actuales,
      });
    } else {
      setEditing(null);
      setForm({
        nombre: "",
        ip: "",
        puerto: 5000,
        precios_actuales: {
          precio_93: 1290,
          precio_95: 1350,
          precio_97: 1400,
          precio_diesel: 1120,
        },
      });
    }
    setOpenEdit(true);
  };

  // Guardar estación (crear o actualizar)
  const handleSave = async () => {
    try {
      if (editing) {
        // Actualizar estación existente
        const response = await fetch(`${API_URL}/api/estaciones/${editing.id_estacion}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            nombre: form.nombre,
            ip: form.ip,
            puerto: form.puerto,
          }),
        });

        if (!response.ok) {
          const error = await response.json();
          alert(`Error: ${error.detail}`);
          return;
        }
      } else {
        // Crear nueva estación
        const response = await fetch(`${API_URL}/api/estaciones`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(form),
        });

        if (!response.ok) {
          const error = await response.json();
          alert(`Error: ${error.detail}`);
          return;
        }
      }

      setOpenEdit(false);
      cargarEstaciones();
    } catch (error) {
      console.error("Error guardando estación:", error);
      alert("Error al guardar estación");
    }
  };

  // Abrir modal de actualizar precios
  const handleOpenPrecios = (estacion) => {
    setPreciosEstacion(estacion);
    setFormPrecios(estacion.precios_actuales);
    setOpenPrecios(true);
  };

  // Actualizar precios
  const handleActualizarPrecios = async () => {
    try {
      const response = await fetch(
        `${API_URL}/api/estaciones/${preciosEstacion.id_estacion}/precios`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ precios: formPrecios }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
        return;
      }

      const resultado = await response.json();
      
      // Mostrar si el envío TCP fue exitoso
      if (resultado._envio_tcp) {
        if (resultado._envio_tcp.exitoso) {
          alert(`✅ Precios actualizados y enviados a ${resultado._envio_tcp.ip}:${resultado._envio_tcp.puerto}`);
        } else {
          alert(`⚠️ Precios actualizados en BD pero no se pudo conectar con la estación`);
        }
      }

      setOpenPrecios(false);
      cargarEstaciones();
    } catch (error) {
      console.error("Error actualizando precios:", error);
      alert("Error al actualizar precios");
    }
  };

  // Confirmar eliminación
  const confirmDelete = (id) => {
    setDeleteId(id);
    setOpenDelete(true);
  };

  // Eliminar estación
  const handleDelete = async () => {
    try {
      const response = await fetch(`${API_URL}/api/estaciones/${deleteId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        alert("Error al eliminar estación");
        return;
      }

      setOpenDelete(false);
      cargarEstaciones();
    } catch (error) {
      console.error("Error eliminando estación:", error);
      alert("Error al eliminar estación");
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
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">
              Gestión de Estaciones
            </h1>
            <p className="text-gray-600 mt-2">
              Administra las estaciones de servicio y actualiza sus precios
            </p>
          </div>
          <Button
            onClick={() => handleOpenEdit()}
            className="bg-[#F26E22] hover:bg-[#d65e1d] text-white"
          >
            <PlusIcon className="mr-2" />
            Nueva Estación
          </Button>
        </div>

        {/* Lista de estaciones */}
        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-500">Cargando estaciones...</p>
          </div>
        ) : estaciones.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-500">No hay estaciones registradas</p>
            <Button
              onClick={() => handleOpenEdit()}
              className="mt-4 bg-[#F26E22] hover:bg-[#d65e1d] text-white"
            >
              Crear primera estación
            </Button>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {estaciones.map((estacion) => (
              <div
                key={estacion.id_estacion}
                className="bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-all p-6"
              >
                {/* Header de la card */}
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-800 mb-1">
                      {estacion.nombre}
                    </h3>
                    <p className="text-sm text-gray-500">ID: {estacion.id_estacion}</p>
                  </div>
                  <span
                    className={`inline-block px-3 py-1 text-xs font-semibold rounded-full ${getEstadoBadgeClass(
                      estacion.estado
                    )}`}
                  >
                    {estacion.estado}
                  </span>
                </div>

                {/* Información de conexión */}
                <div className="mb-4 pb-4 border-b">
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">IP:</span> {estacion.ip}
                  </p>
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Puerto:</span> {estacion.puerto}
                  </p>
                </div>

                {/* Precios actuales */}
                <div className="mb-4">
                  <p className="text-sm font-semibold text-gray-700 mb-2">
                    Precios actuales:
                  </p>
                  <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                    <div>⛽ 93: ${estacion.precios_actuales.precio_93}</div>
                    <div>⛽ 95: ${estacion.precios_actuales.precio_95}</div>
                    <div>⛽ 97: ${estacion.precios_actuales.precio_97}</div>
                    <div>🛢️ Diesel: ${estacion.precios_actuales.precio_diesel}</div>
                  </div>
                </div>

                {/* Botones de acción */}
                <div className="flex gap-2 flex-wrap">
                  <Button
                    onClick={() => handleOpenPrecios(estacion)}
                    size="sm"
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    <UpdateIcon className="mr-1" />
                    Precios
                  </Button>
                  <Button
                    onClick={() => handleOpenEdit(estacion)}
                    size="sm"
                    variant="outline"
                    className="border-[#F26E22] text-[#F26E22] hover:bg-orange-50"
                  >
                    <Pencil1Icon className="mr-1" />
                    Editar
                  </Button>
                  <Link href={`/estaciones/${estacion.id_estacion}/historico`}>
                    <Button
                      size="sm"
                      variant="outline"
                      className="border-gray-300 text-gray-700 hover:bg-gray-50"
                    >
                      📊 Historial
                    </Button>
                  </Link>
                  <Button
                    onClick={() => confirmDelete(estacion.id_estacion)}
                    size="sm"
                    variant="outline"
                    className="border-red-300 text-red-600 hover:bg-red-50"
                  >
                    <TrashIcon />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Modal Crear/Editar Estación */}
        <Dialog open={openEdit} onOpenChange={setOpenEdit}>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="text-lg font-semibold text-gray-800">
                {editing ? "Editar Estación" : "Nueva Estación"}
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-3">
              <div>
                <label className="text-sm font-medium text-gray-700">Nombre</label>
                <Input
                  placeholder="Ej: Estación Norte"
                  value={form.nombre}
                  onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Dirección IP</label>
                <Input
                  placeholder="Ej: 192.168.1.100"
                  value={form.ip}
                  onChange={(e) => setForm({ ...form, ip: e.target.value })}
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Puerto</label>
                <Input
                  type="number"
                  placeholder="5000"
                  value={form.puerto}
                  onChange={(e) =>
                    setForm({ ...form, puerto: parseInt(e.target.value) || 5000 })
                  }
                />
              </div>

              {!editing && (
                <>
                  <div className="border-t pt-4">
                    <label className="text-sm font-medium text-gray-700 mb-2 block">
                      Precios Iniciales
                    </label>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-xs text-gray-600">Gasolina 93</label>
                        <Input
                          type="number"
                          value={form.precios_actuales.precio_93}
                          onChange={(e) =>
                            setForm({
                              ...form,
                              precios_actuales: {
                                ...form.precios_actuales,
                                precio_93: parseInt(e.target.value) || 0,
                              },
                            })
                          }
                        />
                      </div>
                      <div>
                        <label className="text-xs text-gray-600">Gasolina 95</label>
                        <Input
                          type="number"
                          value={form.precios_actuales.precio_95}
                          onChange={(e) =>
                            setForm({
                              ...form,
                              precios_actuales: {
                                ...form.precios_actuales,
                                precio_95: parseInt(e.target.value) || 0,
                              },
                            })
                          }
                        />
                      </div>
                      <div>
                        <label className="text-xs text-gray-600">Gasolina 97</label>
                        <Input
                          type="number"
                          value={form.precios_actuales.precio_97}
                          onChange={(e) =>
                            setForm({
                              ...form,
                              precios_actuales: {
                                ...form.precios_actuales,
                                precio_97: parseInt(e.target.value) || 0,
                              },
                            })
                          }
                        />
                      </div>
                      <div>
                        <label className="text-xs text-gray-600">Diesel</label>
                        <Input
                          type="number"
                          value={form.precios_actuales.precio_diesel}
                          onChange={(e) =>
                            setForm({
                              ...form,
                              precios_actuales: {
                                ...form.precios_actuales,
                                precio_diesel: parseInt(e.target.value) || 0,
                              },
                            })
                          }
                        />
                      </div>
                    </div>
                  </div>
                </>
              )}

              <div className="flex justify-end gap-3 pt-3">
                <Button
                  variant="outline"
                  onClick={() => setOpenEdit(false)}
                  className="border-[#F26E22] text-[#F26E22] hover:bg-orange-50"
                >
                  Cancelar
                </Button>
                <Button
                  onClick={handleSave}
                  className="bg-[#F26E22] hover:bg-[#d65e1d] text-white"
                >
                  {editing ? "Guardar Cambios" : "Crear Estación"}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        {/* Modal Actualizar Precios */}
        <Dialog open={openPrecios} onOpenChange={setOpenPrecios}>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="text-lg font-semibold text-gray-800">
                Actualizar Precios - {preciosEstacion?.nombre}
              </DialogTitle>
              <DialogDescription>
                Los nuevos precios se guardarán en el historial y se enviarán automáticamente a la estación.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 mt-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-sm font-medium text-gray-700">Gasolina 93</label>
                  <Input
                    type="number"
                    value={formPrecios.precio_93}
                    onChange={(e) =>
                      setFormPrecios({
                        ...formPrecios,
                        precio_93: parseInt(e.target.value) || 0,
                      })
                    }
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">Gasolina 95</label>
                  <Input
                    type="number"
                    value={formPrecios.precio_95}
                    onChange={(e) =>
                      setFormPrecios({
                        ...formPrecios,
                        precio_95: parseInt(e.target.value) || 0,
                      })
                    }
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">Gasolina 97</label>
                  <Input
                    type="number"
                    value={formPrecios.precio_97}
                    onChange={(e) =>
                      setFormPrecios({
                        ...formPrecios,
                        precio_97: parseInt(e.target.value) || 0,
                      })
                    }
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">Diesel</label>
                  <Input
                    type="number"
                    value={formPrecios.precio_diesel}
                    onChange={(e) =>
                      setFormPrecios({
                        ...formPrecios,
                        precio_diesel: parseInt(e.target.value) || 0,
                      })
                    }
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3">
                <Button
                  variant="outline"
                  onClick={() => setOpenPrecios(false)}
                  className="border-[#F26E22] text-[#F26E22] hover:bg-orange-50"
                >
                  Cancelar
                </Button>
                <Button
                  onClick={handleActualizarPrecios}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  Actualizar y Enviar
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        {/* Modal Confirmar Eliminación */}
        <Dialog open={openDelete} onOpenChange={setOpenDelete}>
          <DialogContent className="sm:max-w-sm">
            <DialogHeader>
              <DialogTitle className="text-lg font-semibold text-gray-800">
                Confirmar Eliminación
              </DialogTitle>
              <DialogDescription>
                ¿Seguro que deseas eliminar esta estación? Esta acción no se puede deshacer y se perderá todo el historial de precios.
              </DialogDescription>
            </DialogHeader>
            <div className="flex justify-end gap-3 pt-4">
              <Button
                variant="outline"
                onClick={() => setOpenDelete(false)}
                className="border-gray-300 text-gray-700"
              >
                Cancelar
              </Button>
              <Button
                onClick={handleDelete}
                className="bg-red-600 hover:bg-red-700 text-white"
              >
                Eliminar
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </main>
  );
}
