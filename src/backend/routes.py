import cv2
import numpy as np

from fastapi import APIRouter, UploadFile, File, HTTPException

from .services.detection_service import DetectionService


router = APIRouter(prefix="/api")


detection_service = DetectionService()


@router.get("/status")
def status():
    return {
        "backend": "ONLINE",
        "ai": "READY"
    }


@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...)
):

    contents = await file.read()

    image_array = np.frombuffer(
        contents,
        dtype=np.uint8
    )

    frame = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if frame is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file"
        )

    result = detection_service.analyze(frame)

    return result