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
        
        # Load monthly sales data
        sales_data = pd.read_excel(excel_file, 'Monthly Sales 2024')
        
        # Load item sales data
        items_data = pd.DataFrame({
            'ItemCode': ['APP001', 'APP002', 'APP003', 'APP004', 'APP005', 
                        'TAC001', 'TAC002', 'TAC003', 'TAC004', 'TAC005',
                        'ENT001', 'ENT002', 'ENT003', 'ENT004', 'ENT005',
                        'SID001', 'SID002', 'SID003', 'SID004',
                        'DES001', 'DES002', 'DES003', 'DES004',
                        'BEER001', 'BEER002', 'BEER003', 'BEER004',
                        'LIQ001', 'LIQ002', 'LIQ003', 'LIQ004', 'LIQ005'],
            'ItemName': ['Chips and Guacamole', 'Chips and Salsa Trio', 'Elote', 'Queso Fundido', 'Taquitos',
                        'Al Pastor', 'Carne Asada', 'Pollo Tinga', 'Baja Fish Tacos', 'Vegetarian Tacos',
                        'Chicken Mole', 'Beef Barbacoa', 'Carnitas', 'Enchiladas Suizas', 'Chile Rellenos',
                        'Mexican Rice', 'Refried Beans', 'Black Beans', 'Nopalitos Salad',
                        'Churros', 'Tres Leches', 'Flan', 'Sopapillas',
                        'Modelo Especial', 'Pacifico', 'Negra Modelo', 'Corona Extra',
                        'Margarita', 'Paloma', 'Tequila Sunrise', 'Mezcal Mule', 'Horchata Colada'],
            'Category': ['Appetizer', 'Appetizer', 'Appetizer', 'Appetizer', 'Appetizer',
                        'Tacos', 'Tacos', 'Tacos', 'Tacos', 'Tacos',
                        'Entrees', 'Entrees', 'Entrees', 'Entrees', 'Entrees',
                        'Sides', 'Sides', 'Sides', 'Sides',
                        'Desserts', 'Desserts', 'Desserts', 'Desserts',
                        'Beer', 'Beer', 'Beer', 'Beer',
                        'Cocktails', 'Cocktails', 'Cocktails', 'Cocktails', 'Cocktails']
        })
        
        # Load employee data
        employees = pd.DataFrame({
            'FirstName': ['Maria', 'Carlos', 'Kerry', 'Diego', 'Isabella', 'Jeremy', 'Ella', 
                         'Miguel', 'Ana', 'Rafael', 'Lucy', 'Matt', 'Gabriela'],
            'LastName': ['Gonzalez', 'Martinez', 'Lopez', 'Hernandez', 'Garcia', 'Rodriguez',
                        'Perez', 'Sanchez', 'Ramirez', 'Torres', 'Vasquez', 'Morales', 'Gutierrez'],
            'Hourly': [15.5, 17.5, 16, 17.5, 15.5, 15.5, 15.5, 17.5, 15.5, 16, 17.5, 15.5, 22],
            'Role': ['Server', 'Line Cook', 'Porter', 'Line Cook', 'Server', 'Server', 'Server',
                    'Line Cook', 'Bartender', 'Host', 'Line Cook', 'Bartender', 'Manager'],
            'Full/Part Time': ['Part', 'Full', 'Full', 'Full', 'Part', 'Full', 'Part',
                             'Full', 'Part', 'Full', 'Part', 'Full', 'Full'],
            'WeeklyHours': [24, 40, 40, 40, 32, 40, 8, 40, 24, 40, 32, 40, 40]
        })
        
        return sales_data, items_data, employees
        
    except Exception as e:
        st.error(f"Error processing Excel file: {str(e)}")
        return None, None, None

try:
    # Load data
    sales_data, items_data, employees = load_excel_data()
    
    if sales_data is not None and items_data is not None:
        # Title and description
        st.title("🌮 Vida en Tacos Analytics Dashboard")
        
        # Create tabs
        tabs = st.tabs(["Sales Analytics", "Menu Analysis", "Employee Analytics", "Financial Metrics"])
        
        # Tab 1: Sales Analytics
        with tabs[0]:
            st.header("Sales Performance")
            
            # Key metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            # Calculate metrics
            total_sales = sales_data.iloc[0]['Total Sales']
            avg_daily_sales = sales_data.iloc[1]['Average Daily Sales']
            total_items = sales_data.iloc[2]['Total Items Sold']
            avg_orders = sales_data.iloc[3]['Average Daily Orders']
            
            with col1:
                st.metric("Total Sales", f"${total_sales:,.2f}")
            with col2:
                st.metric("Average Daily Sales", f"${avg_daily_sales:,.2f}")
            with col3:
                st.metric("Total Items Sold", f"{total_items:,.0f}")
            with col4:
                st.metric("Average Daily Orders", f"{avg_orders:,.0f}")
            
            # Sales trend visualization
            st.subheader("Monthly Performance Metrics")
            sales_trend = go.Figure()
            
            # Add traces for each metric
            sales_trend.add_trace(go.Scatter(
                name="Total Sales",
                x=sales_data.columns[1:],
                y=sales_data.iloc[0, 1:],
                yaxis="y",
                line=dict(color="#1f77b4")
            ))
            
            sales_trend.add_trace(go.Scatter(
                name="Total Items",
                x=sales_data.columns[1:],
                y=sales_data.iloc[2, 1:],
                yaxis="y2",
                line=dict(color="#ff7f0e")
            ))
            
            sales_trend.update_layout(
                title="Sales and Items Sold Trends",
                yaxis=dict(title="Sales ($)", side="left", showgrid=False),
                yaxis2=dict(title="Items Sold", side="right", overlaying="y", showgrid=False),
                hovermode="x unified"
            )
            
            st.plotly_chart(sales_trend, use_container_width=True)
        
        # Tab 2: Menu Analysis
        with tabs[1]:
            st.header("Menu Analytics")
            
            # Category distribution
            category_dist = items_data['Category'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Menu Category Distribution")
                fig_cat = px.pie(values=category_dist.values, 
                               names=category_dist.index,
                               title="Items by Category")
                st.plotly_chart(fig_cat, use_container_width=True)
            
            with col2:
                st.subheader("Category Performance")
                # Add category performance metrics here
                
            # Item sales analysis
            st.subheader("Item Sales Analysis")
            # Add detailed item sales analysis here
        
        # Tab 3: Employee Analytics
        with tabs[2]:
            st.header("Employee Analytics")
            
            # Employee metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_employees = len(employees)
                full_time = len(employees[employees['Full/Part Time'] == 'Full'])
                st.metric("Total Employees", total_employees, 
                         f"{full_time} Full-time")
            
            with col2:
                avg_hourly = employees['Hourly'].mean()
                st.metric("Average Hourly Rate", f"${avg_hourly:.2f}")
            
            with col3:
                total_weekly_hours = employees['WeeklyHours'].sum()
                st.metric("Total Weekly Hours", f"{total_weekly_hours:,.0f}")
            
            # Role distribution
            st.subheader("Staff Role Distribution")
            role_dist = px.pie(employees, names='Role', title="Employees by Role")
            st.plotly_chart(role_dist, use_container_width=True)
            
            # Payroll analysis
            st.subheader("Weekly Payroll Analysis")
            employees['Weekly Pay'] = employees['Hourly'] * employees['WeeklyHours']
            payroll_by_role = employees.groupby('Role')['Weekly Pay'].sum().reset_index()
            
            fig_payroll = px.bar(payroll_by_role, x='Role', y='Weekly Pay',
                                title="Weekly Payroll by Role")
            fig_payroll.update_layout(yaxis_title="Weekly Pay ($)")
            st.plotly_chart(fig_payroll, use_container_width=True)
            
            # Employee schedule overview
            st.subheader("Employee Schedule Overview")
            schedule_data = employees[['FirstName', 'LastName', 'Role', 'WeeklyHours', 'Full/Part Time']]
            st.dataframe(schedule_data.style.format({'WeeklyHours': '{:.0f}'}))
        
        # Tab 4: Financial Metrics
        with tabs[3]:
            st.header("Financial Analytics")
            
            # Calculate labor costs
            total_weekly_payroll = (employees['Hourly'] * employees['WeeklyHours']).sum()
            monthly_payroll = total_weekly_payroll * 4
            
            # Financial metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                labor_cost_pct = (monthly_payroll / total_sales) * 100
                st.metric("Labor Cost %", f"{labor_cost_pct:.1f}%")
            
            with col2:
                avg_ticket = total_sales / avg_orders
                st.metric("Average Ticket", f"${avg_ticket:.2f}")
            
            with col3:
                sales_per_labor_hour = total_sales / (total_weekly_hours * 4)
                st.metric("Sales per Labor Hour", f"${sales_per_labor_hour:.2f}")
            
            # Financial trends
            st.subheader("Financial Trends")
            # Add financial trend visualizations here

except Exception as e:
    st.error(f"Error in dashboard: {str(e)}")
    st.markdown("""
        ### Dashboard Requirements:
        1. Excel file named 'VidaEnTacos.xlsx' in the data/ directory with:
           - Monthly sales data
           - Employee information
           - Menu items and categories
        2. Proper data structure in each sheet
    """)
