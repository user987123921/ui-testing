from __future__ import annotations

import os
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class Settings(BaseModel):
    gemini_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    conf_threshold: float = Field(default_factory=lambda: float(os.getenv("CONF_THRESHOLD", "0.25")))
    eligible_classes: List[str] = Field(
        default_factory=lambda: [
            s.strip() for s in os.getenv(
                "ELIGIBLE_CLASSES", "button,input,label,text,menu,menu_item,tab,textbox"
            ).split(",") if s.strip()
        ]
    )
    ocr_langs: List[str] = Field(default_factory=lambda: [s.strip() for s in os.getenv("OCR_LANGS", "en").split(",") if s.strip()])
    model_device: str = Field(default_factory=lambda: os.getenv("MODEL_DEVICE", "auto"))


def load_settings() -> Settings:
    load_dotenv(override=False)
    return Settings()

