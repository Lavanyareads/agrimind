# AgriMind: AI-Powered Livestock Feed & Health Optimizer 🐄🌾

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)

AgriMind is a comprehensive, multi-tenant web application designed to help farmers optimize their livestock management. By leveraging Machine Learning, it provides precise daily feed predictions, generates species-aware feeding schedules, and monitors herd health via anomaly detection—ultimately maximizing profitability and reducing feed waste.

---

## ✨ Core Features

- **🔐 Secure Herd Management:** Multi-tenant architecture utilizing MongoDB Atlas and `bcrypt` password hashing. Farmers can securely register, log in, and manage their specific livestock profiles.
- **🧠 AI Feed Predictor:** Uses a **Gradient Boosting Regressor** to predict the exact daily feed (kg) an animal requires based on its age, weight, temperature resilience, and milk yield.
- **📅 Smart Feeding Scheduler:** Dynamically adapts to the species! Ruminants (Cows/Buffaloes) receive a 3-meal-a-day schedule with precise water recommendations, while Monogastrics (Pigs/Horses) receive an optimized 2-meal schedule.
- **🚨 Herd Health Monitor:** Utilizes an **Isolation Forest** anomaly detection algorithm to flag sick or underperforming animals. Calculates a dynamic Health Score Index (HSI) that changes its criteria based on whether the animal is dairy or non-dairy.
- **📊 Global Analytics:** Interactive, real-time Plotly dashboards visualizing growth trends, feed impact, and breed profitability across various regions.

---

## 🛠️ Technology Stack

- **Frontend:** Streamlit, Custom CSS (Glassmorphism & Inter Font)
- **Backend:** Python 3
- **Database:** MongoDB Atlas (PyMongo)
- **Machine Learning:** Scikit-Learn (`GradientBoostingRegressor`, `IsolationForest`), Pandas, NumPy
- **Visualizations:** Plotly Express
- **Security:** Bcrypt, python-dotenv

---

## 🚀 How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/YourUsername/AgriMind.git
cd AgriMind
```

### 2. Install dependencies
Ensure you have Python 3.9+ installed, then run:
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Create a `.env` file in the root directory and add your MongoDB connection string:
```env
MONGO_URI="mongodb+srv://<username>:<password>@yourcluster.mongodb.net/?appName=agrimind"
```

### 4. Run the application
```bash
streamlit run app.py
```
*The app will launch in your default web browser at `http://localhost:8501`.*

---

## 📂 Project Structure

```text
agrimind/
├── .env                              # Ignored by git, stores MONGO_URI
├── app.py                            # Application entry point and routing
├── requirements.txt                  # Python dependencies
├── components/                       # Reusable UI components (Auth forms)
├── data/                             # ML Training datasets
├── database/                         # MongoDB CRUD wrappers
├── models/                           # ML models and HSI logic
├── pages/                            # Streamlit multi-page routing
│   ├── 01_My_Herd.py
│   ├── 02_Feed_Predictor.py
│   ├── 03_Dashboard.py
│   ├── 04_Health_Monitor.py
│   └── 05_Growth_Analysis.py
└── utils/                            # Custom CSS and styling tokens
```

---
**Developed for Engineering Project Design (EEM-283-COM)**
*Team Members: Lavanya Nimbalkar, Aishwarya Pawar, Gargi Mane, Aanadi Masal, Astha Nakat*
