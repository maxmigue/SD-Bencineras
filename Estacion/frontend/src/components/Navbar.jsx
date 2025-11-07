"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEstacion } from "../contexts/EstacionContext";

export default function Navbar() {
  const pathname = usePathname();
  const { nombreEstacion } = useEstacion();

  return (
    <nav className="bg-[#F26E22] shadow-md">
      <div className="max-w-6xl mx-auto flex justify-between items-center px-6 py-4">
        <h1 className="text-2xl font-bold text-white">⛽ {nombreEstacion}</h1>

        <div className="flex items-center gap-4">
          <Link
            href="/"
            className={`text-sm font-medium transition-colors ${
              pathname === "/"
                ? "underline text-white"
                : "text-white/80 hover:text-white"
            }`}
          >
            Surtidores
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
