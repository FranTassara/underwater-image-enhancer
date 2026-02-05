"""
Módulo de mejoramiento de imágenes subacuáticas.
Dos métodos disponibles:
  - WaterNet (IA con PyTorch)
  - OpenCV (pipeline tradicional, sin IA)
"""

import os
import cv2
import numpy as np
from PIL import Image

# --- Configuración ---
MAX_WIDTH = 1920  # Redimensionar imágenes grandes para evitar problemas de memoria


def _resize_if_needed(img):
    """Redimensiona la imagen si excede MAX_WIDTH, manteniendo proporción."""
    h, w = img.shape[:2]
    if w > MAX_WIDTH:
        scale = MAX_WIDTH / w
        new_w = MAX_WIDTH
        new_h = int(h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return img


# =============================================================================
# Método 1: WaterNet (IA con PyTorch)
# =============================================================================

_waternet_model = None  # Cache del modelo para no recargarlo cada vez
_waternet_preprocess = None
_waternet_postprocess = None


def _load_waternet():
    """Carga el modelo WaterNet via PyTorch Hub (descarga pesos la primera vez)."""
    global _waternet_model, _waternet_preprocess, _waternet_postprocess
    if _waternet_model is None:
        import torch
        _waternet_preprocess, _waternet_postprocess, _waternet_model = torch.hub.load(
            "tnwei/waternet", "waternet", force_reload=False
        )
        _waternet_model.eval()
    return _waternet_preprocess, _waternet_postprocess, _waternet_model


def enhance_waternet(input_path, output_path):
    """
    Mejora una imagen subacuática usando WaterNet.

    Args:
        input_path: Ruta a la imagen original
        output_path: Ruta donde guardar la imagen mejorada

    Returns:
        output_path si fue exitoso, None si hubo error
    """
    try:
        import torch

        preprocess, postprocess, model = _load_waternet()

        img = cv2.imread(input_path)
        if img is None:
            return None

        img = _resize_if_needed(img)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # WaterNet espera la imagen original + 3 versiones preprocesadas
        with torch.no_grad():
            rgb_ten, wb_ten, he_ten, gc_ten = preprocess(rgb)
            output_ten = model(rgb_ten, wb_ten, he_ten, gc_ten)

        result = postprocess(output_ten)
        result_bgr = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)

        cv2.imwrite(output_path, result_bgr)
        return output_path

    except Exception as e:
        print(f"Error en WaterNet: {e}")
        return None


# =============================================================================
# Método 2: Pipeline OpenCV (sin IA)
# =============================================================================

def _white_balance(img):
    """Corrección de balance de blancos en espacio LAB."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    l, a, b = cv2.split(lab)
    a = a - np.mean(a) + 128
    b = b - np.mean(b) + 128
    lab = cv2.merge([l, np.clip(a, 0, 255), np.clip(b, 0, 255)])
    return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)


def _apply_clahe(img, clip_limit=3.0, tile_size=(8, 8)):
    """CLAHE en el canal L del espacio LAB para mejorar contraste."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
    l = clahe.apply(l)
    lab = cv2.merge([l, a, b])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def _gamma_correction(img, gamma=1.2):
    """Corrección gamma para ajustar brillo."""
    table = np.array([
        ((i / 255.0) ** (1.0 / gamma)) * 255 for i in range(256)
    ]).astype("uint8")
    return cv2.LUT(img, table)


def _sharpen(img):
    """Mejora la nitidez con unsharp mask."""
    gaussian = cv2.GaussianBlur(img, (0, 0), 3)
    return cv2.addWeighted(img, 1.5, gaussian, -0.5, 0)


def enhance_opencv(input_path, output_path):
    """
    Mejora una imagen subacuática usando pipeline OpenCV.

    Args:
        input_path: Ruta a la imagen original
        output_path: Ruta donde guardar la imagen mejorada

    Returns:
        output_path si fue exitoso, None si hubo error
    """
    try:
        img = cv2.imread(input_path)
        if img is None:
            return None

        img = _resize_if_needed(img)
        img = _white_balance(img)
        img = _apply_clahe(img, clip_limit=3.0)
        img = _gamma_correction(img, gamma=1.2)
        img = _sharpen(img)

        cv2.imwrite(output_path, img)
        return output_path

    except Exception as e:
        print(f"Error en OpenCV pipeline: {e}")
        return None
