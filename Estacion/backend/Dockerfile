# Usa una imagen base oficial de Python y Node.js
FROM node:20-bullseye-slim

# Instala Python y pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean

# Establece el directorio de trabajo
WORKDIR /app

# Copia primero los archivos de dependencias
COPY requirements.txt package.json ./

# Instala dependencias de Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Instala dependencias de Node.js
RUN npm install

# Copia el resto de los archivos del backend
COPY . .

# Hacer ejecutable el script de inicio
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expone los puertos necesarios
EXPOSE 8000 4000 5000

# Comando para iniciar todos los servicios
CMD ["/app/start.sh"]