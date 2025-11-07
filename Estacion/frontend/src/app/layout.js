import "./globals.css";
import { Poppins } from "next/font/google";
import Navbar from "../components/Navbar";
import { EstacionProvider } from "../contexts/EstacionContext";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-poppins",
});

export const metadata = {
  title: "Estación",
  description: "Gestión de surtidores de gasolina",
};

export default function RootLayout({ children }) {
  return (
    <html lang="es" className={poppins.variable}>
      <body className="font-poppins bg-gray-50 min-h-screen flex flex-col">
        <EstacionProvider>
          <Navbar />
          <main className="flex-1">{children}</main>
        </EstacionProvider>
      </body>
    </html>
  );
}
