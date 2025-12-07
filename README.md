# Food Ingredients Analysis App
A full-stack application that analyzes packaged food ingredients through text or image input. The system uses FastAPI for backend processing, OCR for extracting text from images, and a Machine Learning model to estimate ingredient risk levels.

## Overview
This project allows users to submit food ingredient information by typing the ingredient list or uploading an image. The system evaluates each ingredient, assigns a risk level, and calculates an overall product risk score. Unknown ingredients are processed through a Machine Learning model for risk estimation.

## Features

### Text-Based Ingredient Analysis
Users can paste ingredient lists such as “Sugar, E322, palm oil”.  
The backend:
- Matches items with the CSV dictionary
- Assigns risk level, category, and description
- Uses ML for unknown items
- Computes an overall risk score

### Image Ingredient Extraction (OCR)
Users can upload a food label image.  
OpenCV and Tesseract extract text and the system analyzes it automatically.

### Machine Learning Integration
A TF-IDF + Logistic Regression model predicts risk for ingredients not found in the dictionary.  
Training script: backend/train_model.py  
Model file: backend/risk_model.joblib

### Frontend Interface
The frontend uses HTML, CSS, and JavaScript and provides:
- Text input
- Image upload
- Result table
- API communication with the backend

## Project Structure
food-ingredients-analysis/
│
├── backend/
│   ├── main.py
│   ├── utils.py
│   ├── train_model.py
│   ├── ingredients_dict.csv
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── models/
│   └── ingredient_risk_model.joblib
│
├── README.md
└── .gitignore


## Running Locally

### 1. Create and activate virtual environment
python3 -m venv venv  
source venv/bin/activate

### 2. Install dependencies
pip install -r backend/requirements.txt

### 3. Start the FastAPI server
uvicorn backend.main:app --reload

API runs at: http://127.0.0.1:8000

### 4. Open the frontend
Open index.html in a browser.

## API Endpoints
POST /analyze — analyzes an ingredient list  
POST /analyze_image — performs OCR and analyzes extracted text  
GET / — root endpoint

## Machine Learning
- Logistic Regression model
- TF-IDF features
- Predicts: low, medium, high risk

Retrain model:
python backend/train_model.py

## Deployment
Backend can be deployed using:
- Render
- Railway
- Fly.io
- Deta Space

Frontend can be deployed using:
- GitHub Pages
- Netlify
- Vercel

After backend deployment, update script.js:
const API_BASE = "https://your-backend-url.onrender.com";

## Purpose
This project demonstrates ingredient analysis, OCR, machine learning integration, and frontend-backend communication, and can be used as a learning project or a lightweight food analysis tool.
