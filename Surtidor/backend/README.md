# Surtidor Backend

Este es el backend para el surtidor simulado.

## Instalación

1.  Crea un entorno virtual:
    ```bash
    python -m venv venv
    ```
2.  Activa el entorno:
    -   Windows: `venv\Scripts\activate`
    -   macOS/Linux: `source venv/bin/activate`
3.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

## Ejecución

Para iniciar el servidor, ejecuta:
```bash
uvicorn main:app --reload --port 8000
```
El backend del surtidor estará disponible en `http://localhost:8000`.
