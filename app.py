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
        def load_sales_sheet(sheet_name):
            # Read the sheet
            df = pd.read_excel(excel_file, sheet_name)
            # Get the Total Sales row
            sales_row = df[df.iloc[:, 0] == 'Total Sales'].iloc[0]
            # Remove the 'Total Sales' label from the first column
            sales_values = sales_row[1:].values
            # Create a series with the correct months
            months = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']
            return pd.Series(data=sales_values, index=months)

        # Load sales data for both years
        sales_2024 = load_sales_sheet('Monthly Sales 2024')
        sales_2023 = load_sales_sheet('Monthly Sales 2023')
        
        # Load employee data
        employees = pd.read_excel(excel_file, 'Employees')
        
        # Load item sales data starting from the ItemCode row
        items_data = pd.read_excel(excel_file, 'Monthly Sales 2024', skiprows=3)
        items_data = items_data[items_data['ItemCode'].notna()]
        
        return sales_2024, sales_2023, employees, items_data
        
    except Exception as e:
        st.error(f"Error processing Excel file: {str(e)}")
        st.write("Detailed error info:", str(e))
        return None, None, None, None

# Rest of the dashboard code remains the same...
