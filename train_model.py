import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import joblib

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "ingredients_dict.csv"
MODEL_PATH = BASE_DIR / "risk_model.joblib"


def main():

    df = pd.read_csv(CSV_PATH)

    df["common_name"] = df["common_name"].fillna("")
    df["code"] = df["code"].fillna("")
    df["category"] = df["category"].fillna("")
    df["risk"] = df["risk"].fillna("orta")

    df["text"] = df["common_name"] + " " + df["code"] + " " + df["category"]

    X = df["text"]
    y = df["risk"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("clf", LogisticRegression(max_iter=1000))
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print("=== Classification report (validation) ===")
    print(classification_report(y_test, y_pred))

    pipeline.fit(X, y)

    joblib.dump(pipeline, MODEL_PATH)
    print(f"Model kaydedildi: {MODEL_PATH}")


if __name__ == "__main__":
    main()
