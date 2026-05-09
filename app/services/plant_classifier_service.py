# app/services/plant_classifier_service.py
from PIL import Image
from app.models.model_loader import model_loader
from app.utils.logger import logger
import random

class PlantClassifierService:
    def __init__(self):
        self.model = model_loader.model
        self.processor = model_loader.processor
        self.device = model_loader.device
        self.is_mock = self.model == "MockModelInstance"

    def predict(self, image: Image.Image) -> dict:
        """
        Performs real inference using the loaded model.
        Includes a strict organic filter to prevent false positives.
        """
        # 1. Organic check (HSV analysis) + Bounding Box
        is_plant, bbox = self._detect_organic_area(image)
        
        # STRICT RULE: If the CV filter doesn't see a clear plant, we stop.
        if not is_plant:
            return self._no_detection_result("Escaneando... No se detecta entidad vegetal clara.")

        # 2. Mock fallback
        if self.is_mock:
            result = self._mock_predict(image)
            result["bbox"] = bbox
            return result

        # 3. Real Inference
        try:
            import torch
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
            
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            conf, class_idx = torch.max(probabilities, dim=-1)
            raw_confidence = float(conf.item())
            
            # Calibration: Scale 0.95 -> 0.80 approx to reflect model specificity
            calibrated_confidence = raw_confidence * 0.85
            
            if calibrated_confidence < 0.3:
                return self._no_detection_result("Baja confianza en la identificación.")

            label = self.model.config.id2label[class_idx.item()]
            result = self._format_result(label, calibrated_confidence)
            result["bbox"] = bbox 
            return result

        except Exception as e:
            logger.error(f"Inference error: {str(e)}")
            return self._no_detection_result("Error de análisis interno.")

    def _detect_organic_area(self, image: Image.Image) -> tuple[bool, dict]:
        """
        CV check for organic matter. 
        Adjusted to support woody plants with small leaves.
        """
        try:
            import numpy as np
            import cv2
            
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
            
            # WIDER GREEN (Includes olive and dark greens)
            lower_green = np.array([25, 30, 30])
            upper_green = np.array([95, 255, 255])
            mask_green = cv2.inRange(hsv, lower_green, upper_green)
            
            # WIDER BROWN (For stems and trunks)
            lower_brown = np.array([10, 40, 20])
            upper_brown = np.array([25, 255, 180])
            mask_brown = cv2.inRange(hsv, lower_brown, upper_brown)
            
            # Logic: We count both, but we need at least A BIT of green
            green_pixels = cv2.countNonZero(mask_green)
            brown_pixels = cv2.countNonZero(mask_brown)
            total_pixels = img_cv.shape[0] * img_cv.shape[1]
            
            # Thresholds: 
            # 1. Total organic matter > 1.5%
            # 2. Minimum green > 0.2% (to ensure it's a plant, not just a chair)
            organic_ratio = (green_pixels + brown_pixels) / total_pixels
            green_ratio = green_pixels / total_pixels
            
            is_likely_plant = organic_ratio > 0.015 and green_ratio > 0.002
            
            bbox = {"x": 0, "y": 0, "w": 0, "h": 0}
            if is_likely_plant:
                # Combine masks for the hitbox
                mask = cv2.bitwise_or(mask_green, mask_brown)
                kernel = np.ones((5,5), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if contours:
                    # Minimum area reduced to capture small branches
                    valid_contours = [c for c in contours if cv2.contourArea(c) > 300]
                    if valid_contours:
                        all_pts = np.concatenate(valid_contours)
                        x, y, w, h = cv2.boundingRect(all_pts)
                        img_h, img_w = img_cv.shape[:2]
                        bbox = {
                            "x": round((x / img_w) * 100, 1),
                            "y": round((y / img_h) * 100, 1),
                            "w": round((w / img_w) * 100, 1),
                            "h": round((h / img_h) * 100, 1)
                        }
            
            return is_likely_plant, bbox
            
        except Exception as e:
            logger.error(f"Organic area detection error: {str(e)}")
            return True, {"x": 0, "y": 0, "w": 0, "h": 0}

    def _format_result(self, label: str, confidence: float) -> dict:
        plant_translation = {
            "Tomato": "Especie similar a Tomate", 
            "Potato": "Especie similar a Papa", 
            "Pepper bell": "Especie similar a Pimiento",
            "Corn": "Especie similar a Maíz", 
            "Grape": "Especie similar a Uva", 
            "Apple": "Especie similar a Manzana",
            "Cherry": "Especie similar a Cereza", 
            "Strawberry": "Especie similar a Fresa", 
            "Soybean": "Especie similar a Soja",
            "Squash": "Especie similar a Calabaza", 
            "Orange": "Especie similar a Naranja", 
            "Peach": "Especie similar a Durazno",
            "Blueberry": "Especie similar a Arándano", 
            "Raspberry": "Especie similar a Frambuesa"
        }
        
        parts = label.split("___")
        plant_raw = parts[0].replace("_", " ")
        plant_es = plant_translation.get(plant_raw, f"Especie similar a {plant_raw}")
        
        disease_raw = parts[1].replace("_", " ") if len(parts) > 1 else "Sano"
        status = "Sano" if "healthy" in disease_raw.lower() or "sano" in disease_raw.lower() else "Enfermo"
        
        return {
            "domain": "Botánica",
            "primary_label": f"{plant_es}",
            "summary": f"Similitud morfológica con {plant_raw} ({status}).",
            "confidence": round(confidence, 2),
            "attributes": {
                "similitud_visual": f"{round(confidence*100)}%",
                "estado_salud": status,
                "nota": "IA calibrada para especies PlantVillage",
                "analizador": "NV_VISION_PRO_V1"
            },
            "categories": [
                {"label": f"{plant_raw}: {status}", "confidence": round(confidence, 2)},
                {"label": "Otras especies", "confidence": round(1 - confidence, 2)}
            ],
            "recommendation": "¡Todo se ve bien!" if status == "Sano" else "Se detectan patrones inusuales."
        }

    def _no_detection_result(self, reason: str) -> dict:
        return {
            "domain": "Desconocido",
            "primary_label": "Escaneando...",
            "summary": reason,
            "confidence": 0.0,
            "attributes": {"estado": "Buscando entidad..."},
            "categories": [],
            "recommendation": "Apunta a una planta para el hitbox.",
            "bbox": {"x": 0, "y": 0, "w": 0, "h": 0}
        }

    def _mock_predict(self, image: Image.Image) -> dict:
        return self._format_result("Tomato___Healthy", 0.95)
