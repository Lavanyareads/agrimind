import streamlit as st
import pandas as pd
from components.auth import require_auth
from database.db_utils import get_livestock_by_user
from models.ml_utils import get_trained_models, calculate_hsi, load_static_data
from utils.styling import get_css, PRIMARY, ACCENT, AMBER, RED, TEXT_DIM

st.set_page_config(page_title="Feed Predictor", layout="wide")
require_auth()
st.markdown(get_css(), unsafe_allow_html=True)

gbr, _, le_species, le_breed, le_state, model_mae = get_trained_models()
df_static = load_static_data()
max_milk = df_static["Milk_Yield_Liters"].max()
max_weight = df_static["Weight_kg"].max()

st.markdown('<div class="page-header"><h1>AI Feed Predictor</h1><p>Predict optimal feed quantities for your herd.</p></div>', unsafe_allow_html=True)

# Fetch user's livestock
herd = get_livestock_by_user(st.session_state.user_id)

if not herd:
    st.warning("You have no livestock registered. Please go to 'My Herd' to add animals first.")
    st.stop()

st.markdown('<div class="section-title">Select Animal</div>', unsafe_allow_html=True)

# Create a mapping of animal names (e.g., "Cow - Gir (400kg)") to the dictionary
animal_options = {f"{a['species']} - {a['breed']} ({a['weight_kg']}kg)": a for a in herd}
selected_animal_str = st.selectbox("Choose an animal from your herd to predict for:", list(animal_options.keys()))

animal = animal_options[selected_animal_str]

st.markdown("---")
c1, c2 = st.columns([1, 1], gap="large")

with c1:
    st.markdown("### Economic Parameters")
    feed_cost  = st.slider("Feed cost (Rs/kg)",     10, 30, 18)
    milk_price = st.slider("Milk price (Rs/liter)", 30, 80, 50)
    p_temp     = st.number_input("Current Temperature (C)", 10, 45, 28)
    run_btn    = st.button("Run Prediction", type="primary", use_container_width=True)

with c2:
    if run_btn:
        # Encode inputs safely
        sp_enc = le_species.transform([animal['species']])[0] if animal['species'] in le_species.classes_ else 0
        br_enc = le_breed.transform([animal['breed']])[0] if animal['breed'] in le_breed.classes_ else 0
        st_enc = le_state.transform([animal['state']])[0] if animal['state'] in le_state.classes_ else 0
        
        X_pred = pd.DataFrame([[
            animal['weight_kg'], animal['age_years'], animal['milk_yield_liters'], 
            p_temp, sp_enc, br_enc, st_enc
        ]], columns=["Weight_kg","Age_Years","Milk_Yield_Liters","Temperature_C","Species_enc","Breed_enc","State_enc"])
        
        pred_feed = gbr.predict(X_pred)[0]
        roughage  = round(pred_feed * 0.6, 2)
        conc      = round(pred_feed * 0.4, 2)
        
        hsi_val = calculate_hsi(animal['milk_yield_liters'], animal['weight_kg'], p_temp, max_milk, max_weight, animal['species'])
        hsi_color = ACCENT if hsi_val >= 75 else (AMBER if hsi_val >= 50 else RED)
        hsi_label = "HEALTHY" if hsi_val >= 75 else ("MONITOR" if hsi_val >= 50 else "CRITICAL")
        
        st.markdown(f"""
        <div class="result-card" style="background: linear-gradient(135deg, {PRIMARY} 0%, #1B4332 100%); padding: 24px; border-radius: 8px; text-align: center;">
          <div style="font-size: 0.8rem; text-transform: uppercase; color: #9DB8A4;">Recommended Daily Feed</div>
          <div style="font-size: 3rem; font-weight: 800; color: #E8F0EB;">{pred_feed:.2f}</div>
          <div style="color: {ACCENT}; font-size: 1rem;">kg / day</div>
        </div>
        """, unsafe_allow_html=True)
        
        r1, r2 = st.columns(2)
        r1.metric("Roughage", f"{roughage} kg", "60%")
        r2.metric("Concentrate", f"{conc} kg", "40%")
        
        st.markdown(f"""
        <div style="margin-top:20px; padding: 20px; border: 1px solid #2A3D30; border-radius: 8px; text-align:center; background: #161E19;">
          <div style="font-size: 2rem; font-weight: bold; color: {hsi_color};">{hsi_val:.0f}</div>
          <div style="font-size: 0.8rem; color: #9DB8A4;">Health Score Index (HSI)</div>
          <div style="color: {hsi_color}; font-weight: bold; margin-top: 5px;">{hsi_label}</div>
        </div>
        """, unsafe_allow_html=True)
        
        daily_cost_ = pred_feed * feed_cost
        
        if animal['species'] in ["Cow", "Buffalo", "Sheep", "Goat"]:
            daily_rev_  = animal['milk_yield_liters'] * milk_price
            monthly_net = (daily_rev_ - daily_cost_) * 30
            pclass = "strip-green" if monthly_net > 0 else "strip-red"
            
            st.markdown(f"""
            <div class="strip {pclass}">
              <strong>Monthly Economic Estimate (for this animal)</strong><br>
              Feed cost: Rs {daily_cost_*30:,.0f} &nbsp;|&nbsp;
              Milk revenue: Rs {daily_rev_*30:,.0f} &nbsp;|&nbsp;
              Net profit: <strong>Rs {monthly_net:,.0f}</strong>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="strip strip-neutral">
              <strong>Monthly Economic Estimate (for this animal)</strong><br>
              Estimated Feed cost: Rs {daily_cost_*30:,.0f} <br>
              <span style="font-size: 0.75rem; color: {{TEXT_DIM}}">Note: Revenue estimates are hidden for non-dairy animals.</span>
            </div>""", unsafe_allow_html=True)
            
        # ── FEEDING SCHEDULER ─────────────────────
        st.markdown("<div style='margin-top:18px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Smart Feeding Scheduler</div>', unsafe_allow_html=True)
        
        if animal['species'] in ["Cow", "Buffalo", "Sheep", "Goat"]:
            morning_feed = round(pred_feed * 0.4, 2)
            afternoon_feed = round(pred_feed * 0.2, 2)
            evening_feed = round(pred_feed * 0.4, 2)

            schedule_df = pd.DataFrame({
                "Time": ["6:00 AM", "1:00 PM", "7:00 PM"],
                "Feed Quantity (kg)": [morning_feed, afternoon_feed, evening_feed],
                "Meal Components": ["Roughage + Minerals", "Light Concentrate", "Roughage + Concentrate"]
            })
            water_needed = round(pred_feed * 4.5, 1)
        else:
            morning_feed = round(pred_feed * 0.5, 2)
            evening_feed = round(pred_feed * 0.5, 2)

            schedule_df = pd.DataFrame({
                "Time": ["7:00 AM", "6:00 PM"],
                "Feed Quantity (kg)": [morning_feed, evening_feed],
                "Meal Components": ["Standard Mix", "Standard Mix + Supplements"]
            })
            water_needed = round(pred_feed * 2.5, 1)

        st.dataframe(schedule_df, use_container_width=True, hide_index=True)

        st.markdown(f"""
        <div class="strip strip-green">
          <strong>Daily Care Recommendation</strong><br>
          Recommended water intake: <strong>{water_needed} liters/day</strong><br>
          <em>Keep fresh water available at all times. The above schedule is optimized for {animal['species']} digestion.</em>
        </div>
        """, unsafe_allow_html=True)
