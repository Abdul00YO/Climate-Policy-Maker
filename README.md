# 🌍 Climate Policy Maker
An AI-powered app that helps generate **climate-friendly policy suggestions** based on real-time weather data. Built with **FastAPI (backend)** + **Streamlit (frontend)**.

---

## 🚀 Features
- 🌦 **Live Weather Data**: Fetches real-time weather info using APIs.  
- 🤖 **AI Policy Generator**: Suggests climate-smart policies tailored to the city’s weather.  
- 📊 **Visualizations**: Explore insights with charts and analytics.  
- 📄 **Download Reports**: Export AI policies as a PDF.  
- 🧩 **Tabbed Interface**: Easy navigation between raw data, AI policies, downloads, and visuals.  

---

## 🛠 Tech Stack
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)  
- **Frontend**: [Streamlit](https://streamlit.io/)  
- **Weather API**: [Open-Meteo](https://open-meteo.com/) (or any weather data provider)  
- **PDF Export**: ReportLab  
- **Visualization**: Matplotlib / Plotly  

---

## 📂 Project Structure
Climate-Policy-Maker/  
│── app.py              # FastAPI backend  
│── frontend.py         # Streamlit frontend  
│── requirements.txt    # Dependencies  
│── .gitignore  
│── README.md  
└── myenv/              # Virtual environment (ignored)  
---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
$ git clone https://github.com/Abdul00YO/Climate-Policy-Maker.git  
$ cd Climate-Policy-Maker  

### 2️⃣ Create & Activate Virtual Environment
- **Windows (PowerShell)**
  $ python -m venv myenv  
  $ myenv\Scripts\activate  

- **Mac/Linux**
  $ python3 -m venv myenv  
  $ source myenv/bin/activate  

### 3️⃣ Install Dependencies
$ pip install -r requirements.txt  

---

## ▶️ Running the Application

### Start Backend (FastAPI)
$ uvicorn app:app --reload  
👉 Runs at: http://127.0.0.1:8000  

### Start Frontend (Streamlit)
$ streamlit run frontend.py  
👉 Runs at: http://localhost:8501  

---

## 📊 Example Workflow
1. Enter your **city name**.  
2. View **real-time weather data**.  
3. Get **AI-generated climate policy**.  
4. Explore **visualizations**.  
5. **Download policy as PDF**.  

---

## 📌 Future Improvements
- 🌐 Multi-language support  
- 🗺️ Regional climate recommendations  
- 🧠 Smarter AI models  

---

## 📝 License
This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.  
