import os
import io
import base64
import requests
import pandas as pd
import streamlit as st
from datetime import datetime
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
from folium.plugins import MiniMap, Fullscreen, MeasureControl, MousePosition


# --------- App Config ---------
st.set_page_config(
    page_title="Climate Policy Maker",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🌿 AI Climate Policy Maker")

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")  # FastAPI base


# --------- Helpers ---------
@st.cache_data(ttl=300)
def fetch_policy(city: str, model: str, temperature: float, user_prompt: str) -> dict:
    params = {"city": city, "model": model, "temperature": temperature, "user_prompt": user_prompt}
    r = requests.get(f"{API_URL}/policy", params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def to_daily_dataframe(openmeteo_json: dict) -> pd.DataFrame:
    if not openmeteo_json or "daily" not in openmeteo_json:
        return pd.DataFrame()

    daily = openmeteo_json.get("daily", {})
    units = openmeteo_json.get("daily_units", {})
    df = pd.DataFrame(daily)

    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"])
        df.rename(columns={"time": "date"}, inplace=True)

    rename_map = {}
    for col in ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"]:
        if col in df.columns:
            u = units.get(col, "")
            rename_map[col] = f"{col} ({u})" if u else col
    df.rename(columns=rename_map, inplace=True)

    return df


def render_pdf(policy_text: str, city: str, weather_summary: str) -> bytes:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, PageBreak, ListFlowable, ListItem
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    except Exception:
        st.warning("Install 'reportlab' for PDF export: pip install reportlab")
        return b""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleMain", fontSize=20, leading=26, alignment=TA_CENTER, textColor=colors.HexColor("#2E7D32"), spaceAfter=20))
    styles.add(ParagraphStyle(name="Subtle", fontSize=10, textColor=colors.grey, spaceAfter=10, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="Heading", fontSize=14, leading=18, textColor=colors.HexColor("#1B5E20"), spaceAfter=8))
    styles.add(ParagraphStyle(name="Body", fontSize=11, leading=16, alignment=TA_JUSTIFY))

    story = []
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph(f"🌍 Climate Policy Report", styles["TitleMain"]))
    story.append(Paragraph(f"City: <b>{city}</b>", styles["Subtle"]))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Subtle"]))
    story.append(PageBreak())

    story.append(Paragraph("📊 Weather Summary", styles["Heading"]))
    story.append(Spacer(1, 0.3*cm))
    for line in weather_summary.split("\n"):
        story.append(Paragraph(line, styles["Body"]))
    story.append(Spacer(1, 1*cm))

    story.append(Paragraph("🌱 Policy Recommendations", styles["Heading"]))
    story.append(Spacer(1, 0.3*cm))

    bullets = []
    for line in policy_text.split("\n"):
        if line.strip().startswith("-") or line.strip().startswith("*"):
            bullets.append(ListItem(Paragraph(line.strip("-* ").strip(), styles["Body"])))
        elif line.strip():
            story.append(Paragraph(line.strip(), styles["Body"]))
            story.append(Spacer(1, 0.2*cm))

    if bullets:
        story.append(ListFlowable(bullets, bulletType="bullet", leftIndent=15))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(A4[0]/2, 1*cm, "AI Climate Policy Maker — Generated Report")
        canvas.restoreState()

    doc.build(story, onLaterPages=footer, onFirstPage=footer)
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
    city = st.text_input("City", value="Lahore")
    user_prompt = st.text_area("Custom Prompt", value="Suggest climate-friendly policy for this city.")
    model = st.selectbox("LLM Model", ["gpt-4o-mini", "gpt-5-nano"])
    temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.4, 0.1)
    run = st.button("Generate / Refresh")

# Geocode city for map centering
lat, lon = 31.5497, 74.3436  # default Lahore
if city:
    try:
        geolocator = Nominatim(user_agent="climate-map-app")
        loc = geolocator.geocode(city, timeout=10)
        if loc:
            lat, lon = loc.latitude, loc.longitude
    except Exception:
        pass


# --------- Tabs ---------
tab_policy, tab_raw, tab_viz, tab_export = st.tabs(
    ["🌱 AI Policy", "🧾 Raw Data", "📈 Visualizations", "📄 Export"]
)

if "last_response" not in st.session_state:
    st.session_state["last_response"] = None
if "last_pdf" not in st.session_state:
    st.session_state["last_pdf"] = b""


# --------- Fetch Data ---------
if run:
    with st.spinner("Fetching weather & generating policy…"):
        try:
            data = fetch_policy(city, model, temperature, user_prompt)
            st.session_state["last_response"] = data
            st.success("Done!")
        except Exception as e:
            st.error(f"Failed: {e}")

data = st.session_state["last_response"]


# --------- AI Policy Tab ---------
with tab_policy:
    st.subheader("AI-Generated Climate Policy")
    if not data:
        st.info("Use the sidebar to generate a policy.")
    else:
        st.write(data.get("policy", "No policy returned."))
        cols = st.columns(3)
        cols[0].metric("City", data.get("city", city))
        cols[1].metric("Model", model)
        cols[2].metric("Generated", datetime.now().strftime("%H:%M:%S"))


# --------- Raw Data Tab ---------
with tab_raw:
    st.subheader("Raw API Payloads")
    if not data:
        st.info("Generate first.")
    else:
        st.json(data)


# --------- Visualizations Tab ---------
with tab_viz:
    st.subheader("Forecast (Next 7 Days)")
    if not data:
        st.info("Generate first.")
    else:
        openmeteo = data.get("weather", {}).get("OpenMeteo", {})
        df = to_daily_dataframe(openmeteo)
        if df.empty:
            st.warning("No data for charting.")
        else:
            import matplotlib.pyplot as plt
            st.dataframe(df, use_container_width=True)

            if any("temperature_2m_max" in c for c in df.columns):
                col = [c for c in df.columns if "temperature_2m_max" in c][0]
                fig, ax = plt.subplots()
                ax.plot(df["date"], df[col], marker="o")
                ax.set_title("Daily Max Temperature")
                plt.xticks(rotation=45)
                st.pyplot(fig)

            if any("temperature_2m_min" in c for c in df.columns):
                col = [c for c in df.columns if "temperature_2m_min" in c][0]
                fig, ax = plt.subplots()
                ax.plot(df["date"], df[col], marker="o")
                ax.set_title("Daily Min Temperature")
                plt.xticks(rotation=45)
                st.pyplot(fig)

            if any("precipitation_sum" in c for c in df.columns):
                col = [c for c in df.columns if "precipitation_sum" in c][0]
                fig, ax = plt.subplots()
                ax.bar(df["date"].dt.strftime("%Y-%m-%d"), df[col])
                ax.set_title("Daily Precipitation")
                plt.xticks(rotation=45)
                st.pyplot(fig)

    # --------- Interactive Map ---------
    st.subheader("🌍 Climate Map")

    BASEMAPS = {
        "OpenStreetMap": folium.TileLayer("OpenStreetMap", name="OpenStreetMap", control=False),
        "CartoDB Positron": folium.TileLayer(
            tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
            attr="© OpenStreetMap contributors © CARTO",
            name="CartoDB Positron",
            control=False,
        ),
        "CartoDB DarkMatter": folium.TileLayer(
            tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
            attr="© OpenStreetMap contributors © CARTO",
            name="CartoDB DarkMatter",
            control=False,
        ),
        "OpenTopoMap": folium.TileLayer(
            tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
            attr="Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)",
            name="OpenTopoMap",
            control=False,
        ),
    }

    HAZARD_TILES = {
        "Drought Risk": "https://tiles.developmentseed.org/worldbank/climate/drought/{z}/{x}/{y}.png",
        "Flood Risk":   "https://tiles.developmentseed.org/worldbank/climate/flood/{z}/{x}/{y}.png",
        "Heat Stress":  "https://tiles.developmentseed.org/worldbank/climate/heat/{z}/{x}/{y}.png",
    }

    base_map = st.selectbox("Base map", list(BASEMAPS.keys()), index=0)
    hazard = st.selectbox("Climate hazard overlay", ["(None)"] + list(HAZARD_TILES.keys()), index=0)
    opacity = st.slider("Overlay opacity", 0.0, 1.0, 0.6, 0.05)

    m = folium.Map(location=[lat, lon], zoom_start=6, control_scale=True)
    BASEMAPS[base_map].add_to(m)

    if hazard != "(None)":
        folium.TileLayer(
            tiles=HAZARD_TILES[hazard],
            name=hazard,
            attr="World Bank Climate (Development Seed tiles)",
            overlay=True,
            control=True,
            opacity=opacity,
        ).add_to(m)

    folium.Marker([lat, lon], tooltip=f"{city} ({lat:.4f}, {lon:.4f})").add_to(m)
    MiniMap(toggle_display=True).add_to(m)
    Fullscreen().add_to(m)
    m.add_child(MeasureControl(position="topleft", primary_length_unit='kilometers'))
    MousePosition(position='bottomright', prefix="Lat/Lon:")

    folium.LayerControl(collapsed=True).add_to(m)

    map_state = st_folium(m, width=None, height=600, returned_objects=["last_object_clicked", "center", "zoom"])

    if map_state and map_state.get("last_object_clicked"):
        click = map_state["last_object_clicked"]
        st.info(f"🖱️ Last clicked at: lat={click['lat']:.6f}, lon={click['lng']:.6f}")


# --------- Export Tab ---------
with tab_export:
    st.subheader("Export / Share")
    if not data:
        st.info("Generate first.")
    else:
        policy_text = data.get("policy", "")
        city_used = data.get("city", city)
        df = to_daily_dataframe(data.get("weather", {}).get("OpenMeteo", {}))

        if not df.empty:
            summary_lines = []
            for _, row in df.head(3).iterrows():
                line = f"{row['date'].date()}:"
                if "temperature_2m_max" in row: line += f" Max {row['temperature_2m_max (°C)']}"
                if "temperature_2m_min" in row: line += f", Min {row['temperature_2m_min (°C)']}"
                if "precipitation_sum" in row: line += f", Precip {row['precipitation_sum (mm)']}"
                summary_lines.append(line)
            weather_summary = "\n".join(summary_lines)
        else:
            weather_summary = "No forecast available."

        pdf_bytes = render_pdf(policy_text, city_used, weather_summary)
        st.session_state["last_pdf"] = pdf_bytes

        c1, c2 = st.columns([2, 1])
        with c1:
            st.write("**Preview**")
            show_pdf_inline(pdf_bytes)
        with c2:
            st.download_button(
                label="Download Policy PDF",
                data=pdf_bytes,
                file_name=f"policy_{city_used}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )