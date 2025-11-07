# Usa la imagen oficial de oven/bun con la versión 1.3.1
FROM oven/bun:1.3.1

WORKDIR /app

# Copia los archivos de dependencias primero
COPY bun.lock package.json ./

# Instala dependencias
RUN bun install

# Copia el resto del código fuente
COPY . .

# Construye la app Next.js
RUN bun run build

# Expone el puerto de Next.js
EXPOSE 3000

# Comando para iniciar la app en producción
CMD ["bun", "start"]