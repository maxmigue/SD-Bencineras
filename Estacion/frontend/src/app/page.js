"use client";

import { useState, useEffect } from "react";
import { io } from "socket.io-client";
import { Button } from "../components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "../components/ui/dialog";
import { Input } from "../components/ui/input";
import { PlusIcon } from "@radix-ui/react-icons";

import { useEstacion } from "../contexts/EstacionContext";

// ✅ Conexión WebSocket establecida al iniciar
export default function HomePage() {
  const [surtidores, setSurtidores] = useState([]);
  const { nombreEstacion, precios } = useEstacion();
  const [openEdit, setOpenEdit] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteId, setDeleteId] = useState(null);
  const [form, setForm] = useState({ nombre: "", ip: "", puerto: "" });

  useEffect(() => {
    const socket = io("http://localhost:4001", {
      reconnectionDelayMax: 10000,
      reconnectionAttempts: 5,
      transports: ["websocket", "polling"]
    });
  
    socket.on("connect", () => {
      console.log("✅ Conectado al WebSocket bridge");
    });

    socket.on("connect_error", (error) => {
      console.error("❌ Error de conexión:", error);
    });
  
    socket.on("estadoSurtidores", (data) => {
      console.log("📡 Datos recibidos:", data);
      if (Array.isArray(data)) {
        setSurtidores(data);
      } else if (data && typeof data === 'object') {
        setSurtidores(prev => {
          const exists = prev.find(s => s.id === data.id);
          if (exists) {
            return prev.map(s => s.id === data.id ? data : s);
          }
          return [...prev, data];
        });
      }
    });
  
    socket.on("disconnect", (reason) => {
      console.log("❌ Desconectado del WebSocket bridge:", reason);
    });

    return () => {
      console.log("🔄 Limpiando conexión WebSocket");
      socket.disconnect();
    };
  }, []);
  

  // ✏️ Modal editar
  const handleOpenEdit = (surtidor) => {
    if (surtidor) {
      setEditing(surtidor);
      setForm(surtidor);
    } else {
      setEditing(null);
      setForm({ nombre: "", ip: "", puerto: "" });
    }
    setOpenEdit(true);
  };

  // 💾 Guardar o agregar
  const handleSave = () => {
    if (editing) {
      setSurtidores((prev) =>
        prev.map((s) => (s.id === editing.id ? { ...editing, ...form } : s))
      );
    } else {
      const nuevo = {
        id: Date.now(),
        ...form,
        estado: "Parado",
        precios: { gasolina93: 0, gasolina95: 0, gasolina97: 0, diesel: 0 },
      };
      setSurtidores((prev) => [...prev, nuevo]);
    }
    setOpenEdit(false);
  };

  // ❌ Eliminar
  const confirmDelete = (id) => {
    setDeleteId(id);
    setOpenDelete(true);
  };
  const handleDelete = () => {
    setSurtidores((prev) => prev.filter((s) => s.id !== deleteId));
    setOpenDelete(false);
  };

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col">

      {/* TARJETA DE PRECIOS ACTUALES */}
      <section className="max-w-5xl mx-auto mt-10 px-4 w-full">
        <div className="bg-gradient-to-r from-orange-500 to-orange-600 rounded-xl shadow-lg p-6 text-white">
          <h2 className="font-poppins text-2xl font-bold mb-2">
            {nombreEstacion}
          </h2>
          <div className="flex items-center gap-2 mb-4">
            <span className="text-lg">💰 Precios Actuales</span>
            <span className="text-sm font-normal bg-white/20 px-3 py-1 rounded-full">
              En tiempo real
            </span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <p className="text-sm font-medium mb-1">Gasolina 93</p>
              <p className="text-3xl font-bold">${precios.precio_93}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <p className="text-sm font-medium mb-1">Gasolina 95</p>
              <p className="text-3xl font-bold">${precios.precio_95}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <p className="text-sm font-medium mb-1">Gasolina 97</p>
              <p className="text-3xl font-bold">${precios.precio_97}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <p className="text-sm font-medium mb-1">Diésel</p>
              <p className="text-3xl font-bold">${precios.precio_diesel}</p>
            </div>
          </div>
        </div>
      </section>

      {/* LISTA DE SURTIDORES */}
      <section className="flex-1 max-w-5xl mx-auto mt-10 px-4 w-full">
        <h2 className="font-poppins text-3xl font-bold text-gray-800 mb-6">
          Surtidores en tiempo real
        </h2>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {surtidores.map((s) => (
            <div
              key={s.id}
              className="bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-all p-5 flex flex-col justify-between"
            >
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-1">
                  {s.nombre || "Surtidor sin nombre"}
                </h3>
                {s.ip && (
                  <p className="text-sm text-gray-500">IP: {s.ip}</p>
                )}
                {s.puerto && (
                  <p className="text-sm text-gray-500 mb-3">Puerto: {s.puerto}</p>
                )}

                <span
                  className={`inline-block px-3 py-1 text-xs font-semibold rounded-full ${
                    s.estado?.toLowerCase().includes("cargando")
                      ? "bg-green-100 text-green-700"
                      : "bg-gray-100 text-gray-700"
                  }`}
                >
                  {s.estado || "Desconocido"}
                </span>

                {/* Precios */}
                {s.precios && (
                  <div className="mt-4 border-t pt-3">
                    <p className="text-sm font-semibold text-gray-700 mb-2">
                      Precios actuales:
                    </p>
                    <ul className="space-y-1 text-sm text-gray-600">
                      <li>⛽ Gasolina 93: ${s.precios.gasolina93}</li>
                      <li>⛽ Gasolina 95: ${s.precios.gasolina95}</li>
                      <li>⛽ Gasolina 97: ${s.precios.gasolina97}</li>
                      <li>🛢️ Diésel: ${s.precios.diesel}</li>
                    </ul>
                  </div>
                )}
              </div>

            </div>
          ))}
        </div>
      </section>

      {/* DIALOG EDITAR */}
      <Dialog open={openEdit} onOpenChange={setOpenEdit}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-lg font-semibold text-gray-800">
              {editing ? "Editar Surtidor" : "Agregar Surtidor"}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 mt-3">
            <Input
              placeholder="Nombre del surtidor"
              value={form.nombre}
              onChange={(e) => setForm({ ...form, nombre: e.target.value })}
            />
            <Input
              placeholder="Dirección IP"
              value={form.ip}
              onChange={(e) => setForm({ ...form, ip: e.target.value })}
            />
            <Input
              placeholder="Puerto"
              value={form.puerto}
              onChange={(e) => setForm({ ...form, puerto: e.target.value })}
            />
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
                {editing ? "Guardar Cambios" : "Agregar"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* DIALOG ELIMINAR */}
      <Dialog open={openDelete} onOpenChange={setOpenDelete}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle className="text-lg font-semibold text-gray-800">
              Confirmar eliminación
            </DialogTitle>
            <DialogDescription>
              ¿Seguro que deseas eliminar este surtidor? Esta acción no se puede deshacer.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end gap-3 pt-4">
            <Button
              variant="outline"
              onClick={() => setOpenDelete(false)}
              className="border-[#F26E22] text-[#F26E22] hover:bg-orange-50"
            >
              Cancelar
            </Button>
            <Button
              onClick={handleDelete}
              className="bg-[#F26E22] hover:bg-[#d65e1d] text-white"
            >
              Eliminar
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </main>
  );
}
