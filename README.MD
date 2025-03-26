# PDF Table Extractor Web Application

Extract tables from PDFs (even borderless ones) with perfect accuracy - No Tabula/Camelot required!


## Features

- Extracts tables from system-generated PDFs
- Handles tables with borders, no borders, and irregular shapes
- Exports to Excel with multiple sheets
- Simple web interface

Installation
Prerequisites
Python 3.7+

pip package manage
# Clone the repository
git clone https://github.com/yourusername/pdf-table-extractor.git
cd pdf-table-extractor

# Create virtual environment (recommended)
python -m venv venv

# Activate environment
# On Windows:
venv\Scripts\activate


# Install dependencies
pip install -flask
pdfplumber
pandas
openpyxl
python-dotenv
-> python app.py
Start the application:

Open your browser to:

Upload a PDF file and download the extracted tables as Excel

How It Works
PDF Parsing: Uses pdfplumber to extract text with precise positioning

Space Analysis: Identifies columns by analyzing consistent whitespace patterns

Structure Detection: Groups text into rows based on vertical alignment

Excel Export: Formats the data into properly structured Excel sheets


Project Structure
/pdf-table-extractor
├── app.py              # Main application logic
├── requirements.txt    # Python dependencies
├── uploads/            # Temporary file storage
├── static/             # Static assets (CSS/JS)
└── templates/          # HTML templates
