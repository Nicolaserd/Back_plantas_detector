# Plant Detection API Backend

Backend en Python usando FastAPI para una aplicación web de detección de plantas mediante video en vivo. Este servicio está diseñado para procesar frames de imagen en tiempo real a través de WebSockets.

## Características
- **Stateless**: No guarda información en bases de datos, historial ni archivos.
- **Tiempo Real**: Conexión mediante WebSockets para baja latencia.
- **Modular**: Arquitectura limpia separando rutas, servicios y modelos.
- **Containerización**: Listo para desplegar con Docker.

## Requisitos Técnicos
- Python 3.11+
- No utiliza bases de datos (PostgreSQL, SQLite, etc.).
- No utiliza variables de entorno (configuración centralizada en `app/core/config.py`).

## Instalación Local

1. Clonar el repositorio.
2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución Local

Para iniciar el servidor de desarrollo:
```bash
uvicorn app.main:app --reload
```
El servidor estará disponible en `http://localhost:8000`.

## Endpoints

### HTTP
- `GET /api/health`: Verifica el estado del servicio.
  - **Respuesta**: `{"status": "ok", "service": "Plant Detection API", "mode": "realtime-only"}`

### WebSocket
- `WS /ws/detect`: Endpoint para envío de frames.
  - **Entrada**: Bytes de imagen (JPG/PNG/WebP).
  - **Salida**: JSON con la predicción detallada o error.

## Ejemplo de Conexión WebSocket (Frontend)

```javascript
const socket = new WebSocket('ws://localhost:8000/ws/detect');

socket.onopen = () => {
    console.log('Conectado al backend de detección');
};

socket.onmessage = (event) => {
    const response = JSON.parse(event.data);
    console.log('Predicción recibida:', response);
};

// Función para enviar un frame
function sendFrame(blob) {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(blob);
    }
}
```

## Despliegue con Docker

1. Construir la imagen:
   ```bash
   docker build -t plant-detection-api .
   ```
2. Ejecutar el contenedor:
   ```bash
   docker run -p 8000:8000 plant-detection-api
   ```

## Notas para Reemplazo de Modelo

Actualmente, el servicio utiliza un **PlantClassifierService** con predicciones simuladas (Mock). Para integrar un modelo real:
1. Colocar el archivo del modelo en `app/models/plant_model.pt`.
2. Actualizar `app/models/model_loader.py` para cargar el modelo usando la librería correspondiente (PyTorch, TensorFlow, etc.).
3. Implementar la lógica de inferencia real en el método `predict` de `app/services/plant_classifier_service.py`.
# Back_plantas_detector
