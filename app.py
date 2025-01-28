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
    layout="wide"
)

@st.cache_data
def load_excel_data():
    try:
        # Read the Excel file
        excel_file = pd.ExcelFile('data/VidaEnTacos.xlsx')
        
        # Load food items - skip first two rows (header and empty row)
        food_items = pd.read_excel(excel_file, 'FoodItems', skiprows=[1])
        # Drop any completely empty rows
        food_items = food_items.dropna(how='all')
        # Remove any rows where FoodItem or Category is null
        food_items = food_items.dropna(subset=['FoodItem', 'Category'])
        
        # Load and process sales data
        def process_sales_sheet(sheet_name, year):
            # Read the sheet
            df = pd.read_excel(excel_file, sheet_name)
            # Find the Total Sales row and get monthly values
            sales_row = df[df.iloc[:, 0] == 'Total Sales'].iloc[0, 1:]
            # Create a DataFrame with months and sales
            monthly_data = pd.DataFrame({
                'Month': ['January', 'February', 'March', 'April', 'May', 'June', 
                         'July', 'August', 'September', 'October', 'November', 'December'],
                'Sales': sales_row.values
            })
            monthly_data['Year'] = year
            return monthly_data
        
        # Process both years
        sales_2023 = process_sales_sheet('Monthly Sales 2023', 2023)
        sales_2024 = process_sales_sheet('Monthly Sales 2024', 2024)
        
        # Combine sales data
        sales_data = pd.concat([sales_2023, sales_2024], ignore_index=True)
        
        # Convert month names to dates for proper sorting
        sales_data['Date'] = pd.to_datetime(sales_data['Month'] + ' ' + sales_data['Year'].astype(str), format='%B %Y')
        
        # Load employees
        try:
            employees = pd.read_excel(excel_file, 'Employees')
            employees = employees.dropna(how='all')  # Remove completely empty rows
        except:
            employees = pd.DataFrame()  # Empty DataFrame if sheet doesn't exist
        
        return food_items, sales_data, employees
        
    except Exception as e:
        st.error(f"Error processing Excel file: {str(e)}")
        return None, None, None

try:
    # Load data
    food_items, sales_data, employees = load_excel_data()
    
    if food_items is not None and sales_data is not None:
        # Title and description
        st.title("🌮 Vida en Tacos Analytics Dashboard")
        
        # Create tabs
        tabs = st.tabs(["Sales Analytics", "Menu Analysis", "Employee Dashboard"])
        
        # Sidebar filters
        st.sidebar.header("Global Filters")
        years = sorted(sales_data['Year'].unique())
        selected_year = st.sidebar.selectbox('Select Year', years, index=len(years)-1)
        
        # Filter sales data by year
        yearly_sales = sales_data[sales_data['Year'] == selected_year].copy()
        
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
                if selected_year > min(years):
                    prev_year_sales = sales_data[sales_data['Year'] == selected_year-1]['Sales'].sum()
                    yoy_growth = ((total_sales - prev_year_sales) / prev_year_sales) * 100
                    st.metric("YoY Growth", f"{yoy_growth:,.1f}%")
                else:
                    st.metric("YoY Growth", "N/A")
            
            with col4:
                peak_month_idx = yearly_sales['Sales'].idxmax()
                st.metric("Peak Month", yearly_sales.loc[peak_month_idx, 'Month'])
            
            # Sales trend
            st.subheader("Monthly Sales Trend")
            fig_trend = px.line(yearly_sales, x='Month', y='Sales',
                              title=f'Monthly Sales Trend - {selected_year}')
            fig_trend.update_layout(xaxis_title="Month", 
                                  yaxis_title="Sales ($)",
                                  yaxis_tickformat='$,.0f')
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Year-over-Year Comparison
            st.subheader("Year-over-Year Comparison")
            fig_yoy = px.line(sales_data, x='Month', y='Sales', color='Year',
                            title='Monthly Sales Comparison Across Years')
            fig_yoy.update_layout(xaxis_title="Month", 
                                yaxis_title="Sales ($)",
                                yaxis_tickformat='$,.0f')
            st.plotly_chart(fig_yoy, use_container_width=True)
            
            # Monthly Growth Analysis
            st.subheader("Monthly Growth Analysis")
            yearly_sales['Monthly Growth'] = yearly_sales['Sales'].pct_change() * 100
            fig_growth = px.bar(yearly_sales.dropna(), x='Month', y='Monthly Growth',
                              title=f'Month-over-Month Growth Rate - {selected_year}')
            fig_growth.update_layout(yaxis_title="Growth Rate (%)")
            st.plotly_chart(fig_growth, use_container_width=True)
        
        # Tab 2: Menu Analysis
        with tabs[1]:
            st.header("Menu Analytics")
            
            # Category filter
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
                category_data = food_items['Category'].value_counts().reset_index()
                category_data.columns = ['Category', 'Count']
                
                fig_categories = px.pie(category_data, values='Count', names='Category',
                                      title='Menu Items by Category')
                st.plotly_chart(fig_categories, use_container_width=True)
            
            with col2:
                st.subheader("Price Distribution")
                fig_prices = px.histogram(food_items, x='Price',
                                        title='Price Distribution of Menu Items',
                                        nbins=20)
                fig_prices.update_layout(xaxis_title="Price ($)",
                                       yaxis_title="Count",
                                       xaxis_tickformat='$,.2f')
                st.plotly_chart(fig_prices, use_container_width=True)
            
            # Menu items table
            st.subheader("Menu Items")
            if selected_category != 'All':
                filtered_menu = food_items[food_items['Category'] == selected_category]
            else:
                filtered_menu = food_items
            
            st.dataframe(filtered_menu.style.format({'Price': '${:.2f}'}),
                        use_container_width=True)
        
        # Tab 3: Employee Dashboard
        with tabs[2]:
            st.header("Employee Analytics")
            
            if not employees.empty:
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
                if 'Position' in employees.columns:
                    st.subheader("Employees by Position")
                    position_data = employees['Position'].value_counts()
                    fig_positions = px.pie(values=position_data.values, names=position_data.index,
                                         title='Employee Distribution by Position')
                    st.plotly_chart(fig_positions, use_container_width=True)
                
                # Employee table
                st.subheader("Employee Directory")
                st.dataframe(employees, use_container_width=True)
            else:
                st.info("No employee data available")
        
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
        The app expects an Excel file named 'VidaEnTacos.xlsx' in the data/ directory with the following sheets:
        1. FoodItems:
           - FoodItem (name)
           - Category
           - Vegetarian Option?
           - Price
        
        2. Monthly Sales 2023/2024:
           - Columns for each month (January through December)
           - Total Sales row with monthly values
           
        3. Employees:
           - Employee information including Position, Start Date, etc.
    """)
