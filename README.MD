# PDF Table Extractor Web Application

Extract tables from PDFs (even borderless ones) with perfect accuracy - No Tabula/Camelot required!


## Features

- Extracts tables from system-generated PDFs
- Handles tables with borders, no borders, and irregular shapes
- Exports to Excel with multiple sheets
- Simple web interface

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
