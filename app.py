import os
import io
import base64
import time
import requests
import pandas as pd
import streamlit as st
from datetime import datetime
from typing import Dict, Any, List

# --------- App Config ---------
st.set_page_config(
    page_title="Climate Policy Maker",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")  # FastAPI base

# --------- Helpers ---------
@st.cache_data(ttl=300)
def fetch_policy(city: str, model: str, temperature: float) -> Dict[str, Any]:
    """
    Calls FastAPI /policy endpoint. You can extend your backend to accept model/temperature.
    For now this client passes them as query params (safe to ignore server-side if unused).
    """
    params = {"city": city, "model": model, "temperature": temperature}
    r = requests.get(f"{API_URL}/policy", params=params, timeout=60)
    r.raise_for_status()
    return r.json()

def to_daily_dataframe(openmeteo_json: Dict[str, Any]) -> pd.DataFrame:
    if not openmeteo_json or "daily" not in openmeteo_json:
        return pd.DataFrame()

    daily = openmeteo_json.get("daily", {})
    units = openmeteo_json.get("daily_units", {})
    df = pd.DataFrame(daily)

    # Normalize date + units in column names
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"])
        df.rename(columns={"time": "date"}, inplace=True)

    # Optional: attach units to column names
    rename_map = {}
    for col in ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"]:
        if col in df.columns:
            u = units.get(col, "")
            rename_map[col] = f"{col} ({u})" if u else col
    df.rename(columns=rename_map, inplace=True)

    return df

def render_pdf(policy_text: str, city: str, weather_summary: str) -> bytes:
    """
    Create a simple PDF in-memory using reportlab.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
    except Exception:
        st.warning("Installing 'reportlab' enables PDF export: pip install reportlab")
        return b""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleBold", fontSize=16, leading=20, spaceAfter=12, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name="Subtle", fontSize=10, textColor=colors.grey, spaceAfter=10))
    styles.add(ParagraphStyle(name="Body", fontSize=11, leading=16))

    story = []
    title = f"Climate Policy Recommendations for {city}"
    story.append(Paragraph(title, styles["TitleBold"]))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Subtle"]))
    story.append(Paragraph("<b>Weather Summary:</b>", styles["Body"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(weather_summary.replace("\n", "<br/>"), styles["Body"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Policy Recommendations:</b>", styles["Body"]))
    story.append(Spacer(1, 6))
    # Basic sanitization for Paragraph
    safe_policy = policy_text.replace("\n", "<br/>")
    story.append(Paragraph(safe_policy, styles["Body"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()

def show_pdf_inline(pdf_bytes: bytes, height: int = 600):
    if not pdf_bytes:
        st.info("PDF not available.")
        return
    b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    pdf_html = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="{height}" type="application/pdf"></iframe>'
    st.markdown(pdf_html, unsafe_allow_html=True)

# --------- Sidebar Controls ---------
with st.sidebar:
    st.header("⚙️ Controls")
    city = st.text_input("City", value="London")
    model = st.selectbox("LLM Model", ["gpt-4o-mini", "gpt-5-nano"])
    temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.4, 0.1)
    st.caption("Tip: lower temperature = more deterministic policy outputs.")
    run = st.button("Generate / Refresh")

# --------- Header ---------
st.title("🌍 Climate Policy Maker — Dashboard")

# --------- Tabs ---------
tab_policy, tab_raw, tab_viz, tab_export = st.tabs(
    ["🌱 AI Policy", "🧾 Raw Data", "📈 Visualizations", "📄 Export"]
)

# Initialize state
if "last_response" not in st.session_state:
    st.session_state["last_response"] = None
if "last_pdf" not in st.session_state:
    st.session_state["last_pdf"] = b""

# --------- Fetch Data ---------
if run:
    with st.spinner("Fetching weather & generating policy…"):
        try:
            data = fetch_policy(city, model, temperature)
            st.session_state["last_response"] = data
            st.success("Done!")
        except Exception as e:
            st.error(f"Failed: {e}")

data = st.session_state["last_response"]

# --------- AI Policy Tab ---------
with tab_policy:
    st.subheader("AI-Generated Climate Policy")
    if not data:
        st.info("Use the controls in the sidebar to generate a policy.")
    else:
        policy_text = data.get("policy", "No policy text returned.")
        st.write(policy_text)

        # Quick badges/metrics row
        cols = st.columns(3)
        cols[0].metric("City", data.get("city", city))
        # You can make your FastAPI return model & latency for nicer UX
        cols[1].metric("Model", model)
        cols[2].metric("Generated", datetime.now().strftime("%H:%M:%S"))

# --------- Raw Data Tab ---------
with tab_raw:
    st.subheader("Raw API Payloads")
    if not data:
        st.info("Generate first to see raw payloads.")
    else:
        st.write("**Backend Response**")
        st.json(data)
        st.divider()
        st.write("**Open-Meteo Extract**")
        st.json(data.get("weather", {}).get("OpenMeteo", {}))
        st.write("**WeatherAPI Extract**")
        st.json(data.get("weather", {}).get("WeatherAPI", {}))

# --------- Visualizations Tab ---------
with tab_viz:
    st.subheader("Daily Weather (Open-Meteo)")
    if not data:
        st.info("Generate first to see visualizations.")
    else:
        openmeteo = data.get("weather", {}).get("OpenMeteo", {})
        df = to_daily_dataframe(openmeteo)
        if df.empty:
            st.warning("No daily data found for charting.")
        else:
            st.dataframe(df, use_container_width=True)
            st.caption("Daily forecast table (from Open-Meteo).")

            # Charts — use matplotlib for Streamlit consistency
            import matplotlib.pyplot as plt

            # Max temperature
            if any("temperature_2m_max" in c for c in df.columns):
                colname = [c for c in df.columns if "temperature_2m_max" in c][0]
                fig1, ax1 = plt.subplots()
                ax1.plot(df["date"], df[colname], marker="o")
                ax1.set_title("Daily Max Temperature")
                ax1.set_xlabel("Date")
                ax1.set_ylabel(colname)
                plt.xticks(rotation=45)
                st.pyplot(fig1)

            # Min temperature
            if any("temperature_2m_min" in c for c in df.columns):
                colname = [c for c in df.columns if "temperature_2m_min" in c][0]
                fig2, ax2 = plt.subplots()
                ax2.plot(df["date"], df[colname], marker="o")
                ax2.set_title("Daily Min Temperature")
                ax2.set_xlabel("Date")
                ax2.set_ylabel(colname)
                plt.xticks(rotation=45)
                st.pyplot(fig2)

            # Precipitation
            if any("precipitation_sum" in c for c in df.columns):
                colname = [c for c in df.columns if "precipitation_sum" in c][0]
                fig3, ax3 = plt.subplots()
                ax3.bar(df["date"].dt.strftime("%Y-%m-%d"), df[colname])
                ax3.set_title("Daily Precipitation")
                ax3.set_xlabel("Date")
                ax3.set_ylabel(colname)
                plt.xticks(rotation=45)
                st.pyplot(fig3)

# --------- Export Tab ---------
with tab_export:
    st.subheader("Export / Share")
    if not data:
        st.info("Generate a policy to export.")
    else:
        policy_text = data.get("policy", "")
        city_used = data.get("city", city)

        # Create a compact weather summary string
        openmeteo = data.get("weather", {}).get("OpenMeteo", {})
        df = to_daily_dataframe(openmeteo)
        if not df.empty:
            summary_lines = []
            # show first 3 days for brevity
            for _, row in df.head(3).iterrows():
                tmax = [c for c in df.columns if "temperature_2m_max" in c]
                tmin = [c for c in df.columns if "temperature_2m_min" in c]
                prcp = [c for c in df.columns if "precipitation_sum" in c]
                line = f"{row['date'].date()}:"
                if tmax: line += f" Max {row[tmax[0]]}"
                if tmin: line += f", Min {row[tmin[0]]}"
                if prcp: line += f", Precip {row[prcp[0]]}"
                summary_lines.append(line)
            weather_summary = "\n".join(summary_lines)
        else:
            weather_summary = "No daily forecast available."

        pdf_bytes = render_pdf(policy_text, city_used, weather_summary)
        st.session_state["last_pdf"] = pdf_bytes

        c1, c2 = st.columns([2, 1])
        with c1:
            st.write("**Preview**")
            show_pdf_inline(pdf_bytes)
        with c2:
            st.write("**Download**")
            st.download_button(
                label="Download Policy PDF",
                data=pdf_bytes,
                file_name=f"policy_{city_used}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            st.caption("Need a Word/Docx export too? I can add that.")
