import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, IsolationForest
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import streamlit as st
import warnings
warnings.filterwarnings("ignore")

@st.cache_data
def load_static_data():
    """Loads the base dataset to train the global models."""
    df = pd.read_excel("data/complete_indian_livestock_dataset.xlsx")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.month_name()
    df["Feed_per_kg_body"] = df["Feed_Quantity_kg"] / df["Weight_kg"]
    df["Milk_per_kg_feed"]  = df["Milk_Yield_Liters"] / df["Feed_Quantity_kg"]
    df["HSI"] = (
        (df["Milk_Yield_Liters"] / df["Milk_Yield_Liters"].max()) * 50 +
        (df["Weight_kg"]         / df["Weight_kg"].max())          * 30 +
        ((40 - abs(df["Temperature_C"] - 25)) / 40).clip(0, 1)     * 20
    ).clip(0, 100).round(1)
    return df

@st.cache_data
def load_growth_data():
    df = pd.read_csv("data/cow_growth_metrics.csv")
    df = df.drop(columns=["Unnamed: 0"], errors="ignore")
    df.columns = ["Weight_kg", "Height_cm", "Volume_liter", "Feed_Type", "Sunlight"]
    df["Sunlight_label"] = df["Sunlight"].map({"Gt": "High Sunlight", "Lt": "Low Sunlight"})
    return df

@st.cache_resource
def get_trained_models():
    """Trains and caches the GBR and Isolation Forest models."""
    df = load_static_data()
    le_species = LabelEncoder(); le_breed = LabelEncoder(); le_state = LabelEncoder()
    
    X = df[["Weight_kg", "Age_Years", "Milk_Yield_Liters", "Temperature_C"]].copy()
    X["Species_enc"] = le_species.fit_transform(df["Species"])
    X["Breed_enc"]   = le_breed.fit_transform(df["Breed"])
    X["State_enc"]   = le_state.fit_transform(df["Location_State"])
    y = df["Feed_Quantity_kg"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    gbr = GradientBoostingRegressor(n_estimators=150, max_depth=4, random_state=42)
    gbr.fit(X_train, y_train)
    mae = mean_absolute_error(y_test, gbr.predict(X_test))
    
    iso = IsolationForest(contamination=0.1, random_state=42)
    iso.fit(df[["Weight_kg", "Milk_Yield_Liters", "Feed_Quantity_kg"]])
    
    return gbr, iso, le_species, le_breed, le_state, mae

def calculate_hsi(milk, weight, temp, max_milk, max_weight, species="Cow"):
    """Calculates Health Score Index for a given animal."""
    temp_factor = max(0, (40 - abs(temp - 25)) / 40)
    
    if species in ["Cow", "Buffalo", "Goat", "Sheep"]:
        hsi_val = min(100, max(0,
            (milk / max_milk) * 50 +
            (weight / max_weight) * 30 +
            temp_factor * 20
        ))
    else:
        hsi_val = min(100, max(0,
            (weight / max_weight) * 75 +
            temp_factor * 25
        ))
    return hsi_val
