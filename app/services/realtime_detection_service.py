# app/services/realtime_detection_service.py
from app.services.image_preprocessor_service import ImagePreprocessorService
from app.services.plant_classifier_service import PlantClassifierService
from app.utils.logger import logger

class RealtimeDetectionService:
    def __init__(self):
        self.preprocessor = ImagePreprocessorService()
        self.classifier = PlantClassifierService()

    async def detect(self, image_bytes: bytes) -> dict:
        """
        Orchestrates the detection flow: Preprocess -> Classify.
        """
        try:
            # 1. Preprocess
            processed_image = self.preprocessor.process_bytes(image_bytes)
            
            # 2. Classify
            prediction_data = self.classifier.predict(processed_image)
            
            return {
                "status": "success",
                "type": "analysis_result",
                "data": prediction_data
            }
        except ValueError as ve:
            # Expected validation errors
            return {
                "status": "error",
                "type": "invalid_frame",
                "message": str(ve)
            }
        except Exception as e:
            # Unexpected errors
            logger.error(f"Unexpected error during detection: {str(e)}")
            return {
                "status": "error",
                "type": "internal_error",
                "message": "An unexpected error occurred during processing."
            }
        finally:
            # Clean up local references to help GC
            processed_image = None
