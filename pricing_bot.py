import streamlit as st

# --- 1. FIXED COMPANY CONSTANTS (GERMANY) ---
ELEC_PRICE_KWH = 0.30  # €/kWh
LABOR_RATE_DE = 35.00  # €/hour

# Machine Specifics: {Hourly Wear/Depreciation, Avg Wattage}
MACHINE_SPECS = {
    "Prusa XL (FDM)": {"wear": 1.20, "watts": 300, "type": "FDM"},
    "Ultimaker (FDM)": {"wear": 1.80, "watts": 250, "type": "FDM"},
    "Formlabs (SLA)": {"wear": 4.50, "watts": 60, "type": "SLA"}
}

# Fixed Material Prices (Price per 1kg or 1L)
MATERIAL_PRICES = {
    "PLA (Basic)": 25.00,
    "PC (High Temp)": 65.00,
    "Carbon Fiber": 95.00,
    "Rigid 4000 (SLA)": 220.00,
    "Tough 2000 (SLA)": 195.00,
    "Clear Resin (SLA)": 175.00
}

# --- 2. UI SETUP ---
st.set_page_config(page_title="In-House Pricing Bot", layout="wide")

try:
    st.image("logo.png", width=350)
except:
    pass # Silently skip if logo isn't there

st.title("🤖 3D Print Pricing Assistant")
st.write("Calculated based on slicer data, energy consumption, and labor.")
st.divider()

# --- 3. INPUT SECTION ---
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("🛠️ Machine & Material")
    printer = st.selectbox("Select Printer", list(MACHINE_SPECS.keys()))
    
    # Filter materials based on printer type
    p_type = MACHINE_SPECS[printer]["type"]
    valid_mats = [m for m in MATERIAL_PRICES.keys() if (p_type in m or p_type == "FDM" and "SLA" not in m)]
    mat_type = st.selectbox("Material Type", valid_mats)
    
    st.info(f"Fixed Price for {mat_type}: **€{MATERIAL_PRICES[mat_type]:.2f}/unit**")

with col2:
    st.subheader("📊 Slicer & Labor Data")
    qty = st.number_input("Number of Items", min_value=1, value=1)
    slicer_weight = st.number_input("Material per Part (g or ml)", min_value=0.1, value=10.0)
    print_time = st.number_input("Print Time per Part (Hours)", min_value=0.1, value=1.0)
    labor_mins = st.number_input("PostProcessing per Batch (Minutes)", value=15)

# --- 4. CALCULATION LOGIC ---
spec = MACHINE_SPECS[printer]
mat_price = MATERIAL_PRICES[mat_type]

# A. Material Cost (with 3% waste buffer)
unit_mat_cost = (slicer_weight / 1000) * mat_price * 1.03

# B. Electricity Cost
unit_elec_cost = (spec["watts"] / 1000) * print_time * ELEC_PRICE_KWH

# C. Machine Wear
unit_wear_cost = print_time * spec["wear"]

# D. Labor Cost (Distributed across the quantity)
unit_labor_cost = ((labor_mins / 60) * LABOR_RATE_DE) / qty

# E. Total 
unit_subtotal = unit_mat_cost + unit_elec_cost + unit_wear_cost + unit_labor_cost
total_project = unit_subtotal * qty

# F. Volume Discount (100+ items)
discount_applied = False
if qty >= 100:
    total_project *= 0.85
    discount_applied = True

# --- 5. DISPLAY RESULTS ---
st.divider()
res_col1, res_col2 = st.columns(2)

with res_col1:
    st.metric("Total Project Quote", f"€{total_project:.2f}")
    if discount_applied:
        st.success("✅ 15% Bulk Discount Applied (Order > 100 units)")

with res_col2:
    st.metric("Price per Unit", f"€{(total_project/qty):.2f}")

with st.expander("🔍 Cost Breakdown (Per Unit)"):
    st.write(f"**Material:** €{unit_mat_cost:.2f}")
    st.write(f"**Electricity:** €{unit_elec_cost:.2f}")
    st.write(f"**Machine Wear:** €{unit_wear_cost:.2f}")
    st.write(f"**Labor:** €{unit_labor_cost:.2f}")
