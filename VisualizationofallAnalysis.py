
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st
import pandas as pd


def plot_inventory_quantity(inventory_df, product_df, subcategory_df, category_df):
    inventory_df['ProductID'] = inventory_df['ProductID'].astype(str)
    product_df['ProductID'] = product_df['ProductID'].astype(str)
    product_df['ProductSubcategoryID'] = product_df['ProductSubcategoryID'].astype(str)
    subcategory_df['ProductSubcategoryID'] = subcategory_df['ProductSubcategoryID'].astype(str)
    subcategory_df['ProductCategoryID'] = subcategory_df['ProductCategoryID'].astype(str)
    category_df['ProductCategoryID'] = category_df['ProductCategoryID'].astype(str)

    merged = inventory_df.merge(product_df[['ProductID', 'ProductSubcategoryID']], on='ProductID', how='left')
    merged = merged.merge(subcategory_df[['ProductSubcategoryID', 'ProductCategoryID']], on='ProductSubcategoryID', how='left')
    merged = merged.merge(category_df[['ProductCategoryID', 'Name']], on='ProductCategoryID', how='left')

    category_summary = merged.groupby('Name')['Quantity'].sum().reset_index()
    sorted_data = category_summary.sort_values('Quantity', ascending=False)

    plt.figure(figsize=(14, 7))
    sns.barplot(data=sorted_data, x='Quantity', y='Name', palette='viridis')
    plt.title('Inventory Quantity by Product Category', fontsize=20, fontweight='bold')
    plt.xlabel('Quantity', fontsize=15)
    plt.ylabel('Product Category', fontsize=15)

    for index, value in enumerate(sorted_data['Quantity']):
        plt.text(value + max(sorted_data['Quantity']) * 0.01, index, f'{value}', va='center', fontweight='bold', fontsize=12)

    st.pyplot(plt.gcf())


def plot_demand_vs_supply(demand_supply):
    df_melt = demand_supply.melt(
        id_vars='Name', 
        value_vars=['OrderQty', 'Quantity'], 
        var_name='Type', 
        value_name='Amount'
    )
    
    plt.figure(figsize=(14, 7))
    sns.barplot(data=df_melt, x='Name', y='Amount', hue='Type', palette='Set2')
    plt.xticks(rotation=90)
    plt.title('Demand vs Supply by Product', fontsize=16, fontweight='bold')
    plt.xlabel('Product Name', fontsize=14)
    plt.ylabel('Amount', fontsize=14)
    plt.tight_layout()
    
    st.pyplot(plt.gcf())





def plot_inventory_value_by_category(dataframes):
    product_df = dataframes['Product']
    product_inventory_df = dataframes['ProductInventory']
    product_subcategory_df = dataframes['ProductSubcategory']
    product_category_df = dataframes['ProductCategory']

    product_df['ProductID'] = product_df['ProductID'].astype(str)
    product_inventory_df['ProductID'] = product_inventory_df['ProductID'].astype(str)
    product_df['ProductSubcategoryID'] = product_df['ProductSubcategoryID'].astype(str)
    product_subcategory_df['ProductSubcategoryID'] = product_subcategory_df['ProductSubcategoryID'].astype(str)
    product_subcategory_df['ProductCategoryID'] = product_subcategory_df['ProductCategoryID'].astype(str)
    product_category_df['ProductCategoryID'] = product_category_df['ProductCategoryID'].astype(str)

    inventory_per_product = product_inventory_df.groupby('ProductID')['Quantity'].sum().reset_index()

    inventory_with_cost = inventory_per_product.merge(
        product_df[['ProductID', 'StandardCost', 'ProductSubcategoryID']],
        on='ProductID', how='left'
    )

    inventory_with_cost['InventoryValue'] = inventory_with_cost['Quantity'] * inventory_with_cost['StandardCost']

    inventory_with_subcat = inventory_with_cost.merge(
        product_subcategory_df[['ProductSubcategoryID', 'ProductCategoryID']],
        on='ProductSubcategoryID', how='left'
    )

    inventory_with_cat = inventory_with_subcat.merge(
        product_category_df[['ProductCategoryID', 'Name']],
        on='ProductCategoryID', how='left'
    ).rename(columns={'Name': 'CategoryName'})

    category_inventory_value = inventory_with_cat.groupby('CategoryName')['InventoryValue'].sum().reset_index()
    category_inventory_value = category_inventory_value.sort_values(by='InventoryValue', ascending=False)

    plt.figure(figsize=(14, 6))

    plt.subplot(1, 2, 1)
    plt.pie(category_inventory_value['InventoryValue'], 
            labels=category_inventory_value['CategoryName'], 
            autopct='%.1f%%', 
            pctdistance=0.85,
            startangle=90, 
            textprops={"fontsize": 12, "fontweight": "bold"},
            colors=sns.color_palette('pastel'))
    plt.title('Inventory Value Share by Category', fontsize=16, fontweight='bold')
    plt.gca().add_artist(plt.Circle((0, 0), 0.50, color='white'))

    plt.subplot(1, 2, 2)
    sns.barplot(x='InventoryValue', y='CategoryName', data=category_inventory_value, palette='viridis')
    plt.xlabel('Total Inventory Value', fontsize=12)
    plt.ylabel('Category Name', fontsize=12)
    plt.title('Inventory Value by Product Category', fontsize=16, fontweight='bold')

    plt.tight_layout()
    st.pyplot(plt.gcf())


def plot_space_utilization_by_category_location(
    product_df, product_inventory_df, product_subcategory_df, product_category_df, location_df, use_streamlit=True
):
    product_df['ProductID'] = product_df['ProductID'].astype(str)
    product_inventory_df['ProductID'] = product_inventory_df['ProductID'].astype(str)
    product_inventory_df['LocationID'] = product_inventory_df['LocationID'].astype(str)
    product_df['ProductSubcategoryID'] = product_df['ProductSubcategoryID'].astype(str)
    product_subcategory_df['ProductSubcategoryID'] = product_subcategory_df['ProductSubcategoryID'].astype(str)
    product_subcategory_df['ProductCategoryID'] = product_subcategory_df['ProductCategoryID'].astype(str)
    product_category_df['ProductCategoryID'] = product_category_df['ProductCategoryID'].astype(str)
    location_df['LocationID'] = location_df['LocationID'].astype(str)

    inventory_loc = product_inventory_df.groupby(['ProductID', 'LocationID'])['Quantity'].sum().reset_index()
    inventory_loc = inventory_loc.merge(product_df[['ProductID', 'ProductSubcategoryID']], on='ProductID', how='left')
    inventory_loc = inventory_loc.merge(product_subcategory_df[['ProductSubcategoryID', 'ProductCategoryID']], on='ProductSubcategoryID', how='left')
    inventory_loc = inventory_loc.merge(product_category_df[['ProductCategoryID', 'Name']], on='ProductCategoryID', how='left').rename(columns={'Name': 'CategoryName'})
    inventory_loc = inventory_loc.merge(location_df[['LocationID', 'Name']], on='LocationID', how='left').rename(columns={'Name': 'LocationName'})

    space_utilization = inventory_loc.groupby(['LocationName', 'CategoryName'])['Quantity'].sum().reset_index()
    space_pivot = space_utilization.pivot(index='LocationName', columns='CategoryName', values='Quantity').fillna(0)

    plt.figure(figsize=(14, 8))
    sns.heatmap(space_pivot, annot=True, fmt=".0f", cmap='YlGnBu')
    plt.title('Warehouse Space Utilization by Category and Location', fontsize=16, fontweight='bold')
    plt.xlabel('Product Category', fontsize=14)
    plt.ylabel('Warehouse Location', fontsize=14)
    plt.tight_layout()

    if use_streamlit:
        st.pyplot(plt.gcf())
    else:
        plt.show()






def plot_lead_time_by_category(workorder_df, product_df, product_subcategory_df, product_category_df):
    # Convert IDs to strings
    workorder_df['ProductID'] = workorder_df['ProductID'].astype(str)
    product_df['ProductID'] = product_df['ProductID'].astype(str)
    product_df['ProductSubcategoryID'] = product_df['ProductSubcategoryID'].astype(str)
    product_subcategory_df['ProductSubcategoryID'] = product_subcategory_df['ProductSubcategoryID'].astype(str)
    product_subcategory_df['ProductCategoryID'] = product_subcategory_df['ProductCategoryID'].astype(str)
    product_category_df['ProductCategoryID'] = product_category_df['ProductCategoryID'].astype(str)

    # Convert StartDate and EndDate to datetime
    workorder_df['StartDate'] = pd.to_datetime(workorder_df['StartDate'])
    workorder_df['EndDate'] = pd.to_datetime(workorder_df['EndDate'])

    # Calculate Lead Time
    workorder_df['LeadTimeDays'] = (workorder_df['EndDate'] - workorder_df['StartDate']).dt.days
    workorder_df = workorder_df[workorder_df['LeadTimeDays'] >= 0]

    # Merge to get Category Name
    leadtime_with_product = workorder_df.merge(
        product_df[['ProductID', 'ProductSubcategoryID']], on='ProductID', how='left'
    ).merge(
        product_subcategory_df[['ProductSubcategoryID', 'ProductCategoryID']], on='ProductSubcategoryID', how='left'
    ).merge(
        product_category_df[['ProductCategoryID', 'Name']], on='ProductCategoryID', how='left'
    ).rename(columns={'Name': 'CategoryName'})

    # Drop missing category names
    leadtime_with_product = leadtime_with_product.dropna(subset=['CategoryName'])

    # Plot
    st.subheader("🕒 Lead Time Distribution by Product Category")
    plt.figure(figsize=(14, 8))
    sns.boxplot(data=leadtime_with_product, x='CategoryName', y='LeadTimeDays')
    plt.xticks(rotation=45, ha='right')
    plt.title('Lead Time Distribution by Product Category')
    plt.xlabel('Product Category')
    plt.ylabel('Lead Time (Days)')
    plt.tight_layout()
    st.pyplot(plt)







def plot_top_suppliers_by_sales_value(sales_detail_df, product_df):
    # Ensure matching types
    sales_detail_df['ProductID'] = sales_detail_df['ProductID'].astype(str)
    product_df['ProductID'] = product_df['ProductID'].astype(str)

    # Aggregate sales by ProductID
    product_sales = sales_detail_df.groupby('ProductID').agg(
        TotalVolume=('OrderQty', 'sum'),
        TotalValue=('LineTotal', 'sum')
    ).reset_index()

    # Merge ProductModelID (acts as proxy for supplier)
    product_sales = product_sales.merge(
        product_df[['ProductID', 'ProductModelID']],
        on='ProductID',
        how='left'
    )

    # Aggregate by ProductModelID (proxy supplier)
    supplier_like = product_sales.groupby('ProductModelID').agg(
        TotalVolume=('TotalVolume', 'sum'),
        TotalValue=('TotalValue', 'sum')
    ).reset_index()

    # Sort and select top 10
    top_suppliers = supplier_like.sort_values(by='TotalValue', ascending=False).head(10)

    # Plotting
    st.subheader("🏅 Top 10 Proxy Suppliers by Sales Value (via ProductModelID)")
    plt.figure(figsize=(12, 7))
    plt.barh(top_suppliers['ProductModelID'].astype(str), top_suppliers['TotalValue'], color='orange')
    plt.xlabel('Total Sales Value')
    plt.ylabel('ProductModelID (Proxy Supplier)')
    plt.title('Top 10 Proxy Suppliers by Sales Value')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    st.pyplot(plt)





def plot_top_products_by_inventory_quantity(product_inventory_df, product_df):

    # Ensure ProductID is the same type
    product_inventory_df['ProductID'] = product_inventory_df['ProductID'].astype(int)
    product_df['ProductID'] = product_df['ProductID'].astype(int)

    # Aggregate inventory by ProductID
    actual_inventory = product_inventory_df.groupby('ProductID')['Quantity'].sum().reset_index()

    # Merge with product names
    actual_inventory = actual_inventory.merge(
        product_df[['ProductID', 'Name']],
        on='ProductID',
        how='left'
    )

    # Sort and get top 10
    top_inventory = actual_inventory.sort_values(by='Quantity', ascending=False).head(10)

    # Plotting
    st.subheader("📦 Top 10 Products by Actual Inventory Quantity")
    plt.figure(figsize=(12, 7))
    plt.barh(top_inventory['Name'], top_inventory['Quantity'], color='steelblue')
    plt.xlabel('Actual Inventory Quantity')
    plt.title('Top 10 Products by Actual Inventory')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    st.pyplot(plt)




def plot_inventory_vs_safety_stock(product_inventory_df, product_df):

    # Ensure ProductID is consistent type
    product_inventory_df['ProductID'] = product_inventory_df['ProductID'].astype(int)
    product_df['ProductID'] = product_df['ProductID'].astype(int)

    # Aggregate inventory quantity
    actual_inventory = product_inventory_df.groupby('ProductID')['Quantity'].sum().reset_index()

    # Merge with product details
    inventory_vs_safety = actual_inventory.merge(
        product_df[['ProductID', 'Name', 'SafetyStockLevel']],
        on='ProductID',
        how='left'
    )

    # Filter valid safety stock levels
    inventory_vs_safety = inventory_vs_safety[inventory_vs_safety['SafetyStockLevel'] > 0]

    # Sort and limit to top 20 by safety stock
    inventory_vs_safety = inventory_vs_safety.sort_values('SafetyStockLevel', ascending=False).head(20)

    # Plot
    st.subheader("🛡️ Actual Inventory vs Safety Stock Level (Top 20 Products)")
    plt.figure(figsize=(12, 8))
    bar_width = 0.4
    indices = range(len(inventory_vs_safety))

    plt.bar(indices, inventory_vs_safety['Quantity'], width=bar_width, label='Actual Inventory', color='steelblue')
    plt.bar([i + bar_width for i in indices], inventory_vs_safety['SafetyStockLevel'], width=bar_width, label='Safety Stock Level', color='orange')

    plt.xticks([i + bar_width / 2 for i in indices], inventory_vs_safety['Name'], rotation=90)
    plt.ylabel('Quantity')
    plt.title('Actual Inventory vs Safety Stock Level for Top 20 Products')
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)







def plot_fill_rate_by_product_category(sales_df, wo_df, product_df, subcategory_df, category_df):


    # Step 0: Ensure consistent data types
    sales_df['ProductID'] = sales_df['ProductID'].astype(str)
    wo_df['ProductID'] = wo_df['ProductID'].astype(str)
    product_df['ProductID'] = product_df['ProductID'].astype(str)

    # Step 1: Calculate Total Quantity Ordered per Product
    total_ordered = sales_df.groupby('ProductID')['OrderQty'].sum().reset_index()
    total_ordered.rename(columns={'OrderQty': 'TotalOrdered'}, inplace=True)

    # Step 2: Calculate Quantity Shipped On Time per Product
    wo_df['EndDate'] = pd.to_datetime(wo_df['EndDate'], errors='coerce')
    wo_df['DueDate'] = pd.to_datetime(wo_df['DueDate'], errors='coerce')
    shipped_on_time = wo_df[wo_df['EndDate'] <= wo_df['DueDate']]
    shipped_qty = shipped_on_time.groupby('ProductID')['StockedQty'].sum().reset_index()
    shipped_qty.rename(columns={'StockedQty': 'ShippedOnTime'}, inplace=True)

    # Step 3: Merge and Calculate Fill Rate
    fill_rate_df = pd.merge(total_ordered, shipped_qty, on='ProductID', how='left')
    fill_rate_df['ShippedOnTime'].fillna(0, inplace=True)
    fill_rate_df['FillRate'] = (fill_rate_df['ShippedOnTime'] / fill_rate_df['TotalOrdered']) * 100

    # Step 4: Add Product Category Info
    product_info = product_df[['ProductID', 'ProductSubcategoryID']]
    product_info = pd.merge(product_info, subcategory_df[['ProductSubcategoryID', 'ProductCategoryID']], on='ProductSubcategoryID', how='left')
    product_info = pd.merge(product_info, category_df[['ProductCategoryID', 'Name']], on='ProductCategoryID', how='left')
    product_info.rename(columns={'Name': 'ProductCategory'}, inplace=True)

    product_info['ProductID'] = product_info['ProductID'].astype(str)
    fill_rate_df['ProductID'] = fill_rate_df['ProductID'].astype(str)

    fill_rate_df = pd.merge(fill_rate_df, product_info[['ProductID', 'ProductCategory']], on='ProductID', how='left')

    # Step 5: Aggregate and Plot
    category_fill = fill_rate_df.groupby('ProductCategory')['FillRate'].mean().reset_index()

    plt.figure(figsize=(10, 6))
    sns.barplot(data=category_fill.sort_values('FillRate', ascending=False),
                x='FillRate', y='ProductCategory', palette='viridis')
    plt.title('📦 Average Inventory Fill Rate by Product Category')
    plt.xlabel('Fill Rate (%)')
    plt.ylabel('Product Category')
    plt.tight_layout()

    # Show in Streamlit
    st.pyplot(plt.gcf())
    plt.clf()





def plot_cost_of_stockouts(sales_order_detail, inventory_df, product_df):


    # Step 1: Aggregate orders by product
    orders_by_product = sales_order_detail.groupby('ProductID')['OrderQty'].sum().reset_index()
    orders_by_product.rename(columns={'OrderQty': 'TotalOrdered'}, inplace=True)

    # Step 2: Aggregate available inventory by product
    inventory_by_product = inventory_df.groupby('ProductID')['Quantity'].sum().reset_index()
    inventory_by_product.rename(columns={'Quantity': 'InventoryAvailable'}, inplace=True)

    # 🔧 Ensure both ProductID columns are of the same type
    orders_by_product['ProductID'] = orders_by_product['ProductID'].astype(str)
    inventory_by_product['ProductID'] = inventory_by_product['ProductID'].astype(str)

    # Step 3: Merge and calculate stockout
    stockout_df = orders_by_product.merge(inventory_by_product, on='ProductID', how='left')
    stockout_df['InventoryAvailable'].fillna(0, inplace=True)
    stockout_df['Shortfall'] = stockout_df['TotalOrdered'] - stockout_df['InventoryAvailable']
    stockout_df['Shortfall'] = stockout_df['Shortfall'].apply(lambda x: max(x, 0))

    # Step 4: Merge with product prices
    product_df['ProductID'] = product_df['ProductID'].astype(str)
    price_df = product_df[['ProductID', 'ListPrice']]
    stockout_df = stockout_df.merge(price_df, on='ProductID', how='left')
    stockout_df['CostOfStockout'] = stockout_df['Shortfall'] * stockout_df['ListPrice']
    stockout_df = stockout_df.sort_values('CostOfStockout', ascending=False).head(10)

    # Step 5: Merge with product name
    name_df = product_df[['ProductID', 'Name']]
    stockout_df = stockout_df.merge(name_df, on='ProductID', how='left')

    # Step 6: Plot
    plt.figure(figsize=(10, 6))
    sns.barplot(data=stockout_df, x='CostOfStockout', y='Name', palette='Reds_r')
    plt.title("💸 Top 10 Products by Cost of Stockouts")
    plt.xlabel("Cost of Stockouts ($)")
    plt.ylabel("Product")
    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.clf()







def plot_picking_efficiency(work_order_routing_df, work_order_df, product_df, location_df):


    # --- Ensure consistent merge key types ---
    for df in [work_order_routing_df, work_order_df, product_df]:
        if 'ProductID' in df.columns:
            df['ProductID'] = df['ProductID'].astype(str)
    if 'ProductID' in location_df.columns:
        location_df['ProductID'] = location_df['ProductID'].astype(str)

    if 'LocationID' in work_order_routing_df.columns:
        work_order_routing_df['LocationID'] = work_order_routing_df['LocationID'].astype(str)
    if 'LocationID' in location_df.columns:
        location_df['LocationID'] = location_df['LocationID'].astype(str)

    # Step 1: Aggregate time and cost
    routing_agg = work_order_routing_df.groupby(['WorkOrderID', 'ProductID', 'LocationID']).agg({
        'ActualResourceHrs': 'sum',
        'ActualCost': 'sum'
    }).reset_index()

    # Step 2: Aggregate stocked quantity
    work_order_agg = work_order_df.groupby(['WorkOrderID', 'ProductID']).agg({
        'StockedQty': 'sum'
    }).reset_index()

    # Step 3: Merge and calculate per-pick efficiency
    merged = pd.merge(routing_agg, work_order_agg, on=['WorkOrderID', 'ProductID'], how='left')
    merged['StockedQty'].replace(0, pd.NA, inplace=True)
    merged.dropna(subset=['StockedQty'], inplace=True)
    merged['TimePerPick'] = merged['ActualResourceHrs'] / merged['StockedQty']
    merged['CostPerPick'] = merged['ActualCost'] / merged['StockedQty']

    # Step 4: Aggregate by ProductID and LocationID
    efficiency = merged.groupby(['ProductID', 'LocationID']).agg({
        'TimePerPick': 'mean',
        'CostPerPick': 'mean'
    }).reset_index()

    # Step 5: Add product and location names
    efficiency = efficiency.merge(product_df[['ProductID', 'Name']], on='ProductID', how='left')
    efficiency = efficiency.merge(
        location_df[['LocationID', 'Name']],
        on='LocationID',
        how='left',
        suffixes=('_Product', '_Location')
    )

    # Step 6: Drop NA values
    efficiency.dropna(subset=['TimePerPick', 'CostPerPick', 'Name_Product', 'Name_Location'], inplace=True)

    # Step 7: Plot top 10 by TimePerPick
    top_time = efficiency.sort_values('TimePerPick', ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(
        data=top_time,
        y='Name_Product',
        x='TimePerPick',
        hue='Name_Location',
        dodge=False,
        palette='coolwarm',
        ax=ax
    )

    ax.set_title('🚚 Top 10 Products by Avg. Time Per Pick per Location')
    ax.set_xlabel('Average Time Per Pick (hours)')
    ax.set_ylabel('Product Name')
    ax.legend(title='Location', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    st.pyplot(fig)
    plt.clf()







def plot_inventory_by_subcategory(dataframes):


    # Validate required tables
    required_tables = ['ProductInventory', 'Product', 'ProductSubcategory']
    if not all(name in dataframes for name in required_tables):
        st.error("❌ Required tables (ProductInventory, Product, ProductSubcategory) are missing.")
        return

    # --- Step 0: Ensure consistent dtypes for ProductID across all involved tables ---
    for df_name in ['ProductInventory', 'Product']:
        if 'ProductID' in dataframes[df_name].columns:
            dataframes[df_name]['ProductID'] = dataframes[df_name]['ProductID'].astype(str)

    # Step 1: Merge ProductInventory with Product to get ProductSubcategoryID
    inventory_merged = pd.merge(
        dataframes['ProductInventory'],
        dataframes['Product'][['ProductID', 'ProductSubcategoryID']],
        on='ProductID',
        how='left'
    )

    # Step 2: Ensure consistent data types for ProductSubcategoryID
    inventory_merged['ProductSubcategoryID'] = pd.to_numeric(inventory_merged['ProductSubcategoryID'], errors='coerce')
    dataframes['ProductSubcategory']['ProductSubcategoryID'] = pd.to_numeric(
        dataframes['ProductSubcategory']['ProductSubcategoryID'], errors='coerce'
    )

    # Step 3: Merge with ProductSubcategory to get Subcategory Names
    inventory_with_subcat = pd.merge(
        inventory_merged,
        dataframes['ProductSubcategory'][['ProductSubcategoryID', 'Name']],
        on='ProductSubcategoryID',
        how='left'
    )

    # Step 4: Group by Subcategory Name and sum quantities
    subcategory_summary = inventory_with_subcat.groupby('Name')['Quantity'].sum().reset_index()

    # Step 5: Plot
    plt.figure(figsize=(12, 8))
    sns.barplot(
        data=subcategory_summary.sort_values('Quantity', ascending=False),
        x='Quantity', y='Name',
        palette='viridis'
    )
    plt.title('Inventory Quantity by Product Subcategory')
    plt.xlabel('Quantity')
    plt.ylabel('Product Subcategory')
    plt.tight_layout()
    st.pyplot(plt)
    plt.clf()







def plot_top_products_production_over_time(dataframes):


    # --- Step 1: Load and Validate Required Tables ---
    if 'WorkOrder' not in dataframes or 'Product' not in dataframes:
        st.error("❌ Required tables ('WorkOrder' and 'Product') are missing.")
        return

    workorder = dataframes['WorkOrder']
    product = dataframes['Product']

    # --- Step 2: Merge to Get Product Name ---
    workorder_product = pd.merge(
        workorder,
        product[['ProductID', 'Name']],
        on='ProductID',
        how='left'
    )

    # --- Step 3: Convert StartDate to datetime ---
    workorder_product['StartDate'] = pd.to_datetime(workorder_product['StartDate'], errors='coerce')
    workorder_product.dropna(subset=['StartDate'], inplace=True)

    # --- Step 4: Extract Year and Month ---
    workorder_product['Year'] = workorder_product['StartDate'].dt.year
    workorder_product['Month'] = workorder_product['StartDate'].dt.month

    # --- Step 5: Group and Summarize ---
    produced_summary = workorder_product.groupby(['Year', 'Month', 'Name'])['OrderQty'].sum().reset_index()
    produced_summary.rename(columns={'Name': 'ProductName', 'OrderQty': 'TotalProduced'}, inplace=True)

    # --- Step 6: Filter Top 5 Products ---
    top_products = produced_summary.groupby('ProductName')['TotalProduced'].sum().nlargest(5).index
    filtered = produced_summary[produced_summary['ProductName'].isin(top_products)].copy()

    # --- Step 7: Create YearMonth Column ---
    filtered['YearMonth'] = pd.to_datetime(filtered['Year'].astype(str) + '-' + filtered['Month'].astype(str).str.zfill(2))
    filtered.sort_values(by='YearMonth', inplace=True)

    # --- Step 8: Plot ---
    plt.figure(figsize=(14, 6))
    sns.lineplot(data=filtered, x='YearMonth', y='TotalProduced', hue='ProductName', marker='o')
    plt.title('Total Products Produced Over Time (Top 5 Products)')
    plt.xlabel('Year-Month')
    plt.ylabel('Total Produced')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)
    plt.clf()







def plot_scrap_quantity_by_reason(dataframes):

    # Load required tables
    workorder = dataframes['WorkOrder']
    product = dataframes['Product']
    scrapreason = dataframes['ScrapReason']

    # Merge WorkOrder with Product to get Product Name
    wo_product = pd.merge(workorder, product[['ProductID', 'Name']], on='ProductID', how='left')
    wo_product.rename(columns={'Name': 'ProductName'}, inplace=True)

    # Ensure ScrapReasonID columns are numeric
    wo_product['ScrapReasonID'] = pd.to_numeric(wo_product['ScrapReasonID'], errors='coerce')
    scrapreason['ScrapReasonID'] = pd.to_numeric(scrapreason['ScrapReasonID'], errors='coerce')

    # Merge with ScrapReason to get Scrap Reason Name
    wo_scrap = pd.merge(wo_product, scrapreason[['ScrapReasonID', 'Name']], on='ScrapReasonID', how='left')
    wo_scrap.rename(columns={'Name': 'ScrapReason'}, inplace=True)

    # Filter rows where ScrappedQty > 0
    scrap_data = wo_scrap[wo_scrap['ScrappedQty'] > 0]

    # Summarize scrapped quantity by reason
    scrap_reason_summary = scrap_data.groupby('ScrapReason')['ScrappedQty'].sum().reset_index()

    # Plotting
    plt.figure(figsize=(10, 6))
    sns.barplot(data=scrap_reason_summary.sort_values('ScrappedQty', ascending=False),
                x='ScrappedQty', y='ScrapReason', palette='magma')
    plt.title('Scrapped Quantity by Scrap Reason')
    plt.xlabel('Scrapped Quantity')
    plt.ylabel('Scrap Reason')
    plt.tight_layout()

    # Streamlit display
    st.subheader("🛠️ Scrapped Quantity by Scrap Reason")
    st.pyplot(plt.gcf())
    plt.clf()






def plot_top_subcategories_by_sales_and_production(dataframes):
    # Load tables
    product = dataframes['Product']
    subcategory = dataframes['ProductSubcategory']
    category = dataframes['ProductCategory']
    sales = dataframes['SalesOrderDetail']
    workorder = dataframes['WorkOrder']

    # Ensure numeric keys for safe merging
    product['ProductSubcategoryID'] = pd.to_numeric(product['ProductSubcategoryID'], errors='coerce').astype('Int64')
    subcategory['ProductCategoryID'] = pd.to_numeric(subcategory['ProductCategoryID'], errors='coerce').astype('Int64')
    category['ProductCategoryID'] = pd.to_numeric(category['ProductCategoryID'], errors='coerce').astype('Int64')

    # Merge Product → Subcategory → Category
    prod_sub = pd.merge(product, subcategory, on='ProductSubcategoryID', how='left', suffixes=('', '_sub'))
    prod_sub_cat = pd.merge(prod_sub, category, on='ProductCategoryID', how='left', suffixes=('', '_cat'))

    # Merge with SalesOrderDetail and WorkOrder
    sales_merge = pd.merge(sales, prod_sub_cat[['ProductID', 'Name_sub', 'Name_cat']], on='ProductID', how='left')
    workorder_merge = pd.merge(workorder, prod_sub_cat[['ProductID', 'Name_sub', 'Name_cat']], on='ProductID', how='left')

    # Aggregate sales and production
    sales_summary = (
        sales_merge.groupby(['Name_cat', 'Name_sub'])['OrderQty']
        .sum()
        .reset_index()
        .rename(columns={'Name_cat': 'Category', 'Name_sub': 'SubCategory', 'OrderQty': 'TotalSalesQty'})
    )

    production_summary = (
        workorder_merge.groupby(['Name_cat', 'Name_sub'])['OrderQty']
        .sum()
        .reset_index()
        .rename(columns={'Name_cat': 'Category', 'Name_sub': 'SubCategory', 'OrderQty': 'TotalProducedQty'})
    )

    # Merge summaries
    combined_summary = pd.merge(sales_summary, production_summary, on=['Category', 'SubCategory'], how='outer').fillna(0)
    combined_summary.sort_values('TotalSalesQty', ascending=False, inplace=True)
    top10 = combined_summary.head(10)

    # Plotting
    plt.figure(figsize=(14, 6))
    sns.barplot(data=top10, x='TotalSalesQty', y='SubCategory', hue='Category')
    plt.title('Top 10 Subcategories by Sales Quantity')
    plt.xlabel('Total Sales Quantity')
    plt.ylabel('Subcategory')
    plt.legend(title='Category')
    plt.tight_layout()

    # Show plot in Streamlit
    st.pyplot(plt.gcf())




def plot_top_subcategories_by_production(dataframes):
    # Load tables
    product = dataframes['Product']
    subcategory = dataframes['ProductSubcategory']
    category = dataframes['ProductCategory']
    sales = dataframes['SalesOrderDetail']
    workorder = dataframes['WorkOrder']

    # Ensure numeric keys for safe merging
    product['ProductSubcategoryID'] = pd.to_numeric(product['ProductSubcategoryID'], errors='coerce')
    subcategory['ProductCategoryID'] = pd.to_numeric(subcategory['ProductCategoryID'], errors='coerce')

    # Merge Product → Subcategory → Category
    prod_sub = pd.merge(product, subcategory, on='ProductSubcategoryID', how='left', suffixes=('', '_sub'))
    prod_sub_cat = pd.merge(prod_sub, category, on='ProductCategoryID', how='left', suffixes=('', '_cat'))

    # Merge with SalesOrderDetail and WorkOrder
    sales_merge = pd.merge(sales, prod_sub_cat[['ProductID', 'Name_sub', 'Name_cat']], on='ProductID', how='left')
    workorder_merge = pd.merge(workorder, prod_sub_cat[['ProductID', 'Name_sub', 'Name_cat']], on='ProductID', how='left')

    # Aggregate sales and production
    sales_summary = (
        sales_merge.groupby(['Name_cat', 'Name_sub'])['OrderQty']
        .sum()
        .reset_index()
        .rename(columns={'Name_cat': 'Category', 'Name_sub': 'SubCategory', 'OrderQty': 'TotalSalesQty'})
    )

    production_summary = (
        workorder_merge.groupby(['Name_cat', 'Name_sub'])['OrderQty']
        .sum()
        .reset_index()
        .rename(columns={'Name_cat': 'Category', 'Name_sub': 'SubCategory', 'OrderQty': 'TotalProducedQty'})
    )

    # Merge summaries
    combined_summary = pd.merge(sales_summary, production_summary, on=['Category', 'SubCategory'], how='outer').fillna(0)
    combined_summary.sort_values('TotalProducedQty', ascending=False, inplace=True)
    top10 = combined_summary.head(10)

    # Plotting
    plt.figure(figsize=(14, 6))
    sns.barplot(data=top10, x='TotalProducedQty', y='SubCategory', hue='Category')
    plt.title('Top 10 Subcategories by Production Quantity')
    plt.xlabel('Total Production Quantity')
    plt.ylabel('Subcategory')
    plt.legend(title='Category')
    plt.tight_layout()
    
    # Show plot in Streamlit
    st.pyplot(plt.gcf())



def plot_inventory_delay_correlation(dataframes):
    # Load necessary tables
    product = dataframes['Product']
    inventory = dataframes['ProductInventory']
    sales = dataframes['SalesOrderDetail']
    workorder = dataframes['WorkOrder']
    routing = dataframes['WorkOrderRouting']

    # =====================
    # Step 1: Aggregate Inventory by Product
    # =====================
    inventory_summary = inventory.groupby('ProductID')['Quantity'].sum().reset_index()
    inventory_summary.rename(columns={'Quantity': 'InventoryQty'}, inplace=True)

    # =====================
    # Step 2: Aggregate Sales by Product
    # =====================
    sales_summary = sales.groupby('ProductID')['OrderQty'].sum().reset_index()
    sales_summary.rename(columns={'OrderQty': 'TotalSalesQty'}, inplace=True)

    # =====================
    # Step 3: Compute Delay per Work Order
    # =====================
    workorder_routing = routing.copy()
    workorder_routing['ScheduledEndDate'] = pd.to_datetime(workorder_routing['ScheduledEndDate'], errors='coerce')
    workorder_routing['ActualEndDate'] = pd.to_datetime(workorder_routing['ActualEndDate'], errors='coerce')

    # Calculate delay in days
    workorder_routing['Delay'] = (workorder_routing['ActualEndDate'] - workorder_routing['ScheduledEndDate']).dt.days
    delay_summary = workorder_routing.groupby('ProductID')['Delay'].mean().reset_index()
    delay_summary.rename(columns={'Delay': 'AvgDelayDays'}, inplace=True)

    # =====================
    # Step 4: Merge All Summaries
    # =====================
    combined = product[['ProductID', 'Name']].merge(inventory_summary, on='ProductID', how='left')
    combined = combined.merge(sales_summary, on='ProductID', how='left')
    combined = combined.merge(delay_summary, on='ProductID', how='left')

    # Drop incomplete data
    combined.dropna(subset=['InventoryQty', 'TotalSalesQty', 'AvgDelayDays'], inplace=True)

    # =====================
    # Step 5: Correlation Heatmap
    # =====================
    st.subheader("📊 Correlation: Inventory, Sales & Delays")
    corr = combined[['InventoryQty', 'TotalSalesQty', 'AvgDelayDays']].corr()

    fig1, ax1 = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax1)
    ax1.set_title("Correlation Heatmap")
    st.pyplot(fig1)

    # =====================
    # Step 6: Scatter Plot
    # =====================
    st.subheader("📉 Inventory vs Production Delay (Sales Spike as Size)")
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    scatter = sns.scatterplot(
        data=combined,
        x='InventoryQty',
        y='AvgDelayDays',
        hue='TotalSalesQty',
        size='TotalSalesQty',
        palette='viridis',
        ax=ax2
    )
    ax2.set_title("Inventory vs Avg Production Delay")
    ax2.set_xlabel("Inventory Quantity")
    ax2.set_ylabel("Avg Production Delay (Days)")
    ax2.legend(title='Sales Qty', loc='best', bbox_to_anchor=(1, 1))
    plt.tight_layout()
    st.pyplot(fig2)



def plot_stock_shortages_vs_overstock(dataframes):
    # Load tables
    product = dataframes['Product']
    product_inventory = dataframes['ProductInventory']
    sales_detail = dataframes['SalesOrderDetail']
    work_order = dataframes['WorkOrder']

    # --- Total Inventory Quantity per Product ---
    inventory_qty = product_inventory.groupby('ProductID')['Quantity'].sum().reset_index()
    inventory_qty.rename(columns={'Quantity': 'InventoryQty'}, inplace=True)

    # --- Total Sales Order Quantity per Product ---
    sales_qty = sales_detail.groupby('ProductID')['OrderQty'].sum().reset_index()
    sales_qty.rename(columns={'OrderQty': 'SalesQty'}, inplace=True)

    # --- Total Work Order Quantity per Product ---
    prod_qty = work_order.groupby('ProductID')['OrderQty'].sum().reset_index()
    prod_qty.rename(columns={'OrderQty': 'ProducedQty'}, inplace=True)

    # --- Merge all ---
    df = product[['ProductID', 'Name']].merge(inventory_qty, on='ProductID', how='left') \
                                       .merge(sales_qty, on='ProductID', how='left') \
                                       .merge(prod_qty, on='ProductID', how='left')
    df.fillna(0, inplace=True)

    # --- Add Mismatch Columns ---
    df['Stock_Shortage'] = df['SalesQty'] - df['InventoryQty']
    df['Overstock'] = df['InventoryQty'] - df['SalesQty']

    # --- View sample mismatches ---
    df_mismatch = df[(df['Stock_Shortage'] > 0) | (df['Overstock'] > 0)].copy()

    # =============================
    # 🔴 Top 20 Products with Stock Shortages
    # =============================
    st.subheader("🔴 Top 20 Products with Inventory Shortages")
    top_shortage = df_mismatch.sort_values('Stock_Shortage', ascending=False).head(20)

    fig1, ax1 = plt.subplots(figsize=(10, 8))
    sns.barplot(data=top_shortage, x='Name', y='Stock_Shortage', color='red', ax=ax1)
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
    ax1.set_title("Top 20 Products with Inventory Shortages")
    ax1.set_ylabel("Shortage (SalesQty - InventoryQty)")
    ax1.set_xlabel("Product")
    st.pyplot(fig1)

    # =============================
    # 🟢 Top 20 Products with Overstock
    # =============================
    st.subheader("🟢 Top 20 Products with Overstock")
    top_overstock = df_mismatch.sort_values('Overstock', ascending=False).head(20)

    fig2, ax2 = plt.subplots(figsize=(10, 8))
    sns.barplot(data=top_overstock, x='Name', y='Overstock', color='green', ax=ax2)
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)
    ax2.set_title("Top 20 Products with Overstock")
    ax2.set_ylabel("Overstock (InventoryQty - SalesQty)")
    ax2.set_xlabel("Product")
    st.pyplot(fig2)





def plot_inventory_production_delay_correlation(dataframes):
    # Load tables
    product = dataframes['Product']
    inventory = dataframes['ProductInventory']
    sales = dataframes['SalesOrderDetail']
    work_order = dataframes['WorkOrder']

    # --- Total Inventory Quantity per Product ---
    inventory_qty = inventory.groupby('ProductID')['Quantity'].sum().reset_index()
    inventory_qty.rename(columns={'Quantity': 'InventoryQty'}, inplace=True)

    # --- Total Sales Order Quantity per Product ---
    sales_qty = sales.groupby('ProductID')['OrderQty'].sum().reset_index()
    sales_qty.rename(columns={'OrderQty': 'SalesQty'}, inplace=True)

    # --- Total Work Order Quantity per Product ---
    prod_qty = work_order.groupby('ProductID')['OrderQty'].sum().reset_index()
    prod_qty.rename(columns={'OrderQty': 'ProducedQty'}, inplace=True)

    # --- Merge all ---
    df = product[['ProductID', 'Name']].merge(inventory_qty, on='ProductID', how='left') \
                                       .merge(sales_qty, on='ProductID', how='left') \
                                       .merge(prod_qty, on='ProductID', how='left')
    df.fillna(0, inplace=True)

    # --- Calculate Stock Shortage ---
    df['Stock_Shortage'] = df['SalesQty'] - df['InventoryQty']

    # --- Calculate delay in days (EndDate vs DueDate) ---
    work_order['StartDate'] = pd.to_datetime(work_order['StartDate'])
    work_order['EndDate'] = pd.to_datetime(work_order['EndDate'])
    work_order['DueDate'] = pd.to_datetime(work_order['DueDate'])
    work_order['ProductionDelayDays'] = (work_order['EndDate'] - work_order['DueDate']).dt.days

    # --- Average Delay per Product ---
    delay_summary = work_order.groupby('ProductID')['ProductionDelayDays'].mean().reset_index()

    # --- Merge delay info ---
    df_delay = df.merge(delay_summary, on='ProductID', how='left')
    df_delay.dropna(subset=['ProductionDelayDays'], inplace=True)

    # --- Correlation Matrix ---
    st.subheader("📊 Correlation: Inventory, Sales, Production, Shortage, and Delays")
    corr_cols = ['InventoryQty', 'SalesQty', 'ProducedQty', 'Stock_Shortage', 'ProductionDelayDays']

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(df_delay[corr_cols].corr(), annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
    ax.set_title("Correlation Matrix: Inventory, Sales, and Delays")
    st.pyplot(fig)



def plot_seasonal_inventory_vs_production(dataframes):
    # Load relevant tables
    product_inventory = dataframes['ProductInventory'].copy()
    work_order = dataframes['WorkOrder'].copy()

    # Convert dates
    product_inventory['ModifiedDate'] = pd.to_datetime(product_inventory['ModifiedDate'])
    work_order['StartDate'] = pd.to_datetime(work_order['StartDate'])

    # Monthly Inventory Quantity
    inv_monthly = (
        product_inventory.groupby(product_inventory['ModifiedDate'].dt.to_period('M'))['Quantity']
        .sum()
        .reset_index()
    )
    inv_monthly['Month'] = inv_monthly['ModifiedDate'].dt.to_timestamp()

    # Monthly Production Quantity
    prod_monthly = (
        work_order.groupby(work_order['StartDate'].dt.to_period('M'))['OrderQty']
        .sum()
        .reset_index()
    )
    prod_monthly['Month'] = prod_monthly['StartDate'].dt.to_timestamp()

    # Merge for visualization
    seasonal_df = pd.merge(
        inv_monthly[['Month', 'Quantity']],
        prod_monthly[['Month', 'OrderQty']],
        on='Month',
        how='outer'
    ).fillna(0)

    # --- Plot Inventory vs Production Over Time ---
    st.subheader("📅 Seasonal Pattern: Inventory vs Production Over Time")
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.lineplot(data=seasonal_df, x='Month', y='Quantity', label='Inventory', marker='o', color='orange', ax=ax)
    sns.lineplot(data=seasonal_df, x='Month', y='OrderQty', label='Production', marker='o', color='blue', ax=ax)
    ax.set_title("📅 Inventory vs Production (Monthly)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Quantity")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

    # --- Time Series Decomposition for Inventory ---
    st.subheader("📈 Inventory Seasonality Decomposition")

    series = inv_monthly.set_index('Month')['Quantity'].asfreq('MS').fillna(0)

    try:
        result = seasonal_decompose(series, model='additive')
        fig2 = result.plot()
        fig2.set_size_inches(12, 8)
        st.pyplot(fig2)
    except Exception as e:
        st.warning(f"Time series decomposition failed: {e}")




def plot_sales_by_territory(dataframes):
    # Load tables
    sales_order_header = dataframes['SalesOrderHeader'].copy()
    sales_territory = dataframes.get('SalesTerritory')  # Optional

    # Convert dates
    sales_order_header['OrderDate'] = pd.to_datetime(sales_order_header['OrderDate'])

    # Filter for FY 2014 (July 2013 - June 2014)
    filtered_sales = sales_order_header[
        (sales_order_header['OrderDate'] >= '2013-07-01') &
        (sales_order_header['OrderDate'] <= '2014-06-30')
    ]

    # Group by TerritoryID
    sales_by_territory = (
        filtered_sales.groupby('TerritoryID', dropna=False)['TotalDue']
        .sum()
        .reset_index()
        .rename(columns={'TotalDue': 'TotalSales'})
        .sort_values(by='TotalSales', ascending=False)
    )

    # Optional merge with region names
    if sales_territory is not None:
        sales_by_territory = sales_by_territory.merge(
            sales_territory[['TerritoryID', 'Name']],
            on='TerritoryID',
            how='left'
        )
        sales_by_territory['Region'] = sales_by_territory['Name'].fillna('Unknown')
    else:
        sales_by_territory['Region'] = sales_by_territory['TerritoryID'].fillna('Unknown')

    # Plotting
    st.subheader("🗺️ Total Sales by Territory (Jul 2013 - Jun 2014)")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=sales_by_territory, x='Region', y='TotalSales', palette='Blues_d', ax=ax)
    ax.set_title("🗺️ Total Sales by Territory", fontsize=16)
    ax.set_xlabel("Territory / Region")
    ax.set_ylabel("Total Sales")
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    st.pyplot(fig)


def plot_us_region_sales(conn):
    # Step 1: Load SalesTerritory data
    sales_territory_df = pd.read_sql("SELECT * FROM Sales.SalesTerritory", conn)

    # Step 2: Filter for US Region only
    us_sales = sales_territory_df[sales_territory_df['CountryRegionCode'] == 'US'].copy()
    us_sales['Sales_YTD'] = us_sales['SalesYTD'].round(2)
    us_sales['Sales_LastYear'] = us_sales['SalesLastYear'].round(2)

    # Sort and convert YTD sales to Lakhs (i.e., 1 Lakh = 100,000)
    us_sales_sorted = us_sales.sort_values(by='Sales_YTD', ascending=False)
    us_sales_sorted['Sales_YTD_Lakhs'] = (us_sales_sorted['Sales_YTD'] / 1e5).round(2)

    # Step 3: Visualization
    st.subheader("📊 Sales by US Region (in Lakhs)")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=us_sales_sorted, x='Name', y='Sales_YTD_Lakhs', palette='coolwarm', ax=ax)

    ax.set_title("📊 Sales by US Region (in Lakhs)", fontsize=16)
    ax.set_xlabel("Region Name")
    ax.set_ylabel("Sales YTD (in Lakhs)")
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    st.pyplot(fig)






def plot_sales_by_country(sales_territory_df):


    # Step 1: Group by Country and aggregate sales
    country_sales = (
        sales_territory_df
        .groupby('CountryRegionCode', as_index=False)[['SalesYTD', 'SalesLastYear']]
        .sum()
    )

    # Step 2: Convert to Lakhs
    country_sales['Sales_YTD_Lakhs'] = (country_sales['SalesYTD'] / 1e5).round(2)
    country_sales['Sales_LastYear_Lakhs'] = (country_sales['SalesLastYear'] / 1e5).round(2)

    # Step 3: Sort by Sales_YTD_Lakhs
    country_sales_sorted = country_sales.sort_values(by='Sales_YTD_Lakhs', ascending=False)

    # Step 4: Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=country_sales_sorted, x='CountryRegionCode', y='Sales_YTD_Lakhs', palette='viridis', ax=ax)

    ax.set_title("🌍 Sales by Country (YTD in Lakhs)", fontsize=16)
    ax.set_xlabel("Country Code")
    ax.set_ylabel("Sales YTD (in Lakhs)")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # ✅ Show in Streamlit
    st.pyplot(fig)
