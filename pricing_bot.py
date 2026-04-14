import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. FIXED COMPANY CONSTANTS ---
ELEC_PRICE_KWH = 0.30
LABOR_RATE_DE = 18.00 

MACHINE_SPECS = {
    "Prusa XL (FDM)": {"wear": 1.20, "watts": 300, "type": "FDM"},
    "Ultimaker (FDM)": {"wear": 1.80, "watts": 250, "type": "FDM"},
    "Formlabs (SLA)": {"wear": 4.50, "watts": 60, "type": "SLA"}
}

MATERIAL_PRICES = {
    "PETG (Basic)": 16.60, "PC (High Temp)": 30.49, "Carbon Fiber": 50.00,
    "Rigid 4000 (SLA)": 236.81, "Rigid 10000 (SLA)": 355.81,
    "Tough 2000 (SLA)": 208.25, "Clear Resin (SLA)": 166.60
}

# --- 2. SESSION STATE SETUP ---
# This acts as our "Temporary Database" for the current session
if 'quote_history' not in st.session_state:
    st.session_state.quote_history = []

# --- 3. UI SETUP ---
st.set_page_config(page_title="In-House Pricing Bot", layout="wide")

try:
    st.image("logo.png", width=350)
except:
    pass

st.title("🤖 3D Print Pricing Assistant")
st.divider()

# --- 4. INPUT SECTION ---
with st.container():
    col_part, col_machine = st.columns(2)
    part_name = col_part.text_input("Part Name / ID", value="Unnamed Part")
    printer = col_machine.selectbox("Select Printer", list(MACHINE_SPECS.keys()))

st.subheader("📊 Production Details")
c1, c2, c3 = st.columns(3)

with c1:
    p_type = MACHINE_SPECS[printer]["type"]
    valid_mats = [m for m in MATERIAL_PRICES.keys() if (p_type in m or p_type == "FDM" and "SLA" not in m)]
    mat_type = st.selectbox("Material Type", valid_mats)
    qty = st.number_input("Order Quantity", min_value=1, value=1)

with c2:
    slicer_weight = st.number_input("Slicer Weight/Volume (g or ml)", min_value=0.1, value=10.0)
    st.write("**Print Duration:**")
    h_col, m_col = st.columns(2)
    h_in = h_col.number_input("Hours", min_value=0, value=1, key="hr")
    m_in = m_col.number_input("Minutes", min_value=0, max_value=59, value=0, key="min")
    # Convert to decimal hours for math
    print_time_decimal = h_in + (m_in / 60)

with c3:
    labor_mins = st.number_input("Post-Processing per Batch (Mins)", value=15)
    st.info(f"Fixed Material Cost: €{MATERIAL_PRICES[mat_type]:.2f}/unit")

# --- 5. CALCULATIONS ---
spec = MACHINE_SPECS[printer]
mat_price = MATERIAL_PRICES[mat_type]

unit_mat_cost = (slicer_weight / 1000) * mat_price * 1.03
unit_elec_cost = (spec["watts"] / 1000) * print_time_decimal * ELEC_PRICE_KWH
unit_wear_cost = print_time_decimal * spec["wear"]
unit_labor_cost = ((labor_mins / 60) * LABOR_RATE_DE) / qty

unit_subtotal = unit_mat_cost + unit_elec_cost + unit_wear_cost + unit_labor_cost
total_project = unit_subtotal * qty
if qty >= 100: total_project *= 0.85

# --- 6. RESULTS & LOGGING ---
st.divider()
r1, r2 = st.columns([1, 1])

r1.metric("Total Project Quote", f"€{total_project:.2f}")
r2.metric("Price per Unit", f"€{(total_project/qty):.2f}")

if st.button("➕ Save Quote to Session Log"):
    new_entry = {
        "Timestamp": datetime.now().strftime("%H:%M:%S"),
        "Part Name": part_name,
        "Printer": printer,
        "Qty": qty,
        "Total Price (€)": round(total_project, 2),
        "Unit Price (€)": round(total_project/qty, 2),
        "Mat Cost": round(unit_mat_cost, 2),
        "Elec Cost": round(unit_elec_cost, 2),
        "Labor Cost": round(unit_labor_cost, 2)
    }
    st.session_state.quote_history.append(new_entry)
    st.toast(f"Saved {part_name} to log!")

# --- 7. THE LOG TABLE ---
if st.session_state.quote_history:
    st.subheader("📋 Session Quote Log")
    df = pd.DataFrame(st.session_state.quote_history)
    st.dataframe(df, use_container_width=True)
    
    # Download as CSV (Excel compatible)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Log as CSV (Excel)",
        data=csv,
        file_name=f"print_quotes_{datetime.now().strftime('%Y-%m-%d')}.csv",
        mime="text/csv",
    )
