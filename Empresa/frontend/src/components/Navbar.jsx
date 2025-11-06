"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="bg-[#F26E22] shadow-md">
      <div className="max-w-7xl mx-auto flex justify-between items-center px-6 py-4">
        <Link href="/">
          <h1 className="text-2xl font-bold text-white cursor-pointer hover:text-white/90 transition-colors">
            🏢 Empresa Bencinera
          </h1>
        </Link>

        <div className="flex items-center gap-6">
          <Link
            href="/"
            className={`text-sm font-medium transition-colors ${
              pathname === "/"
                ? "underline text-white"
                : "text-white/80 hover:text-white"
            }`}
          >
            Dashboard
          </Link>

          <Link
            href="/estaciones"
            className={`text-sm font-medium transition-colors ${
              pathname.startsWith("/estaciones")
                ? "underline text-white"
                : "text-white/80 hover:text-white"
            }`}
          >
            Gestión de Estaciones
          </Link>

          <Link
            href="/transacciones"
            className={`text-sm font-medium transition-colors ${
              pathname.startsWith("/transacciones")
                ? "underline text-white"
                : "text-white/80 hover:text-white"
            }`}
          >
            Transacciones
          </Link>
        </div>
      </div>
    </nav>
  );
}
