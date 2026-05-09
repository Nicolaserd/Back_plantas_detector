# app/models/model_loader.py
from app.core import config
from app.utils.logger import logger

class ModelLoader:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        # Using a model that is definitely compatible with transformers AutoModel
        model_id = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
        logger.info(f"Loading real AI model: {model_id}...")
        try:
            from transformers import AutoModelForImageClassification, AutoImageProcessor
            import torch
            
            self._processor = AutoImageProcessor.from_pretrained(model_id)
            self._model = AutoModelForImageClassification.from_pretrained(model_id)
            self._model.eval()
            
            # Check for GPU
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            self._model.to(self._device)
            
            logger.info(f"Model loaded successfully on {self._device}.")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            # Fallback to mock if loading fails
            self._model = "MockModelInstance"
            self._processor = None
            self._device = "cpu"

    @property
    def model(self):
        return self._model
        
    @property
    def processor(self):
        return self._processor
        
    @property
    def device(self):
        return self._device

# Singleton instance
model_loader = ModelLoader()
