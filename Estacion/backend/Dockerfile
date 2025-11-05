# Usa una imagen base oficial de Python y Node.js
FROM node:20-bullseye-slim

# Instala Python y pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del backend
COPY . .

# Instala dependencias de Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Instala dependencias de Node.js
RUN npm install

# Expone los puertos necesarios
EXPOSE 8000 4000 5000

# Comando para iniciar FastAPI y el bridge
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]