# app/schemas/prediction_schema.py
from pydantic import BaseModel
from typing import List, Optional

class PredictionCategory(BaseModel):
    label: str
    confidence: float

class PredictionData(BaseModel):
    plant: str
    detected_part: str
    health_status: str
    disease: Optional[str] = None
    fruit_detected: bool
    confidence: float
    categories: List[PredictionCategory]
    recommendation: str

class PredictionResponse(BaseModel):
    status: str
    type: str
    data: PredictionData

class ErrorResponse(BaseModel):
    status: str
    type: str
    message: str
