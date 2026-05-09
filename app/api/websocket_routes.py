# app/api/websocket_routes.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.realtime_detection_service import RealtimeDetectionService
from app.utils.logger import logger
import json

router = APIRouter()
detection_service = RealtimeDetectionService()

@router.websocket("/ws/analyze")
async def websocket_detect(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket client connected.")
    
    try:
        while True:
            # Receive frames as bytes
            try:
                image_bytes = await websocket.receive_bytes()
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected normally.")
                break
            except Exception as e:
                logger.error(f"Error receiving bytes: {str(e)}")
                break

            # Process detection
            result = await detection_service.detect(image_bytes)
            
            # Send result JSON
            await websocket.send_json(result)
            
            # Help memory management
            image_bytes = None
            
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        logger.info("Closing WebSocket connection.")
