import streamlit as st

# --- SETTINGS ---
LABOR_RATE_DE = 35.00 

import streamlit as st

# --- CONFIGURATION ---
ELEC_PRICE_KWH = 0.30  # Average Euro price in Germany 2024-2026
LABOR_RATE_DE = 35.00 

# Machine Specifics: {Hourly Wear/Depreciation, Avg Wattage (Watts)}
MACHINE_SPECS = {
    "Prusa XL (FDM)": {"wear": 1.20, "watts": 300},
    "Ultimaker (FDM)": {"wear": 1.80, "watts": 250},
    "Formlabs (SLA)": {"wear": 4.00, "watts": 60}
}

# Material Specifics: {Price/kg, Risk Multiplier}
MATERIAL_DATA = {
    "PLA (Basic)": {"price": 25.0, "risk_mod": 1.0},
    "PC (High Temp)": {"price": 60.0, "risk_mod": 1.5},
    "Carbon Fiber": {"price": 90.0, "risk_mod": 1.8},
    "Rigid 4000 (SLA)": {"price": 220.0, "risk_mod": 1.2},
    "Tough 2000 (SLA)": {"price": 190.0, "risk_mod": 1.3},
    "Clear Resin (SLA)": {"price": 170.0, "risk_mod": 1.1}
}

# ... (UI Setup code with Logo remains the same) ...

# --- INPUTS ---
with st.sidebar:
    printer = st.selectbox("Select Printer", list(MACHINE_SPECS.keys()))
    # Filter materials based on printer type
    if "SLA" in printer:
        valid_mats = ["Rigid 4000 (SLA)", "Tough 2000 (SLA)", "Clear Resin (SLA)"]
    else:
        valid_mats = ["PLA (Basic)", "PC (High Temp)", "Carbon Fiber"]
    
    mat_type = st.selectbox("Material Type", valid_mats)

# --- NEW CALCULATIONS ---
spec = MACHINE_SPECS[printer]
mat = MATERIAL_DATA[mat_type]

# 1. Precise Electricity Cost
# (Watts / 1000) * Hours * Price_Per_kWh
elec_cost_per_part = (spec["watts"] / 1000) * print_time * ELEC_PRICE_KWH

# 2. Material Cost + Machine Wear
unit_mat_cost = (weight / 1000) * mat["price"]
unit_wear_cost = print_time * spec["wear"]

# 3. Dynamic Risk (Base Risk * Material Difficulty)
base_risk = st.slider("Base Failure Risk %", 0, 50, 10) / 100
final_risk_factor = base_risk * mat["risk_mod"]

# 4. Total Calculation
unit_subtotal = unit_mat_cost + unit_wear_cost + elec_cost_per_part + unit_labor
total_final = (unit_subtotal * qty) * (1 + final_risk_factor)

# Apply Volume Discount if > 100
if qty >= 100:
    total_final *= 0.85

st.set_page_config(page_title="DE-Print Assistant", layout="wide")

# --- LOGO SECTION ---
# You can adjust the width to fit your logo's dimensions
st.image("logo.png", width=300) 

# --- UI HEADER ---
st.title("🤖 3D Print Part Pricing Assistant")
st.markdown(f"**Current Machine:** `{st.sidebar.selectbox('Switch Printer', list(MACHINE_DATA.keys()), key='main_select')}`")

machine_choice = st.session_state.main_select
config = MACHINE_DATA[machine_choice]

# --- TWO COLUMN INPUT ---
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.subheader("📋 Part Details")
    c1, c2 = st.columns(2)
    qty = c1.number_input("Quantity", min_value=1, value=1)
    weight = c2.number_input("Weight/Volume (g/ml)", min_value=1.0, value=50.0)
    
    t1, t2 = st.columns(2)
    print_time = t1.number_input("Print Time (Hours per part)", min_value=0.1, value=4.0)
    labor_mins = t2.number_input("Labor (Minutes per batch)", value=20)

with col2:
    st.subheader("")
    mat_cost = st.number_input("Material €/kg or €/L", value=config["default_material"])

# --- CALCULATIONS ---
unit_mat = (weight / 1000) * mat_cost * (1 + config["waste"])
unit_mach = print_time * config["hourly_rate"]
unit_labor = ((labor_mins / 60) * LABOR_RATE_DE) / qty
total_final = (unit_mat + unit_mach + unit_labor) * qty

if qty >= 100:
    total_final *= 0.85 # 15% Bulk discount

# --- INTERACTIVE FEEDBACK (THE "BOT" PART) ---
st.divider()
res_col1, res_col2 = st.columns([1, 2])

with res_col1:
    st.metric("Total Quote", f"€{total_final:.2f}")
    st.metric("Unit Price", f"€{(total_final/qty):.2f}")

with res_col2:
    st.subheader("💡 Assistant Analysis")
    if total_final / qty > 100:
        st.warning("This part is quite expensive. Consider if FDM is an option or optimize orientation to reduce print time.")
    elif qty > 100:
        st.success(f"Bulk order detected! Applied a 15% discount and optimized labor costs.")
    else:
        st.info("Pricing looks within standard ranges for the German market.")
    
    if machine_choice == "Formlabs (SLA)" and weight > 200:
        st.error("Large resin prints have high failure rates. Ensure supports are heavy-duty.")
