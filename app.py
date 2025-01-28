import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import openpyxl

# Set page configuration
st.set_page_config(
    page_title="Vida en Tacos Analytics",
    page_icon="🌮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .st-tabs {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_excel_data():
    # Read the Excel file
    excel_file = pd.ExcelFile('data/VidaEnTacos.xlsx')
    
    # Load all sheets
    food_items = pd.read_excel(excel_file, 'FoodItems')
    sales_2023 = pd.read_excel(excel_file, 'Monthly Sales 2023')
    sales_2024 = pd.read_excel(excel_file, 'Monthly Sales 2024')
    employees = pd.read_excel(excel_file, 'Employees')
    
    # Process sales data
    def process_sales_data(df, year):
        melted = pd.melt(df, id_vars=[], var_name='Month', value_name='Sales')
        melted = melted[melted['Month'] != 'Unnamed: 0']
        melted['Date'] = pd.to_datetime(melted['Month'] + ' ' + str(year), format='%B %Y')
        return melted

    sales_2023 = process_sales_data(sales_2023, 2023)
    sales_2024 = process_sales_data(sales_2024, 2024)
    sales_data = pd.concat([sales_2023, sales_2024])
    
    return food_items, sales_data, employees

try:
    # Load data
    food_items, sales_data, employees = load_excel_data()
    
    # Title and description
    st.title("🌮 Vida en Tacos Analytics Dashboard")
    
    # Create tabs for different sections
    tabs = st.tabs(["Sales Analytics", "Menu Analysis", "Employee Dashboard"])
    
    # Sidebar filters
    st.sidebar.header("Global Filters")
    years = sorted(sales_data['Date'].dt.year.unique())
    selected_year = st.sidebar.selectbox('Select Year', years, index=len(years)-1)
    
    # Filter sales data by year
    yearly_sales = sales_data[sales_data['Date'].dt.year == selected_year]
    
    # Tab 1: Sales Analytics
    with tabs[0]:
        st.header("Sales Performance")
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_sales = yearly_sales['Sales'].sum()
            st.metric("Total Sales", f"${total_sales:,.2f}")
        
        with col2:
            avg_monthly_sales = yearly_sales['Sales'].mean()
            st.metric("Avg Monthly Sales", f"${avg_monthly_sales:,.2f}")
        
        with col3:
            yoy_growth = None
            if selected_year > min(years):
                prev_year_sales = sales_data[sales_data['Date'].dt.year == selected_year-1]['Sales'].sum()
                yoy_growth = ((total_sales - prev_year_sales) / prev_year_sales) * 100
                st.metric("YoY Growth", f"{yoy_growth:,.1f}%")
            else:
                st.metric("YoY Growth", "N/A")
        
        with col4:
            peak_month = yearly_sales.loc[yearly_sales['Sales'].idxmax()]
            st.metric("Peak Month", f"{peak_month['Month']}")
        
        # Sales trend
        st.subheader("Monthly Sales Trend")
        fig_trend = px.line(yearly_sales, x='Date', y='Sales',
                          title=f'Monthly Sales Trend - {selected_year}')
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Year-over-Year Comparison
        st.subheader("Year-over-Year Comparison")
        pivot_sales = sales_data.pivot(index='Month', columns=sales_data['Date'].dt.year, values='Sales')
        
        fig_yoy = go.Figure()
        for year in pivot_sales.columns:
            fig_yoy.add_trace(go.Scatter(
                x=pivot_sales.index,
                y=pivot_sales[year],
                name=str(year),
                mode='lines+markers'
            ))
        
        fig_yoy.update_layout(
            title='Monthly Sales Comparison Across Years',
            xaxis_title='Month',
            yaxis_title='Sales ($)',
            hovermode='x unified'
        )
        st.plotly_chart(fig_yoy, use_container_width=True)
    
    # Tab 2: Menu Analysis
    with tabs[1]:
        st.header("Menu Analytics")
        
        # Category filter for menu
        categories = ['All'] + sorted(food_items['Category'].unique().tolist())
        selected_category = st.selectbox('Select Category', categories)
        
        # Menu metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_items = len(food_items)
            st.metric("Total Menu Items", total_items)
        
        with col2:
            veg_percentage = (food_items['Vegetarian Option?'] == 'Yes').mean() * 100
            st.metric("Vegetarian Options", f"{veg_percentage:.1f}%")
        
        with col3:
            avg_price = food_items['Price'].mean()
            st.metric("Average Price", f"${avg_price:.2f}")
        
        # Menu visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Menu Categories")
            category_data = food_items.groupby('Category').size().reset_index()
            category_data.columns = ['Category', 'Count']
            
            fig_categories = px.pie(category_data, values='Count', names='Category',
                                  title='Menu Items by Category')
            st.plotly_chart(fig_categories, use_container_width=True)
        
        with col2:
            st.subheader("Price Distribution")
            fig_prices = px.histogram(food_items, x='Price',
                                    title='Price Distribution of Menu Items',
                                    nbins=20)
            st.plotly_chart(fig_prices, use_container_width=True)
        
        # Menu items table
        st.subheader("Menu Items")
        if selected_category != 'All':
            filtered_menu = food_items[food_items['Category'] == selected_category]
        else:
            filtered_menu = food_items
        
        st.dataframe(
            filtered_menu.style.format({
                'Price': '${:.2f}'
            }),
            use_container_width=True
        )
    
    # Tab 3: Employee Dashboard
    with tabs[2]:
        st.header("Employee Analytics")
        
        # Employee metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_employees = len(employees)
            st.metric("Total Employees", total_employees)
        
        with col2:
            if 'Position' in employees.columns:
                positions = len(employees['Position'].unique())
                st.metric("Different Positions", positions)
        
        with col3:
            if 'Start Date' in employees.columns:
                avg_tenure = (pd.Timestamp.now() - pd.to_datetime(employees['Start Date'])).mean()
                st.metric("Average Tenure", f"{avg_tenure.days / 365:.1f} years")
        
        # Employee visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Position' in employees.columns:
                st.subheader("Employees by Position")
                position_data = employees.groupby('Position').size().reset_index()
                position_data.columns = ['Position', 'Count']
                
                fig_positions = px.pie(position_data, values='Count', names='Position',
                                     title='Employee Distribution by Position')
                st.plotly_chart(fig_positions, use_container_width=True)
        
        with col2:
            if 'Start Date' in employees.columns:
                st.subheader("Employee Tenure Distribution")
                employees['Tenure'] = (pd.Timestamp.now() - pd.to_datetime(employees['Start Date'])).dt.days / 365
                fig_tenure = px.histogram(employees, x='Tenure',
                                        title='Employee Tenure Distribution (Years)',
                                        nbins=10)
                st.plotly_chart(fig_tenure, use_container_width=True)
        
        # Employee table
        st.subheader("Employee Directory")
        if 'Salary' in employees.columns:
            employees_display = employees.style.format({
                'Salary': '${:,.2f}',
                'Tenure': '{:.1f} years'
            })
        else:
            employees_display = employees
        
        st.dataframe(employees_display, use_container_width=True)
    
    # Download options in sidebar
    st.sidebar.markdown("### Download Data")
    
    # Sales data download
    sales_csv = yearly_sales.to_csv(index=False)
    st.sidebar.download_button(
        label="Download Sales Data",
        data=sales_csv,
        file_name=f"vida_en_tacos_sales_{selected_year}.csv",
        mime="text/csv",
    )
    
    # Menu data download
    menu_csv = food_items.to_csv(index=False)
    st.sidebar.download_button(
        label="Download Menu Data",
        data=menu_csv,
        file_name="vida_en_tacos_menu.csv",
        mime="text/csv",
    )

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.markdown("""
        ### Expected Excel Structure:
        The app expects an Excel file named 'VidaEnTacos.xlsx' with the following sheets:
        1. FoodItems:
           - FoodItem (name)
           - Category
           - Vegetarian Option?
           - Price
        
        2. Monthly Sales 2023/2024:
           - Columns for each month (January through December)
           - Sales data in rows
           
        3. Employees:
           - Employee information including Position, Start Date, etc.
    """)
