from fastapi import FastAPI, UploadFile, File
from services.analytics import calculate_total_metrics, calculate_roi, calculate_growth
from services.analytics import generate_insights
from services.ml_model import train_model, predict_revenue, get_model_insights
from services.ml_model import recommend_budget, generate_decision, advanced_decision
from services.recommendation_engine import generate_recommendations
import pandas as pd
import numpy as np

app = FastAPI()

REQUIRED_COLUMNS = ["date", "marketing_spend", "revenue", "channel"]


@app.get("/")
def home():
    return {"message": "Business Decision Engine is running 🚀"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)

        # 🔹 1. Check empty
        if df.empty:
            return {"error": "Uploaded file is empty"}

        # 🔹 2. Validate columns
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            return {"error": f"Missing columns: {missing_cols}"}

        # 🔹 3. Convert date
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # 🔹 4. Convert numeric columns
        df["marketing_spend"] = pd.to_numeric(df["marketing_spend"], errors="coerce")
        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")

        # 🔹 5. Remove invalid rows
        df = df.dropna()

        # 🔹 6. Remove invalid values
        df = df[df["marketing_spend"] > 0]
        df = df[df["revenue"] >= 0]

        # 🔹 7. Remove duplicates
        df = df.drop_duplicates()

        # 🔹 8. Final sanity check
        if df.empty:
            return {"error": "No valid data left after cleaning"}

        # 🔹 9. Analytics
        metrics = calculate_total_metrics(df)
        roi = calculate_roi(df)
        growth = calculate_growth(df)

        # 🔥 10. GLOBAL SAFETY NET (VERY IMPORTANT)
        def clean_output(data):
            if isinstance(data, dict):
                return {k: clean_output(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [clean_output(i) for i in data]
            elif isinstance(data, float):
                if np.isnan(data) or np.isinf(data):
                    return 0
            return data

        # 11. Generate insights
        insights = generate_insights(df)
        
        #12. Train ML model
        model = train_model(df)
        # Example predictions
        #future_spend = [1000, 5000, 10000]
        future_spend = list(range(1000, 20000, 3000))
        predictions = predict_revenue(model, future_spend)
        model_info = get_model_insights(model)


        budget_plan = recommend_budget(df, total_budget=10000)
        decision = generate_decision(df)
        
        advanced_plan = advanced_decision(df, total_budget=10000)

        recommendations = generate_recommendations(df, insights)

        return clean_output({
            "message": "File processed successfully ✅",
            "developed_by": "𝐉0𝐡𝐧𝐬0𝐧𝐉0𝐲 𝐰𝐢𝐭𝐡 ❤️ | 𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐛𝐲 𝐅𝐚𝐬𝐭𝐀𝐏𝐈 & 𝐒𝐭𝐫𝐞𝐚𝐦𝐥𝐢𝐭",
            "rows_after_cleaning": len(df),
            "channels_displayed": df["channel"].unique().tolist(),
            "columns": list(df.columns),
            "metrics": metrics,
            "average_roi": roi,
            "average_growth": growth,
            "insights": insights,
            "preview": df.to_dict(orient="records"), #if you want only first 5 rows ->  df.head().to_dict(orient="records")
            "model_insights": model_info,
            "predictions": {
                "spend": future_spend,
                "predicted_revenue": predictions
            },
            "decision_engine": {
                "budget_allocation": budget_plan.to_dict(orient="records"),
                "decision": decision
            },
            "advanced_decision_engine": advanced_plan.to_dict(orient="records"),
            "ai_recommendations": recommendations
        })

    except Exception as e:
        return {"error": str(e)}