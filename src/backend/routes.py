 import sys
import os
import cv2
import numpy as np

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

# AI Service import
from services.detection_service import DetectionService

# Intelligence/Graph import karne ke liye path set kar rahe hain
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from intelligence.routing import CrowdRouter

router = APIRouter(prefix="/api")

# Dono engines start kar rahe hain
detection_service = DetectionService()
crowd_router = CrowdRouter()

@router.get("/status")
def status():
    return {
        "backend": "ONLINE",
        "ai": "READY",
        "routing": "CONNECTED"
    }

# --------------------------------------------------
# 1. AI DETECTION (Ab yeh Graph ko update karega)
# --------------------------------------------------
@router.post("/analyze")
async def analyze_image(
    zone_id: str = Form(..., description="Example: Z1, Z2, Z3"), # Frontend batayega konsa camera hai
    file: UploadFile = File(...)
):
    """
    Upload image -> AI counts people -> Updates Routing Graph
    """
    contents = await file.read()

    if not contents:
        raise HTTPException(status_code=400, detail="Empty image file")

    image_array = np.frombuffer(contents, dtype=np.uint8)
    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    try:
        # AI se log count karwao
        result = detection_service.analyze(frame)
        
        # Total log nikal kar Graph mein update karo!
        total_people = result.get("total_people", 0)
        crowd_router.update_crowd({zone_id: total_people})

        return {
            "message": f"Successfully updated {zone_id} with {total_people} people.",
            "ai_analysis": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


# --------------------------------------------------
# 2. ROUTING APIS (Ab yeh browser mein khulenge!)
# --------------------------------------------------
@router.get("/venue-status")
def get_venue_status():
    """Live map ki density dikhane ke liye"""
    return {
        "status": "success",
        "data": crowd_router.venue_status()
    }

@router.get("/recommendations")
def get_recommendations():
    """CRITICAL ya HIGH risk alerts ke liye"""
    return {
        "status": "success",
        "actions": crowd_router.management_recommendation()
    }

@router.get("/evacuation")
def get_evacuation_routes():
    """Sabse safe rasta nikalne ke liye"""
    return {
        "status": "success",
        "safe_routes": crowd_router.evacuation_routes()
    }