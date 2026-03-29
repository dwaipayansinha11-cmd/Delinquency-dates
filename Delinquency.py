import streamlit as st
import pandas as pd
from datetime import timedelta

# Page configuration
st.set_page_config(page_title="Delinquency Calculator", layout="wide")

# Header Section
st.title("Delinquency calculator")
st.markdown("**Created by Dwaipayan Sinha**")
st.divider()

# --- DATA LOADING ---
@st.cache_data
def load_config():
    try:
        # Loading the CSV file specifically named 'Delinquency.csv'
        df = pd.read_csv('Delinquency.csv')
        # Fill empty cells with 'Not applicable' for consistency in filtering
        df = df.fillna('Not applicable')
        return df
    except FileNotFoundError:
        return None

df_config = load_config()

# --- SIDEBAR (Left Panel) ---
with st.sidebar:
    st.header("Configuration Filters")
    show_config = st.checkbox("Show Master Configuration", value=True)
    st.divider()
    
    if df_config is not None:
        # 1. Bill Type Dropdown
        bill_types = sorted(df_config['Bill Type'].unique().tolist())
        selected_bill = st.selectbox("Bill Type", options=bill_types)
        
        # 2. Allocation mode Dropdown (Filtered by Bill Type)
        alloc_options = sorted(df_config[df_config['Bill Type'] == selected_bill]['Allocation mode'].unique().tolist())
        selected_alloc = st.selectbox("Allocation mode", options=alloc_options)
        
        # --- CONDITIONAL LOGIC FOR INVOICE STATUS ---
        is_logic_met = (selected_bill == "List Bill" and selected_alloc == "Individual payment allocation")
        
        if is_logic_met:
            status_options = sorted([s for s in df_config['Invoice status'].unique() if s != 'Not applicable'])
            selected_status = st.selectbox("Invoice status", options=status_options, disabled=False)
        else:
            selected_status = st.selectbox("Invoice status", options=["Not applicable"], index=0, disabled=True)

        # 3. Product Name Dropdown
        product_options = sorted(df_config['Product Name'].unique().tolist())
        selected_product = st.selectbox("Product Name", options=product_options)

        st.divider()
        
        # 4. Input Date and Trigger Button
        due_date = st.date_input("Invoice Due date")
        btn_calculate = st.button("Delinquency event date", type="primary", use_container_width=True)
    else:
        st.error("File 'Delinquency.csv' not found. Please ensure it is in your project folder.")

# --- MAIN PANEL (Right Panel) ---

if df_config is not None:
    # Section A: Master Configuration Table
    if show_config:
        with st.expander("Database Configuration", expanded=False):
            st.dataframe(df_config, hide_index=True, use_container_width=True)

    # Section B: Results Area
    if btn_calculate:
        # Filter the CSV data to find the matching row
        mask = (
            (df_config['Bill Type'] == selected_bill) & 
            (df_config['Allocation mode'] == selected_alloc) & 
            (df_config['Invoice status'] == selected_status) & 
            (df_config['Product Name'] == selected_product)
        )
        
        filtered_row = df_config[mask]

        if not filtered_row.empty:
            row = filtered_row.iloc[0]
            grace = int(row['Grace Period'])
            
            # Event Date = Invoice Due Date + Grace Period + Event Offset
            results_data = {
                "Delinquency Event": ["Reminder 1", "Reminder 2", "Cancel Notice", "Cancellation Request"],
                "Event Date": [
                    (due_date + timedelta(days=grace + int(row['Reminder 1']))).strftime('%d-%b-%Y'),
                    (due_date + timedelta(days=grace + int(row['Reminder 2']))).strftime('%d-%b-%Y'),
                    (due_date + timedelta(days=grace + int(row['Cancel notice']))).strftime('%d-%b-%Y'),
                    (due_date + timedelta(days=grace + int(row['Cancellation request']))).strftime('%d-%b-%Y')
                ]
            }

            st.subheader(f"Calculated Timeline")
            # Updated Output: Mention only Bill Type and Product Name
            st.write(f"**Applied Configuration:** {selected_bill} | {selected_product}")
            st.write(f"**Invoice Due Date:** {due_date.strftime('%d-%b-%Y')}")
            
            # Display results table with hidden index
            st.dataframe(pd.DataFrame(results_data), hide_index=True, use_container_width=True)
        else:
            st.warning("No matching configuration found for this specific selection.")
    else:
        st.info("Adjust the sidebar settings and click 'Delinquency event date' to view the timeline.")