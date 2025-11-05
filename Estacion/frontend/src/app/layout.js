import "./globals.css";
import { Poppins } from "next/font/google";
import Navbar from "../components/Navbar"; // 👈 Importamos componente cliente

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-poppins",
});

export const metadata = {
  title: "Estación X",
  description: "Gestión de surtidores de gasolina",
};

export default function RootLayout({ children }) {
  return (
    <html lang="es" className={poppins.variable}>
      <body className="font-poppins bg-gray-50 min-h-screen flex flex-col">
        <Navbar /> {/* ✅ Navbar ahora separado y cliente */}
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
