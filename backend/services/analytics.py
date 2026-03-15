import pandas as pd


def calculate_total_metrics(df):
    total_spend = df["marketing_spend"].sum()
    total_revenue = df["revenue"].sum()

    return {
        "total_spend": float(total_spend),
        "total_revenue": float(total_revenue)
    }


def calculate_roi(df):
    df = df.copy()

    # Avoid division by zero
    df = df[df["marketing_spend"] > 0]

    df["roi"] = (df["revenue"] - df["marketing_spend"]) / df["marketing_spend"]

    # Remove inf / NaN
    df = df.replace([float("inf"), -float("inf")], pd.NA)
    df = df.dropna(subset=["roi"])

    if df.empty:
        return 0.0

    return float(df["roi"].mean())


def calculate_growth(df):
    df = df.copy()
    df = df.sort_values("date")

    df["prev_revenue"] = df["revenue"].shift(1)
    df["growth"] = (df["revenue"] - df["prev_revenue"]) / df["prev_revenue"]

    # Remove inf / NaN
    df = df.replace([float("inf"), -float("inf")], pd.NA)
    df = df.dropna(subset=["growth"])

    if df.empty:
        return 0.0

    return float(df["growth"].mean())

def generate_insights(df):
    insights = {}

    # 🔹 1. ROI per channel
    df["ROI"] = df["revenue"] / df["marketing_spend"]

    channel_roi = df.groupby("channel")["ROI"].mean()

    # 🔹 2. Best & worst channel
    best_channel = channel_roi.idxmax()
    worst_channel = channel_roi.idxmin()

    # 🔹 3. Total metrics
    total_revenue = df["revenue"].sum()
    total_spend = df["marketing_spend"].sum()
    overall_roi = total_revenue / total_spend if total_spend != 0 else 0

    # 🔹 4. Growth trend
    df_sorted = df.sort_values("date")
    revenue_growth = df_sorted["revenue"].pct_change().mean()

    # 🔹 5. Build insights
    insights["best_channel"] = best_channel
    insights["worst_channel"] = worst_channel
    insights["overall_roi"] = overall_roi
    insights["avg_growth"] = revenue_growth
    insights["channel_performance"] = channel_roi.to_dict()

    if total_spend > total_revenue:
        insights["warning"] = "You are spending more than you earn!"

    # 🔹 6. Business recommendations (THIS IS THE MAGIC ✨)
    if overall_roi > 1:
        insights["recommendation"] = "Scale marketing — profitable returns"
    elif overall_roi > 0.5:
        insights["recommendation"] = "Optimize campaigns for better efficiency"
    else:
        insights["recommendation"] = "Reduce spend or rethink strategy"

    return insights

