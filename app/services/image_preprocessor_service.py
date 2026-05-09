# app/services/image_preprocessor_service.py
import io
from PIL import Image
from app.core import config
from app.utils.logger import logger

class ImagePreprocessorService:
    @staticmethod
    def process_bytes(image_bytes: bytes) -> Image.Image:
        """
        Validates and preprocesses image bytes.
        """
        # Validate size
        size_mb = len(image_bytes) / (1024 * 1024)
        if size_mb > config.MAX_FRAME_SIZE_MB:
            logger.warning(f"Frame rejected: Size {size_mb:.2f}MB exceeds limit {config.MAX_FRAME_SIZE_MB}MB")
            raise ValueError(f"Image size {size_mb:.2f}MB exceeds the maximum allowed size of {config.MAX_FRAME_SIZE_MB}MB.")

        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB (removes alpha channel if present)
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            # Resize
            image = image.resize((config.MODEL_IMAGE_SIZE, config.MODEL_IMAGE_SIZE))
            
            return image
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise ValueError("Invalid image format or corrupted data.")
