# 🌍 Climate Policy Maker

A modern, AI-powered application designed to generate **climate-friendly policy suggestions** using real-time weather data. Built with a robust **FastAPI backend** and an intuitive **Streamlit frontend**, this tool empowers policymakers, researchers, and environmental enthusiasts to create data-driven, sustainable policies.

---

## ✨ Key Features

- **🌦 Real-Time Weather Data**: Fetches live weather information using the Open-Meteo API.  
- **🤖 AI-Driven Policy Suggestions**: Generates tailored climate-smart policies based on local weather conditions.  
- **📊 Interactive Visualizations**: Explore weather trends and policy impacts with Matplotlib and Plotly charts.  
- **📄 PDF Report Generation**: Export AI-generated policies as professional PDF documents.  
- **🧩 Tabbed Interface**: Seamlessly navigate between weather data, policy suggestions, visualizations, and downloads.  

---

## 🛠 Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) – High-performance, asynchronous API framework.  
- **Frontend**: [Streamlit](https://streamlit.io/) – User-friendly interface for data-driven apps.  
- **Weather API**: [Open-Meteo](https://open-meteo.com/) – Reliable, open-source weather data provider.  
- **PDF Export**: [ReportLab](https://www.reportlab.com/) – Dynamic PDF generation.  
- **Visualization**: [Matplotlib](https://matplotlib.org/) / [Plotly](https://plotly.com/) – Rich, interactive charts.  

---

## 📂 Project Structure

```
Climate-Policy-Maker/
├── app.py              # FastAPI backend
├── frontend.py         # Streamlit frontend
├── requirements.txt    # Project dependencies
├── .gitignore          # Git ignore file
├── README.md           # Project documentation
└── myenv/              # Virtual environment (ignored)
```

---

## ⚙️ Installation & Setup

Follow these steps to set up and run the Climate Policy Maker locally.

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Abdul00YO/Climate-Policy-Maker.git
cd Climate-Policy-Maker
```

### 2️⃣ Create & Activate Virtual Environment

- **Windows (PowerShell)**
  ```bash
  python -m venv myenv
  myenv\Scripts\activate
  ```

- **MacOS/Linux**
  ```bash
  python3 -m venv myenv
  source myenv/bin/activate
  ```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

### Start the Backend (FastAPI)
```bash
uvicorn main:app --reload
```
- Access the API at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Start the Frontend (Streamlit)
```bash
streamlit run frontend.py
```
- Access the app at: [http://localhost:8501](http://localhost:8501)

---

## 📊 Example Workflow

1. **Enter a City Name**: Input your target city to fetch real-time weather data.  
2. **View Weather Data**: Explore current weather conditions and trends.  
3. **Generate Policies**: Receive AI-crafted climate policies tailored to the city's conditions.  
4. **Visualize Insights**: Analyze weather and policy data with interactive charts.  
5. **Download Reports**: Export AI-generated policies as professional PDFs.  

---

## 🚀 Future Enhancements

- **🌐 Multi-Language Support**: Expand accessibility with multilingual interfaces.  
- **🗺️ Regional Recommendations**: Provide granular, region-specific climate policies.  
- **🧠 Advanced AI Models**: Integrate cutting-edge AI for smarter, context-aware suggestions.  
- **📈 Enhanced Analytics**: Add predictive modeling for long-term climate trends.  

---

## 📝 License

This project is licensed under the [MIT License](LICENSE). See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

We welcome contributions! Please fork the repository, create a feature branch, and submit a pull request. For major changes, open an issue first to discuss your ideas.

---

## 📧 Contact

For questions, suggestions, or feedback, reach out via [GitHub Issues](https://github.com/Abdul00YO/Climate-Policy-Maker/issues) or connect with the project maintainer at [your-email@example.com](mailto:your-email@example.com).

---

🌱 **Build a greener future with Climate Policy Maker!**
