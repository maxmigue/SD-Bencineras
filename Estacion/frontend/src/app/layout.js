import "./globals.css";
import { Poppins } from "next/font/google";

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
      {/* Aplica Poppins por defecto a todo el sitio */}
      <body className="font-poppins bg-gray-50">{children}</body>
    </html>
  );
}
