PDF Table Extractor - Setup and Execution Guide
Step 1:- 
Install Python 3.7+ from python.org


Step 2: Download the Project
Open Command Prompt/Terminal

Clone the repository:

git clone https://github.com/yourusername/pdf-table-extractor.git


Step 3: Set Up Virtual Environment (Recommended)
Create virtual environment:

python -m venv venv
Activate environment:

venv\Scripts\activate


Step 4: Install Dependencies
Install required packages:

pip install -r requirements.txt
OR pip install flask
pdfplumber
pandas
openpyxl
python-dotenv


Step 5: Run the Application
Start the Flask server:

python app.py
You should see output similar to:

* Running on http://127.0.0.1:5000/

Step 6: Access the Web Interface
Open your web browser

Visit:

http://localhost:5000
