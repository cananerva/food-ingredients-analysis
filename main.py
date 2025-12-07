from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .utils import analyze_ingredients, image_bytes_to_text


app = FastAPI(
    title="Food Ingredients Analyzer API",
    description="Metin veya resimden içindekiler analizi yapan sistem",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    ingredients: str


@app.get("/")
def root():
    return {"message": "Food Ingredients Analysis API is running!"}


@app.post("/analyze")
def analyze_text(req: AnalyzeRequest):
    """
    Kullanıcının metin olarak girdiği içindekiler bilgisini analiz eder.
    """
    return analyze_ingredients(req.ingredients)


@app.post("/analyze_image")
async def analyze_image(file: UploadFile = File(...)):
    """
    İçindekiler fotoğrafını alır:
    - OCR ile metne dönüştürür
    - Aynı analyze_ingredients fonksiyonunu çalıştırır
    """

    content = await file.read()

    extracted_text = image_bytes_to_text(content)

    analysis = analyze_ingredients(extracted_text)

    return {
        "extracted_text": extracted_text,
        "analysis": analysis
    }
