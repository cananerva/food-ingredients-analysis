import csv
import re
from pathlib import Path

import numpy as np
import cv2
import pytesseract
import joblib

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "ingredients_dict.csv"
MODEL_PATH = BASE_DIR / "risk_model.joblib"


def load_ingredients_dict():
    """
    ingredients_dict.csv dosyasını okuyup
    her satırı bir dict olacak şekilde liste döndürür.
    """
    items = []
    with CSV_PATH.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append(row)
    return items

INGREDIENTS = load_ingredients_dict()

try:
    RISK_MODEL = joblib.load(MODEL_PATH)
except Exception:
    RISK_MODEL = None


def normalize_text(text: str) -> str:
    """
    Karşılaştırma için basit normalize:
    - Küçük harfe çevir
    - Türkçe karakterleri sadeleştir
    - Noktalama işaretlerini temizle
    - Fazla boşlukları sil
    """
    text = text.strip().lower()

    replace_map = {
        "ş": "s",
        "ç": "c",
        "ğ": "g",
        "ı": "i",
        "ö": "o",
        "ü": "u",
    }
    for k, v in replace_map.items():
        text = text.replace(k, v)

    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def split_ingredients_list(raw_text: str):
    """
    Kullanıcının girdiği 'İçindekiler' metnini parçalar.
    Örnek:
    'Sugar, glucose syrup; E322 (lecithin) ve E202'
    ->
    ['Sugar', 'glucose syrup', 'E322 (lecithin)', 'E202']
    """
    if not raw_text:
        return []

    tmp = raw_text.replace(";", ",")

    parts = [p.strip() for p in tmp.split(",") if p.strip()]

    cleaned = []
    for p in parts:
        subparts = re.split(r"\bve\b|\band\b", p, flags=re.IGNORECASE)
        for s in subparts:
            s = s.strip()
            if s:
                cleaned.append(s)

    return cleaned


def predict_risk_ml(text: str):
    """
    ML modeli ile risk tahmini yapar.
    Model yoksa veya hata olursa None döndürür.
    """
    if RISK_MODEL is None or not text:
        return None
    try:
        pred = RISK_MODEL.predict([text])
        return str(pred[0])
    except Exception:
        return None


def match_single_ingredient(token: str):
    """
    Tek bir içerik parçasını (örneğin 'E202' veya 'glucose syrup')
    ingredients_dict.csv içindeki verilerle eşleştirir.
    Eşleşme yoksa ML modeli ile risk tahmini dener.
    """
    norm_token = normalize_text(token)
    best_match = None

    for item in INGREDIENTS:
        code_norm = normalize_text(item["code"])
        name_norm = normalize_text(item["common_name"])

        if norm_token == code_norm or norm_token == name_norm:
            best_match = item
            break

        if norm_token in name_norm or name_norm in norm_token:
            best_match = item
            break

    if best_match is None:
        ml_risk = predict_risk_ml(token)

        if ml_risk is not None:
            return {
                "ingredient": token,
                "matched": False,
                "predicted_risk": ml_risk,
                "info": "Bu madde sözlükte yok, ML modeli ile risk tahmini yapıldı."
            }

        return {
            "ingredient": token,
            "matched": False,
            "info": "Bu madde veri tabanında bulunamadı."
        }

    return {
        "ingredient": token,
        "matched": True,
        "common_name": best_match["common_name"],
        "category": best_match["category"],
        "risk": best_match["risk"],
        "description": best_match["description"],
    }


def image_bytes_to_text(image_bytes: bytes) -> str:
    """
    Yüklenen resimden (bytes) içindekiler metnini çıkarmaya çalışır.
    Basit OCR pipeline:
    - Bytes -> OpenCV image
    - Gri tonlama
    - Threshold
    - pytesseract ile metin okuma
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return ""

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    try:
        text = pytesseract.image_to_string(thresh, lang="eng")
    except Exception:
        text = pytesseract.image_to_string(thresh)

    text = text.strip()
    return text


def analyze_ingredients(raw_text: str):
    """
    Tüm 'İçindekiler' metnini analiz eder:
    - Metni parçalara ayırır
    - Her parçayı sözlükle eşleştirir
    - Gerekirse ML ile risk tahmini yapar
    - Genel risk seviyesini hesaplar
    """
    tokens = split_ingredients_list(raw_text)
    results = [match_single_ingredient(t) for t in tokens]

    risk_map = {
        "dusuk": 1, "düşük": 1,
        "orta": 2,
        "yuksek": 3, "yüksek": 3,
    }

    scores = []
    for r in results:
        if r.get("matched"):
            rv = r["risk"].lower()
            if rv in risk_map:
                scores.append(risk_map[rv])
        elif r.get("predicted_risk"):
            rv = r["predicted_risk"].lower()
            if rv in risk_map:
                scores.append(risk_map[rv])

    if scores:
        avg = sum(scores) / len(scores)
        if avg < 1.5:
            overall = "düşük"
        elif avg < 2.5:
            overall = "orta"
        else:
            overall = "yüksek"
    else:
        overall = "bilinmiyor"

    summary_sentences = []
    for r in results:
        if not r.get("matched"):
            if r.get("predicted_risk"):
                summary_sentences.append(
                    f"{r['ingredient']}: Sözlükte yok, ML tahmini riski {r['predicted_risk']}."
                )
            else:
                summary_sentences.append(f"{r['ingredient']}: Bu madde sözlükte bulunamadı.")
        else:
            ing = r["ingredient"]
            name = r["common_name"]
            category = r["category"]
            risk = r["risk"]
            desc = r["description"]
            summary_sentences.append(
                f"{ing} ({name}): {risk} riskli bir {category}dır/dir. {desc}"
            )

    summary_text = "\n".join(summary_sentences)

    return {
        "raw_text": raw_text,
        "summary_text": summary_text,
        "items": results,
        "overall_risk_level": overall,
    }
