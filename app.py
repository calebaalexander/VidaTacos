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
        # Read all sheets from Excel file
        excel_file = pd.ExcelFile('data/VidaEnTacos.xlsx')
        
        # Load monthly sales data with specific structure
        def load_sales_sheet(year):
            sheet_name = f'Monthly Sales {year}'
            df = pd.read_excel(excel_file, sheet_name, header=0)
            # Get the row with Total Sales
            sales_row = df[df.iloc[:, 0] == 'Total Sales'].iloc[0]
            # Convert to monthly data
            monthly_data = pd.Series(sales_row.values[1:], 
                                   index=['January', 'February', 'March', 'April', 'May', 'June',
                                         'July', 'August', 'September', 'October', 'November', 'December'])
            return monthly_data

        # Load sales data for both years
        sales_2024 = load_sales_sheet(2024)
        sales_2023 = load_sales_sheet(2023)
        
        # Load employee data
        employees = pd.read_excel(excel_file, 'Employees')
        
        # Process item data from ItemCode sheet
        items_monthly = pd.read_excel(excel_file, 'Monthly Sales 2024', skiprows=3)
        items_monthly = items_monthly[items_monthly['ItemName'].notna()]

        return sales_2024, sales_2023, employees, items_monthly
        
    except Exception as e:
        st.error(f"Error processing Excel file: {str(e)}")
        return None, None, None, None

try:
    # Load data
    sales_2024, sales_2023, employees, items_monthly = load_excel_data()
    
    if sales_2024 is not None:
        # Title
        st.title("🌮 Vida en Tacos Analytics Dashboard")
        
        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Sales Analytics", "Menu Analysis", 
                                         "Employee Analytics", "Financial Metrics"])
        
        # Tab 1: Sales Analytics
        with tab1:
            st.header("Sales Performance")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_sales = sales_2024.sum()
                st.metric("Total Sales", f"${total_sales:,.2f}")
            
            with col2:
                avg_monthly = sales_2024.mean()
                st.metric("Average Monthly Sales", f"${avg_monthly:,.2f}")
            
            with col3:
                max_month = sales_2024.idxmax()
                max_sales = sales_2024.max()
                st.metric("Peak Month", f"{max_month}", f"${max_sales:,.2f}")
            
            with col4:
                yoy_growth = ((sales_2024.sum() - sales_2023.sum()) / sales_2023.sum() * 100)
                st.metric("YoY Growth", f"{yoy_growth:.1f}%")
            
            # Sales trends
            st.subheader("Monthly Sales Trends")
            
            # Create monthly comparison chart
            fig = go.Figure()
            
            # Add 2024 data
            fig.add_trace(go.Scatter(
                x=sales_2024.index,
                y=sales_2024.values,
                name='2024',
                line=dict(color='#1f77b4')
            ))
            
            # Add 2023 data
            fig.add_trace(go.Scatter(
                x=sales_2023.index,
                y=sales_2023.values,
                name='2023',
                line=dict(color='#ff7f0e')
            ))
            
            fig.update_layout(
                title='Monthly Sales Comparison',
                xaxis_title='Month',
                yaxis_title='Sales ($)',
                yaxis_tickformat='$,.0f',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Monthly Growth Analysis
            st.subheader("Monthly Growth Analysis")
            monthly_growth = sales_2024.pct_change() * 100
            
            fig_growth = px.bar(
                x=monthly_growth.index[1:],  # Skip first month as it has no growth rate
                y=monthly_growth[1:],
                title='Month-over-Month Growth Rate (2024)',
                labels={'x': 'Month', 'y': 'Growth Rate (%)'}
            )
            
            st.plotly_chart(fig_growth, use_container_width=True)

        # Tab 2: Menu Analysis
        with tab2:
            st.header("Menu Analytics")
            
            if items_monthly is not None:
                # Category performance
                category_totals = items_monthly.groupby('Category')['Total Items'].sum()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Sales by Category")
                    fig_cat = px.pie(values=category_totals.values,
                                   names=category_totals.index,
                                   title='Items Sold by Category')
                    st.plotly_chart(fig_cat, use_container_width=True)
                
                with col2:
                    st.subheader("Top Selling Items")
                    top_items = items_monthly.nlargest(10, 'Total Items')
                    fig_top = px.bar(top_items,
                                   x='ItemName',
                                   y='Total Items',
                                   title='Top 10 Items by Sales Volume')
                    fig_top.update_layout(xaxis_tickangle=45)
                    st.plotly_chart(fig_top, use_container_width=True)

        # Tab 3: Employee Analytics
        with tab3:
            st.header("Employee Analytics")
            
            if employees is not None:
                # Employee metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_employees = len(employees)
                    full_time = len(employees[employees['Full/Part Time'] == 'Full'])
                    st.metric("Total Staff", total_employees,
                             f"{full_time} Full-time")
                
                with col2:
                    avg_hourly = employees['Hourly'].mean()
                    st.metric("Average Hourly Rate", f"${avg_hourly:.2f}")
                
                with col3:
                    total_hours = employees['WeeklyHours'].sum()
                    st.metric("Total Weekly Hours", f"{total_hours:,.0f}")
                
                # Role distribution
                st.subheader("Staff Role Distribution")
                role_dist = px.pie(employees,
                                 names='Role',
                                 title='Employees by Role')
                st.plotly_chart(role_dist, use_container_width=True)
                
                # Payroll analysis
                employees['Weekly Pay'] = employees['Hourly'] * employees['WeeklyHours']
                st.subheader("Weekly Payroll by Role")
                payroll_by_role = employees.groupby('Role')['Weekly Pay'].sum()
                fig_payroll = px.bar(x=payroll_by_role.index,
                                   y=payroll_by_role.values,
                                   title='Weekly Payroll Distribution')
                fig_payroll.update_layout(xaxis_title='Role',
                                        yaxis_title='Weekly Pay ($)',
                                        yaxis_tickformat='$,.0f')
                st.plotly_chart(fig_payroll, use_container_width=True)

        # Tab 4: Financial Metrics
        with tab4:
            st.header("Financial Analytics")
            
            # Calculate financial metrics
            if employees is not None:
                weekly_payroll = employees['Weekly Pay'].sum()
                monthly_payroll = weekly_payroll * 4
                monthly_sales = sales_2024.mean()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    labor_cost = (monthly_payroll / monthly_sales) * 100
                    st.metric("Labor Cost %", f"{labor_cost:.1f}%")
                
                with col2:
                    total_hours = employees['WeeklyHours'].sum() * 4
                    sales_per_hour = monthly_sales / total_hours
                    st.metric("Sales per Labor Hour", f"${sales_per_hour:.2f}")
                
                with col3:
                    st.metric("Monthly Labor Cost", f"${monthly_payroll:,.2f}")

except Exception as e:
    st.error(f"Dashboard Error: {str(e)}")
    st.markdown("""
        ### Dashboard Requirements:
        1. Excel file named 'VidaEnTacos.xlsx' in the data/ directory with:
           - Monthly sales data
           - Employee information
           - Menu items and categories
        2. Proper data structure in each sheet
    """)
