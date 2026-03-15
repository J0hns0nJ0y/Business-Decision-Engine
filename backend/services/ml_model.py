from sklearn.linear_model import LinearRegression
import numpy as np

def train_model(df):
    # Features (X) and Target (y)
    X = df[["marketing_spend"]]
    y = df["revenue"]

    model = LinearRegression()
    model.fit(X, y)

    return model


def predict_revenue(model, spend_values):
    spend_array = np.array(spend_values).reshape(-1, 1)
    predictions = model.predict(spend_array)

    return predictions.tolist()

def get_model_insights(model):
    return {
        "impact_factor": model.coef_[0],
        "base_revenue": model.intercept_
    }

def channel_analysis(df):
    df["ROI"] = df["revenue"] / df["marketing_spend"]
    df["ROI"].replace([float("inf"), -float("inf")], 0, inplace=True)
    channel_data = df.groupby("channel").agg({
        "marketing_spend": "sum",
        "revenue": "sum",
        "ROI": "mean"
    }).reset_index()

    return channel_data

def recommend_budget(df, total_budget=10000):
    channel_data = channel_analysis(df)

    # Normalize ROI to allocate budget proportionally
    total_roi = channel_data["ROI"].sum()

    if total_roi == 0:
        channel_data["recommended_budget"] = total_budget / len(channel_data)
    else:
        channel_data["recommended_budget"] = (
            channel_data["ROI"] / total_roi
        ) * total_budget

    return channel_data[["channel", "ROI", "recommended_budget"]]

def generate_decision(df):
    channel_data = channel_analysis(df)

    best_channel = channel_data.loc[channel_data["ROI"].idxmax(), "channel"]
    worst_channel = channel_data.loc[channel_data["ROI"].idxmin(), "channel"]

    decision = {
        "best_channel_to_invest": best_channel,
        "channel_to_reduce_spend": worst_channel
    }

    return decision

def optimize_budget(df, total_budget=10000):
    df["ROI"] = df["revenue"] / df["marketing_spend"]
    df["ROI"].replace([np.inf, -np.inf], 0, inplace=True)

    channel_data = df.groupby("channel").agg({
        "ROI": "mean"
    }).reset_index()

    # Normalize ROI
    roi_values = channel_data["ROI"].values

    if roi_values.sum() == 0:
        weights = np.ones(len(roi_values)) / len(roi_values)
    else:
        weights = roi_values / roi_values.sum()

    # Diversification factor to prevent over-concentration
    diversification_factor = 0.7

    equal_weight = np.ones(len(weights)) / len(weights)

    final_weights = (
        diversification_factor * weights +
        (1 - diversification_factor) * equal_weight
    )

    # Allocate budget
    channel_data["optimized_budget"] = final_weights * total_budget

    return channel_data

def risk_analysis(df):
    channel_risk = df.groupby("channel")["revenue"].std().reset_index()
    channel_risk.columns = ["channel", "risk"]

    return channel_risk

def advanced_decision(df, total_budget=10000):
    budget_plan = optimize_budget(df, total_budget)
    risk = risk_analysis(df)

    final = budget_plan.merge(risk, on="channel")

    return final