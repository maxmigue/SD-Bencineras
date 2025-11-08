# Imagen base de Node.js
FROM node:20-alpine

# Establece el directorio de trabajo
WORKDIR /app

# Copia archivos de dependencias
COPY package*.json ./

# Instala dependencias
RUN npm install

# Copia el resto del código fuente
COPY . .

# Construye la aplicación Next.js
RUN npm run build

# Expone el puerto del frontend
EXPOSE 3000

# Comando para iniciar en modo producción
CMD ["npm", "start"]
