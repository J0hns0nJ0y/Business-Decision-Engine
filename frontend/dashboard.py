import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
import io

#------------------PDF REPORT GENERATION------------------#
def generate_pdf_report(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4
    )
    styles = getSampleStyleSheet()
    elements = []
    # -----------------------------
    # Title
    # -----------------------------
    elements.append(Paragraph("Business Decision Engine Report", styles['Title']))
    elements.append(Spacer(1,20))
    # -----------------------------
    # KPI Metrics
    # -----------------------------
    elements.append(Paragraph("Key Metrics", styles['Heading2']))
    metrics_table = [
        ["Metric", "Value"],
        ["Average ROI", str(data.get("average_roi"))],
        ["Average Growth", str(data.get("average_growth"))],
        ["Rows Processed", str(data.get("rows_after_cleaning"))]
    ]
    elements.append(Table(metrics_table))
    elements.append(Spacer(1,20))
    # -----------------------------
    # Insights
    # -----------------------------
    elements.append(Paragraph("Insights", styles['Heading2']))
    insights = data.get("insights", [])
    for insight in insights:
        elements.append(Paragraph(f"- {insight}", styles['Normal']))

    elements.append(Spacer(1,20))
    # -----------------------------
    # AI Recommendations
    # -----------------------------
    elements.append(Paragraph("AI Recommendations", styles['Heading2']))
    recommendations = data.get("ai_recommendations", [])
    for rec in recommendations:
        elements.append(Paragraph(f"- {rec}", styles['Normal']))
    elements.append(Spacer(1,20))
    # -----------------------------
    # Decision Engine Output
    # -----------------------------
    elements.append(Paragraph("Decision Engine Output", styles['Heading2']))
    decision_data = data.get("decision_engine", {}).get("decision", {})
    if isinstance(decision_data, dict):
        for key, value in decision_data.items():
            elements.append(Paragraph(f"{key}: {value}", styles['Normal']))
    else:
        elements.append(Paragraph(str(decision_data), styles['Normal']))
    elements.append(Spacer(1,20))
    # -----------------------------
    # Budget Allocation
    # -----------------------------
    elements.append(Paragraph("Recommended Budget Allocation", styles['Heading2']))
    budget_data = data.get("decision_engine", {}).get("budget_allocation", [])
    if budget_data:
        table_data = [["Channel", "Recommended Budget"]]
        for row in budget_data:
            table_data.append([
                str(row.get("channel")),
                str(row.get("recommended_budget"))
            ])
        elements.append(Table(table_data))
    elements.append(Spacer(1,20))
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

#------------------STREAMLIT DASHBOARD------------------#
st.set_page_config(
    page_title="Business Decision Engine",
    page_icon="📊",
    layout="wide"
)
st.set_page_config(page_title="Business Decision Engine", layout="wide")
st.title("📊 Marketing Decision Intelligence Dashboard")
st.write("𝐃𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐝 𝐛𝐲 𝐉0𝐡𝐧𝐬0𝐧𝐉0𝐲 𝐰𝐢𝐭𝐡 ❤️ | 𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐛𝐲 𝐅𝐚𝐬𝐭𝐀𝐏𝐈 & 𝐒𝐭𝐫𝐞𝐚𝐦𝐥𝐢𝐭")
st.write("Upload marketing data to generate insights.")
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:

    files = {"file": uploaded_file.getvalue()}
    response = requests.post(
        "http://127.0.0.1:8000/upload",   # your backend endpoint
        files=files
    )
    data = response.json()

    # 🔹 Handle backend errors
    if "error" in data:
        st.error(data["error"])
        st.stop()

    # 🔹 Success message
    if "message" in data:
        st.success(data["message"])

    # 🔹 Dataset preview
    st.subheader("Dataset Preview")
    df = pd.DataFrame(data["preview"])
    st.dataframe(df)

    # 🔹 Metrics
    st.subheader("Key Metrics")
    col1, col2 = st.columns(2)
    col1.metric("Average ROI", round(data["average_roi"],2))
    col2.metric("Average Growth", round(data["average_growth"],2))

    #KPI CARDS
    st.subheader("Key Performance Indicators")
    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Average ROI",
        round(data["average_roi"], 2)
    )
    col2.metric(
        "Average Growth",
        str(round(data["average_growth"] * 100, 2)) + "%"
    )
    col3.metric(
        "Rows Processed",
        data["rows_after_cleaning"]
    )

    # 🔹 Charts
    st.subheader("Marketing Spend vs Revenue")

    if "channel" in df.columns:
        chart_df = df.groupby("channel")[["marketing_spend","revenue"]].sum()
        st.bar_chart(chart_df)
    
    #ROI CHART
    st.subheader("ROI by Channel")
    roi_df = df.groupby("channel").apply(
        lambda x: x["revenue"].sum() / x["marketing_spend"].sum()
    ).reset_index(name="ROI")
    st.bar_chart(roi_df.set_index("channel"))
    
    #channel performance table
    st.subheader("Channel Performance")
    channel_perf = df.groupby("channel").agg({
        "marketing_spend": "sum",
        "revenue": "sum"
    })
    channel_perf["ROI"] = channel_perf["revenue"] / channel_perf["marketing_spend"]
    st.dataframe(channel_perf)

    #Trend Chart
    st.subheader("Marketing Performance Trend")
    trend_df = df.sort_values("date")
    trend_df = trend_df.set_index("channel")[["marketing_spend","revenue"]]
    st.line_chart(trend_df)

    #ML REVENUE CHART
    st.subheader("ML Revenue Prediction")
    if "predictions" in data:
        pred_df = pd.DataFrame({
            "Spend": data["predictions"]["spend"],
            "Predicted Revenue": data["predictions"]["predicted_revenue"]
        })
        pred_df["Upper Bound"] = pred_df["Predicted Revenue"] * 1.1
        pred_df["Lower Bound"] = pred_df["Predicted Revenue"] * 0.9
        pred_df = pred_df.set_index("Spend")
        st.line_chart(pred_df)
    
    # 💰 Budget Allocation Section
    st.subheader("Recommended Budget Allocation")
    budget_df = pd.DataFrame(data["decision_engine"]["budget_allocation"])
    st.dataframe(budget_df)
    # initialize toggle state
    if "show_pie" not in st.session_state:
        st.session_state.show_pie = False
    # toggle button
    if st.button("📊 Toggle Budget Chart"):
        st.session_state.show_pie = not st.session_state.show_pie
    # show chart only if toggled on
    if st.session_state.show_pie:
        fig, ax = plt.subplots(figsize=(8,8), facecolor="#0E1117")
        budget_df.set_index("channel")["recommended_budget"].plot.pie(
            autopct="%1.1f%%",
            ax=ax,
            textprops={"color": "white", "fontsize": 11}
        )
        ax.set_ylabel("")
        ax.set_facecolor("#0E1117")
        st.pyplot(fig)
        
    #Decision Engine Panel
    st.subheader("Decision Engine Recommendation")
    decision = data["decision_engine"]["decision"]
    if isinstance(decision, dict):
        for key, value in decision.items():
            st.markdown(f"**{key.replace('_',' ').title()}**: {value}")
    else:
        st.success(decision)

    # 🔹 AI recommendations
    st.subheader("AI Recommendations")
    for r in data["ai_recommendations"]:
        st.write("✅", r)

    #Report Download Button
    st.subheader("Export Report")
    pdf_file = generate_pdf_report(data)
    st.download_button(
        label="Download Analytics Report",
        data=pdf_file,
        file_name="business_decision_report.pdf",
        mime="application/pdf"
    )