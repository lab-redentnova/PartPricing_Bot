import streamlit as st

# --- SETTINGS ---
LABOR_RATE_DE = 35.00 

MACHINE_DATA = {
    "Prusa XL (FDM)": {"hourly_rate": 1.50, "default_material": 30.0, "waste": 0.05, "desc": "Reliable FDM for functional parts."},
    "Ultimaker (FDM)": {"hourly_rate": 2.20, "default_material": 50.0, "waste": 0.05, "desc": "High-precision FDM for prototypes."},
    "Formlabs (SLA)": {"hourly_rate": 4.50, "default_material": 180.0, "waste": 0.15, "desc": "Resin-based for high detail/smooth finish."}
}

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