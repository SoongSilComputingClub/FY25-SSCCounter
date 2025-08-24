import io
from typing import Union

from PIL import Image
from ultralytics import YOLO

PERSON_CLASS_ID = 0
_model_singleton: YOLO | None = None

def load_model_once(model_path: str) -> YOLO:
    """Load YOLO model once and reuse the instance.

    Why:
        Model initialization is expensive. Reusing a single instance reduces
        per-request latency and memory thrashing.
    """
    global _model_singleton
    if _model_singleton is None:
        _model_singleton = YOLO(model_path)
    return _model_singleton

def _jpeg_to_rgb_image(jpeg_bytes: bytes) -> Image.Image:
    """Decode JPEG bytes to a PIL RGB image."""
    img = Image.open(io.BytesIO(jpeg_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img

def count_persons(
    model: YOLO,
    jpeg_bytes: bytes,
    conf_thres: float = 0.5,
    img_size: int = 640,
    return_overlay: bool = False
) -> Union[tuple[int, list[dict]], bytes]:
    """Run detection and return person count (and optional overlay image).

    Args:
        model: Loaded YOLO model.
        jpeg_bytes: Single-frame JPEG bytes from ESP32-CAM.
        conf_thres: Confidence threshold for detections.
        img_size: Inference image size.
        return_overlay: If True, return an annotated JPEG instead of counts.

    Returns:
        If return_overlay is False:
            (persons, details) where
            - persons: int, number of 'person' detections
            - details: list of dicts with keys {class_id, score, bbox_xyxy}
        If return_overlay is True:
            Annotated JPEG bytes.
    """
    img = _jpeg_to_rgb_image(jpeg_bytes)
    results = model.predict(img, imgsz=img_size, conf=conf_thres, verbose=False)
    res = results[0]

    persons = 0
    details: list[dict] = []
    if res.boxes is not None and len(res.boxes) > 0:
        classes = res.boxes.cls.cpu().numpy().astype(int)
        confs = res.boxes.conf.cpu().numpy().astype(float)
        xyxy = res.boxes.xyxy.cpu().numpy().astype(float)
        for cls, score, box in zip(classes, confs, xyxy):
            if cls == PERSON_CLASS_ID:
                persons += 1
                details.append(
                    {
                        "class_id": int(cls),
                        "score": float(score),
                        "bbox_xyxy": [float(x) for x in box],
                    }
                )

    if return_overlay:
        plotted = res.plot()  # numpy (BGR)
        img_pil = Image.fromarray(plotted[:, :, ::-1])  # BGR -> RGB
        buff = io.BytesIO()
        img_pil.save(buff, format="JPEG", quality=90)
        return buff.getvalue()

    return persons, details

def detect_with_overlay(
    model: YOLO,
    jpeg_bytes: bytes,
    conf_thres: float = 0.5,
    img_size: int = 640,
) -> tuple[int, list[dict], bytes]:
    """Single inference pass returning (count, details, overlay JPEG)."""
    img = _jpeg_to_rgb_image(jpeg_bytes)
    results = model.predict(img, imgsz=img_size, conf=conf_thres, verbose=False)
    res = results[0]

    persons = 0
    details: list[dict] = []
    if res.boxes is not None and len(res.boxes) > 0:
        classes = res.boxes.cls.cpu().numpy().astype(int)
        confs = res.boxes.conf.cpu().numpy().astype(float)
        xyxy = res.boxes.xyxy.cpu().numpy().astype(float)
        for cls, score, box in zip(classes, confs, xyxy):
            if cls == PERSON_CLASS_ID:
                persons += 1
                details.append(
                    {
                        "class_id": int(cls),
                        "score": float(score),
                        "bbox_xyxy": [float(x) for x in box],
                    }
                )

    plotted = res.plot()  # numpy (BGR)
    img_pil = Image.fromarray(plotted[:, :, ::-1])  # BGR -> RGB
    buff = io.BytesIO()
    img_pil.save(buff, format="JPEG", quality=90)
    overlay_jpeg = buff.getvalue()

    return persons, details, overlay_jpeg