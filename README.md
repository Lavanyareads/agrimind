# 🐄 AgriMind — AI-Powered Livestock Feed Optimizer

## Setup (3 steps)

### 1. Folder Structure
Make sure your project looks like this:
```
agrimind/
├── app.py
├── requirements.txt
└── data/
    ├── india_livestock_feeding_dataset.xlsx
    └── cow_growth_metrics.csv
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

The app will open at http://localhost:8501

---

## Features
- **📊 Dashboard** — Feed & milk trends by breed, state, and temperature
- **🤖 Feed Predictor** — AI predicts daily feed quantity for any animal
- **🚨 Health Monitor** — Anomaly detection + Health Score Index (HSI)
- **📈 Growth Analysis** — Cow growth metrics by feed type and sunlight
