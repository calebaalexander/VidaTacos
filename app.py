# VidaTacos Analytics Dashboard - Setup Guide

## Repository Structure
```
VidaTacos/
├── .gitignore
├── README.md
├── requirements.txt
├── app.py
└── data/
    └── VidaEnTacos.xlsx
```

## Step-by-Step Setup Commands

```bash
# Clone the repository
git clone https://github.com/yourusername/VidaTacos.git
cd VidaTacos

# Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Create necessary directories and files
mkdir data
touch .gitignore
touch README.md
touch requirements.txt
touch app.py

# Install required packages
pip install streamlit pandas plotly openpyxl numpy

# Generate requirements.txt
pip freeze > requirements.txt

# Initial git commands
git add .
git commit -m "Initial setup: VidaTacos analytics dashboard"
git push origin main
```

## Required Files Content

### .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
.env
venv/
.venv/

# Excel temp files
~$*.xlsx

# OS files
.DS_Store
Thumbs.db
```

### requirements.txt
```
streamlit
pandas
plotly
openpyxl
numpy
```

### README.md
```markdown
# VidaTacos Analytics Dashboard

A Streamlit-based analytics dashboard for Vida en Tacos restaurant, providing insights into sales, menu performance, and employee metrics.

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/VidaTacos.git
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Add data file:
   - Place VidaEnTacos.xlsx in the `data/` directory

5. Run dashboard:
   ```bash
   streamlit run app.py
   ```

## Features
- Interactive Sales Analytics
- Menu Performance Metrics
- Employee Dashboard
- Data Export Capabilities
```
