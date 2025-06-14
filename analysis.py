
import os
import streamlit as st
import pandas as pd
import pyodbc
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import base64
from scipy.stats import chi2_contingency
import scipy.stats as stats
from streamlit_lottie import st_lottie
import requests
import time

from VisualizationofallAnalysis import (
    plot_inventory_quantity,
    plot_demand_vs_supply,
    plot_inventory_value_by_category,
    plot_space_utilization_by_category_location,
    plot_lead_time_by_category,
    plot_top_suppliers_by_sales_value,
    plot_inventory_vs_safety_stock,
    plot_top_products_by_inventory_quantity,
    plot_fill_rate_by_product_category,
    plot_cost_of_stockouts,
    plot_picking_efficiency,
    plot_inventory_by_subcategory,
    plot_top_products_production_over_time,
    plot_scrap_quantity_by_reason,
    plot_top_subcategories_by_sales_and_production,
    plot_top_subcategories_by_production,
    plot_inventory_delay_correlation,
    plot_stock_shortages_vs_overstock,
    plot_inventory_production_delay_correlation,
    plot_seasonal_inventory_vs_production,
    plot_sales_by_territory,
    plot_us_region_sales,
    plot_sales_by_country
)

st.set_page_config(page_title="📊 Inventory Analysis Dashboard", layout="wide")

@st.cache_data
def load_csv_data(input_dir):
    dataframes = {}
    for filename in os.listdir(input_dir):
        if filename.endswith('.csv'):
            table_name = filename.replace('.csv', '')
            try:
                df = pd.read_csv(os.path.join(input_dir, filename))
                if 'ProductID' in df.columns:
                    df['ProductID'] = df['ProductID'].astype(str)
                dataframes[table_name] = df
            except Exception:
                pass
    return dataframes

def show_login():
    def load_lottieurl(url):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()

    if st.session_state.get("logged_in") and st.session_state.get("remember_me"):
        st.success(f"✅ Welcome back, {st.session_state.username}!")
        return

    with st.container():
        col1 = st.columns([1, 2, 1])[1]
        with col1:
            lottie_animation = load_lottieurl("https://assets9.lottiefiles.com/private_files/lf30_wqypnpu5.json")
            if lottie_animation:
                st_lottie(lottie_animation, height=200, key="attrition")
            st.markdown("""
                <div style='background-color: #1A1A40; padding: 10px; border-radius: 10px; margin-top: -50px;'>
                    <h1 style='text-align: center; color: white;'>🔐 Inventory Analysis Web Application</h1>
                </div>
                """, unsafe_allow_html=True)

    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                st.markdown("""
                    <div style="background-color: #FFD9E6; padding: 30px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5); border: 2px solid #1A1A1A; text-align: center;">
                    <h2 style='margin-bottom: 20px; color: #333;'>Login to Continue</h2>
                    """, unsafe_allow_html=True)
                
                st.markdown("""
                    <style>
                        .stTextInput>div>div>input {
                            text-transform: uppercase;
                            font-size: 16px;
                            padding: 10px;
                            text-align: center;
                        }
                        .stTextInput>label {
                            font-weight: bold;
                            text-transform: uppercase;
                            font-size: 14px;
                        }
                    </style>
                    """, unsafe_allow_html=True)

                st.markdown("<h3 style='font-weight: bold; text-transform: uppercase;'>🙂 Please Enter !</h3>", unsafe_allow_html=True)
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                remember_me = st.checkbox("Remember Me", value=False)

                login_button = st.form_submit_button("Login", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            if login_button:
                if not username or not password:
                    st.warning("⚠️ Please fill in both Username and Password.")
                else:
                    with st.spinner('Authenticating...'):
                        time.sleep(1)
                        if username in ["somya", "viewer", "admin"] and password == "admin@1234":
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.role = "admin" if username == "admin" else "viewer"
                            st.session_state.remember_me = remember_me
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Incorrect username or password.")

    st.write("")
    st.markdown("""
        <hr style='border: 1px solid #ccc;'>
        <p style='text-align: center; color: gray;'>© 2025 Inventory Analysis. All rights reserved.</p>
        <p style='text-align: center; color: gray;'>Contact: <a href='mailto:kharesomya251@gmail.com' style='color: gray;'>kharesomya251@gmail.com</a></p>
        """, unsafe_allow_html=True)

# ---------- Run Login ----------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    show_login()
    st.stop()

# ---------- Logout Button ----------
with st.sidebar:
    st.markdown(f"### 👋 Welcome, {st.session_state.get('username', '').title()}")
    if st.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.session_state.clear()
        st.rerun()



# ---------- Main App ----------
input_dir = 'output_csvs'
dataframes = load_csv_data(input_dir)

inventory_df = dataframes.get('ProductInventory')
product_df = dataframes.get('Product')
subcategory_df = dataframes.get('ProductSubcategory')
category_df = dataframes.get('ProductCategory')
location_df = dataframes.get('Location')

# ---------- Navigation ----------
page = st.sidebar.selectbox("📂 Select Page", (
    "📦 Inventory & Stock Insights",
    "🏭 Production & Operational Efficiency",
    "💼 Sales & Supplier Performance",
    "📊 Advanced Analysis & Correlations"
))


# 🌗 Theme Toggle
theme_mode = st.sidebar.radio("🎨 Theme Mode", ["🌞 Light", "🌚 Dark"])
if theme_mode == "🌚 Dark":
    st.markdown("""
        <style>
        .stApp {
            background-color: #0E1117;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

# 📌 Quick Stats
st.sidebar.markdown("### 📌 Quick Stats")
st.sidebar.metric("Products", len(product_df) if product_df is not None else 0)
st.sidebar.metric("Locations", location_df['LocationID'].nunique() if location_df is not None else 0)
st.sidebar.metric("Inventory Records", len(inventory_df) if inventory_df is not None else 0)

# 🌟 Rate App
st.sidebar.markdown("### 🌟 Rate This App")
rating = st.sidebar.slider("Your Rating:", 1, 5, 4)
st.sidebar.write(f"⭐ You rated: **{rating} / 5**")

# 📄 Download CSV
def generate_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download Inventory Data</a>'

st.sidebar.markdown("### 📄 Download Report")
if inventory_df is not None:
    st.sidebar.markdown(generate_download_link(inventory_df, "Inventory_Report.csv"), unsafe_allow_html=True)

# 📬 Contact
st.sidebar.markdown("### 📬 Contact")
st.sidebar.markdown("✉️ [Email Somya](mailto:kharesomya251@gmail.com)")




# ------------------ PAGE 1 ------------------
if page == "📦 Inventory & Stock Insights":
    st.title("📦 Inventory & Stock Insights")

    # ---- Metrics Filter Buttons ----
    with st.expander("🔍 Filter by KPIs"):
        metric_filter = st.radio("Select a KPI filter to apply:", (
            "None",
            "Product Category",
            "Product Subcategory",
            "Product Name",
            "Location"
        ))
        if metric_filter == "Product Category":
            cat = st.selectbox("Select Product Category:", category_df['Name'].unique())
            product_ids = subcategory_df[subcategory_df['ProductCategoryID'] == category_df[category_df['Name'] == cat]['ProductCategoryID'].values[0]]['ProductSubcategoryID'].values
            inventory_df = inventory_df[inventory_df['ProductID'].isin(product_df[product_df['ProductSubcategoryID'].isin(product_ids)]['ProductID'])]
        elif metric_filter == "Product Subcategory":
            subcat = st.selectbox("Select Product Subcategory:", subcategory_df['Name'].unique())
            subcat_id = subcategory_df[subcategory_df['Name'] == subcat]['ProductSubcategoryID'].values[0]
            inventory_df = inventory_df[inventory_df['ProductID'].isin(product_df[product_df['ProductSubcategoryID'] == subcat_id]['ProductID'])]
        elif metric_filter == "Product Name":
            pname = st.selectbox("Select Product Name:", product_df['Name'].unique())
            inventory_df = inventory_df[inventory_df['ProductID'].isin(product_df[product_df['Name'] == pname]['ProductID'])]
        elif metric_filter == "Location":
            loc = st.selectbox("Select Location:", location_df['Name'].unique())
            inventory_df = inventory_df[inventory_df['LocationID'].isin(location_df[location_df['Name'] == loc]['LocationID'])]

    if st.button("🔄 Reset Filters"):
        st.rerun()

    chart_option = st.selectbox("📊 Select an analysis to visualize:", (
        "📉 Inventory Quantity by Product Category",
        "🛡️ Actual Inventory vs Safety Stock Level",
        "🏷️ Top 10 Products by Actual Inventory Quantity",
        "📊 Inventory Quantity by Product Subcategory",
        "📜 Warehouse Space Utilization by Product Category and Location",
        "⚖️ Inventory Mismatches: Stock Shortages vs Overstock",
        "💰 Inventory Value by Product Category"
    ))
    st.markdown("---")

    if chart_option == "📉 Inventory Quantity by Product Category":
        plot_inventory_quantity(inventory_df, product_df, subcategory_df, category_df)

    elif chart_option == "🛡️ Actual Inventory vs Safety Stock Level":
        plot_inventory_vs_safety_stock(inventory_df, product_df)

    elif chart_option == "🏷️ Top 10 Products by Actual Inventory Quantity":
        plot_top_products_by_inventory_quantity(inventory_df, product_df)

    elif chart_option == "📊 Inventory Quantity by Product Subcategory":
        plot_inventory_by_subcategory(dataframes)

    elif chart_option == "📜 Warehouse Space Utilization by Product Category and Location":
        plot_space_utilization_by_category_location(product_df, inventory_df, subcategory_df, category_df, location_df)

    elif chart_option == "⚖️ Inventory Mismatches: Stock Shortages vs Overstock":
        plot_stock_shortages_vs_overstock(dataframes)

    elif chart_option == "💰 Inventory Value by Product Category":
        plot_inventory_value_by_category({
            "Product": product_df,
            "ProductInventory": inventory_df,
            "ProductSubcategory": subcategory_df,
            "ProductCategory": category_df
        })




# ------------------ PAGE 2 ------------------
elif page == "🏭 Production & Operational Efficiency":
    st.title("🏭 Production & Operational Efficiency")

    # 🔍 --- FILTER SECTION ---
    with st.expander("🎯 Apply Filters (Optional)"):
        filter_type = st.radio("Filter By:", ["None", "Product Name", "Location", "Subcategory", "Scrap Quantity"], horizontal=True)

        selected_filter_value = None
        scrap_qty_threshold = None

        if filter_type == "Product Name":
            selected_filter_value = st.selectbox("Select Product:", product_df['Name'].unique())

        elif filter_type == "Location":
            selected_filter_value = st.selectbox("Select Location:", location_df['Name'].unique())

        elif filter_type == "Subcategory":
            selected_filter_value = st.selectbox("Select Subcategory:", subcategory_df['Name'].unique())

        elif filter_type == "Scrap Quantity":
            scrap_qty_threshold = st.slider("Minimum Scrap Quantity:", min_value=0, max_value=500, value=50, step=10)

        # Reset button
        if st.button("🔄 Reset Filters"):
            st.rerun()

    st.markdown("---")

    # 🔧 Filter logic
    filtered_dataframes = dataframes.copy()

    if filter_type == "Product Name" and selected_filter_value:
        product_ids = product_df[product_df['Name'] == selected_filter_value]['ProductID'].tolist()
        filtered_dataframes['WorkOrder'] = dataframes['WorkOrder'][dataframes['WorkOrder']['ProductID'].isin(product_ids)]
        filtered_dataframes['WorkOrderRouting'] = dataframes['WorkOrderRouting'][dataframes['WorkOrderRouting']['ProductID'].isin(product_ids)]

    elif filter_type == "Location" and selected_filter_value:
        location_ids = location_df[location_df['Name'] == selected_filter_value]['LocationID'].tolist()
        filtered_dataframes['WorkOrderRouting'] = dataframes['WorkOrderRouting'][dataframes['WorkOrderRouting']['LocationID'].isin(location_ids)]

    elif filter_type == "Subcategory" and selected_filter_value:
        sub_ids = subcategory_df[subcategory_df['Name'] == selected_filter_value]['ProductSubcategoryID'].astype(str).tolist()
        filtered_products = product_df[product_df['ProductSubcategoryID'].astype(str).isin(sub_ids)]
        filtered_dataframes['WorkOrder'] = dataframes['WorkOrder'][dataframes['WorkOrder']['ProductID'].isin(filtered_products['ProductID'])]
        filtered_dataframes['WorkOrderRouting'] = dataframes['WorkOrderRouting'][dataframes['WorkOrderRouting']['ProductID'].isin(filtered_products['ProductID'])]

    elif filter_type == "Scrap Quantity" and scrap_qty_threshold is not None:
        if 'WorkOrder' in dataframes:
            filtered_dataframes['WorkOrder'] = dataframes['WorkOrder'][dataframes['WorkOrder']['ScrappedQty'] >= scrap_qty_threshold]

    # 📊 --- CHART SELECTION ---
    chart_option = st.selectbox("⚙️ Select an analysis to visualize:", (
        "📈 Top 5 Products Production Trend Over Time",
        "♻️ Scrap Quantity by Reason",
        "⏱️ Lead Time Analysis by Product Category",
        "🚚 Picking Efficiency by Product and Location",
        "📈 Correlation: Inventory, Production, Delay",
        "📉 Seasonality Analysis of Inventory and Production"
    ))
    st.markdown("---")

    # 📊 --- CHART VISUALIZATION ---
    if chart_option == "📈 Top 5 Products Production Trend Over Time":
        plot_top_products_production_over_time(filtered_dataframes)

    elif chart_option == "♻️ Scrap Quantity by Reason":
        plot_scrap_quantity_by_reason(filtered_dataframes)

    elif chart_option == "⏱️ Lead Time Analysis by Product Category":
        plot_lead_time_by_category(
            workorder_df=filtered_dataframes['WorkOrder'],
            product_df=product_df,
            product_subcategory_df=subcategory_df,
            product_category_df=category_df
        )

    elif chart_option == "🚚 Picking Efficiency by Product and Location":
        plot_picking_efficiency(
            work_order_routing_df=filtered_dataframes['WorkOrderRouting'],
            work_order_df=filtered_dataframes['WorkOrder'],
            product_df=product_df,
            location_df=location_df
        )

    elif chart_option == "📈 Correlation: Inventory, Production, Delay":
        plot_inventory_production_delay_correlation(filtered_dataframes)

    elif chart_option == "📉 Seasonality Analysis of Inventory and Production":
        plot_seasonal_inventory_vs_production(filtered_dataframes)





# ------------------ PAGE 3 ------------------
elif page == "💼 Sales & Supplier Performance":
    st.title("💼 Sales & Supplier Performance")

    # 🔍 --- FILTER SECTION ---
    with st.expander("🎯 Apply Filters (Optional)"):
        filter_type = st.radio("Filter By:", ["None", "Product Name", "Location", "Subcategory", "Scrap Quantity"], horizontal=True)
        selected_filter_value = None
        scrap_qty_threshold = None

        if filter_type == "Product Name":
            selected_filter_value = st.selectbox("Select Product:", product_df['Name'].unique())

        elif filter_type == "Location":
            selected_filter_value = st.selectbox("Select Location:", location_df['Name'].unique())

        elif filter_type == "Subcategory":
            selected_filter_value = st.selectbox("Select Subcategory:", subcategory_df['Name'].unique())

        elif filter_type == "Scrap Quantity":
            scrap_qty_threshold = st.slider("Minimum Scrap Quantity:", min_value=0, max_value=500, value=50, step=10)

        if st.button("🔄 Reset Filters"):
            st.rerun()

    # 🔧 Apply filters
    filtered_dataframes = dataframes.copy()
    if filter_type == "Product Name" and selected_filter_value:
        product_ids = product_df[product_df['Name'] == selected_filter_value]['ProductID'].tolist()
        for key in filtered_dataframes:
            if 'ProductID' in filtered_dataframes[key].columns:
                filtered_dataframes[key] = filtered_dataframes[key][filtered_dataframes[key]['ProductID'].isin(product_ids)]

    elif filter_type == "Location" and selected_filter_value:
        location_ids = location_df[location_df['Name'] == selected_filter_value]['LocationID'].tolist()
        if 'WorkOrderRouting' in filtered_dataframes:
            filtered_dataframes['WorkOrderRouting'] = filtered_dataframes['WorkOrderRouting'][filtered_dataframes['WorkOrderRouting']['LocationID'].isin(location_ids)]

    elif filter_type == "Subcategory" and selected_filter_value:
        sub_ids = subcategory_df[subcategory_df['Name'] == selected_filter_value]['ProductSubcategoryID'].astype(str).tolist()
        filtered_products = product_df[product_df['ProductSubcategoryID'].astype(str).isin(sub_ids)]
        for key in filtered_dataframes:
            if 'ProductID' in filtered_dataframes[key].columns:
                filtered_dataframes[key] = filtered_dataframes[key][filtered_dataframes[key]['ProductID'].isin(filtered_products['ProductID'])]

    elif filter_type == "Scrap Quantity" and scrap_qty_threshold is not None:
        if 'WorkOrder' in filtered_dataframes:
            filtered_dataframes['WorkOrder'] = filtered_dataframes['WorkOrder'][filtered_dataframes['WorkOrder']['ScrappedQty'] >= scrap_qty_threshold]

    # 📊 CHART OPTIONS
    chart_option = st.selectbox("💹 Select an analysis to visualize:", (
        "🧾 Top Suppliers by Sales Value",
        "📍 Sales by Territory",
        "🇺🇸 US Region-wise Sales YTD",
        "🌍 Country-wise Sales YTD",
        "🔄 Demand vs Supply by Product",
        "📦 Fill Rate by Product Category"
    ))
    st.markdown("---")

    # 📊 VISUALIZATIONS
    if chart_option == "🧾 Top Suppliers by Sales Value":
        plot_top_suppliers_by_sales_value(
            sales_detail_df=filtered_dataframes['SalesOrderDetail'],
            product_df=filtered_dataframes['Product']
        )

    elif chart_option == "📍 Sales by Territory":
        plot_sales_by_territory(filtered_dataframes)

    elif chart_option == "🇺🇸 US Region-wise Sales YTD":
        conn = get_connection()
        plot_us_region_sales(conn)

    elif chart_option == "🌍 Country-wise Sales YTD":
        conn = pyodbc.connect("Driver={SQL Server};Server=DESKTOP-R54T5QR\\SQLEXPRESS;Database=AdventureWorks2025;Trusted_Connection=yes;")
        st.subheader("🌍 Country-wise Sales YTD Analysis (in Lakhs)")
        plot_sales_by_country(conn)

    elif chart_option == "🔄 Demand vs Supply by Product":
        demand_supply = filtered_dataframes['Product'][['ProductID', 'Name']].merge(
            filtered_dataframes['ProductInventory'].groupby('ProductID')['Quantity'].sum().reset_index(),
            on='ProductID', how='left'
        ).fillna({'Quantity': 0})
        demand_supply['OrderQty'] = 0  # Placeholder
        plot_demand_vs_supply(demand_supply)

    elif chart_option == "📦 Fill Rate by Product Category":
        required_tables = ['SalesOrderDetail', 'WorkOrder', 'Product', 'ProductSubcategory', 'ProductCategory']
        if all(name in filtered_dataframes for name in required_tables):
            p_df = filtered_dataframes['Product']
            sc_df = filtered_dataframes['ProductSubcategory']
            c_df = filtered_dataframes['ProductCategory']

            p_df['ProductSubcategoryID'] = p_df['ProductSubcategoryID'].astype(str)
            sc_df['ProductSubcategoryID'] = sc_df['ProductSubcategoryID'].astype(str)
            sc_df['ProductCategoryID'] = sc_df['ProductCategoryID'].astype(str)
            c_df['ProductCategoryID'] = c_df['ProductCategoryID'].astype(str)

            plot_fill_rate_by_product_category(
                sales_df=filtered_dataframes['SalesOrderDetail'],
                wo_df=filtered_dataframes['WorkOrder'],
                product_df=p_df,
                subcategory_df=sc_df,
                category_df=c_df
            )
        else:
            st.warning("⚠️ Missing tables required for Fill Rate analysis.")


# ------------------ PAGE 4 ------------------
elif page == "📊 Advanced Analysis & Correlations":
    st.title("📊 Advanced Comparative & Correlation Analysis")

    # 🔍 FILTER SECTION
    with st.expander("🎯 Apply Filters (Optional)"):
        filter_type = st.radio("Filter By:", ["None", "Product Name", "Location", "Subcategory", "Scrap Quantity"], horizontal=True)
        selected_filter_value = None
        scrap_qty_threshold = None

        if filter_type == "Product Name":
            selected_filter_value = st.selectbox("Select Product:", product_df['Name'].unique())

        elif filter_type == "Location":
            selected_filter_value = st.selectbox("Select Location:", location_df['Name'].unique())

        elif filter_type == "Subcategory":
            selected_filter_value = st.selectbox("Select Subcategory:", subcategory_df['Name'].unique())

        elif filter_type == "Scrap Quantity":
            scrap_qty_threshold = st.slider("Minimum Scrap Quantity:", min_value=0, max_value=500, value=50, step=10)

        if st.button("🔄 Reset Filters"):
            st.rerun()

    filtered_dataframes = dataframes.copy()
    if filter_type == "Product Name" and selected_filter_value:
        product_ids = product_df[product_df['Name'] == selected_filter_value]['ProductID'].tolist()
        for key in filtered_dataframes:
            if 'ProductID' in filtered_dataframes[key].columns:
                filtered_dataframes[key] = filtered_dataframes[key][filtered_dataframes[key]['ProductID'].isin(product_ids)]

    elif filter_type == "Location" and selected_filter_value:
        location_ids = location_df[location_df['Name'] == selected_filter_value]['LocationID'].tolist()
        if 'WorkOrderRouting' in filtered_dataframes:
            filtered_dataframes['WorkOrderRouting'] = filtered_dataframes['WorkOrderRouting'][filtered_dataframes['WorkOrderRouting']['LocationID'].isin(location_ids)]

    elif filter_type == "Subcategory" and selected_filter_value:
        sub_ids = subcategory_df[subcategory_df['Name'] == selected_filter_value]['ProductSubcategoryID'].astype(str).tolist()
        filtered_products = product_df[product_df['ProductSubcategoryID'].astype(str).isin(sub_ids)]
        for key in filtered_dataframes:
            if 'ProductID' in filtered_dataframes[key].columns:
                filtered_dataframes[key] = filtered_dataframes[key][filtered_dataframes[key]['ProductID'].isin(filtered_products['ProductID'])]

    elif filter_type == "Scrap Quantity" and scrap_qty_threshold is not None:
        if 'WorkOrder' in filtered_dataframes:
            filtered_dataframes['WorkOrder'] = filtered_dataframes['WorkOrder'][filtered_dataframes['WorkOrder']['ScrappedQty'] >= scrap_qty_threshold]

    # 📊 CHART OPTIONS
    chart_option = st.selectbox("🧪 Select an analysis to visualize:", (
        "🏷️ Top 10 Subcategories by Sales Quantity",
        "🏭 Top 10 Subcategories by Production Quantity",
        "📦 Inventory, Sales & Delay Correlation",
        "💸 Cost of Stockouts"
    ))
    st.markdown("---")

    if chart_option == "🏷️ Top 10 Subcategories by Sales Quantity":
        plot_top_subcategories_by_sales_and_production(filtered_dataframes)

    elif chart_option == "🏭 Top 10 Subcategories by Production Quantity":
        plot_top_subcategories_by_production(filtered_dataframes)

    elif chart_option == "📦 Inventory, Sales & Delay Correlation":
        plot_inventory_delay_correlation(filtered_dataframes)

    elif chart_option == "💸 Cost of Stockouts":
        plot_cost_of_stockouts(
            sales_order_detail=filtered_dataframes['SalesOrderDetail'],
            inventory_df=filtered_dataframes['ProductInventory'],
            product_df=filtered_dataframes['Product']
        )


# ---------- Footer ----------
st.markdown("""
    <hr style="margin-top: 30px;">
    <div style='text-align: center; font-size: 14px; padding-top: 10px; color: gray;'>
        Made with ❤️ by <strong>Somya Khare</strong> | © 2025 Inventory Insights
    </div>
""", unsafe_allow_html=True)
