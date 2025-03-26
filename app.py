import os
import re
from flask import Flask, render_template, request, send_file, jsonify
import pdfplumber
import pandas as pd
from werkzeug.utils import secure_filename
from collections import defaultdict

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_tables_with_spaces(pdf_path):
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract words with precise positioning
            words = page.extract_words(
                x_tolerance=2,
                y_tolerance=2,
                keep_blank_chars=False,
                use_text_flow=False,
                extra_attrs=["fontname", "size"]
            )
            
            if not words:
                continue
                
            # Group words into lines based on vertical alignment
            lines = defaultdict(list)
            for word in words:
                # Use rounded y-position to group words into lines
                line_key = round(word['top'] * 10) / 10  # Group with 0.1 precision
                lines[line_key].append(word)
            
            # Sort lines vertically and process each line
            sorted_lines = sorted(lines.items(), key=lambda x: x[0])
            all_lines = [line[1] for line in sorted_lines]
            
            # Detect column boundaries from all lines
            column_boundaries = detect_column_boundaries(all_lines)
            
            # Detect row boundaries (using original line groupings)
            row_boundaries = [line[0] for line in sorted_lines]
            
            # Reconstruct table
            table = []
            for line_words in all_lines:
                row = reconstruct_row(line_words, column_boundaries)
                if any(cell.strip() for cell in row):  # Skip empty rows
                    table.append(row)
            
            if len(table) > 1:  # Require at least 2 rows
                tables.append(table)
    
    return tables

def detect_column_boundaries(all_lines):
    """Analyze all lines to detect common column boundaries"""
    boundary_candidates = defaultdict(int)
    
    for line in all_lines:
        if len(line) < 2:
            continue
            
        # Sort words left to right
        line_sorted = sorted(line, key=lambda x: x['x0'])
        
        # Analyze gaps between words
        for i in range(1, len(line_sorted)):
            prev_word = line_sorted[i-1]
            current_word = line_sorted[i]
            gap = current_word['x0'] - prev_word['x1']
            
            if gap > 5:  # Minimum gap to consider as column separator
                # Use weighted position between words
                boundary_pos = (prev_word['x1'] + current_word['x0']) / 2
                rounded_pos = round(boundary_pos)
                boundary_candidates[rounded_pos] += 1
    
    # Filter boundaries that appear in at least 25% of lines
    min_count = max(2, len(all_lines) * 0.25)
    strong_boundaries = [pos for pos, count in boundary_candidates.items() 
                        if count >= min_count]
    strong_boundaries.sort()
    
    # Merge nearby boundaries
    if not strong_boundaries:
        return []
    
    merged_boundaries = [strong_boundaries[0]]
    for pos in strong_boundaries[1:]:
        last_pos = merged_boundaries[-1]
        if pos - last_pos < 10:  # Merge if closer than 10 units
            # Weighted average based on occurrence count
            merged_pos = (last_pos * boundary_candidates[last_pos] + 
                         pos * boundary_candidates[pos]) / \
                        (boundary_candidates[last_pos] + boundary_candidates[pos])
            merged_boundaries[-1] = round(merged_pos)
        else:
            merged_boundaries.append(pos)
    
    return merged_boundaries

def reconstruct_row(words, column_boundaries):
    """Assign words to columns based on boundaries"""
    # Sort words left to right
    words_sorted = sorted(words, key=lambda x: x['x0'])
    
    # Initialize empty cells
    row = [""] * (len(column_boundaries) + 1)
    
    for word in words_sorted:
        word_center = (word['x0'] + word['x1']) / 2
        col_idx = 0
        
        # Find appropriate column
        for boundary in column_boundaries:
            if word_center > boundary:
                col_idx += 1
            else:
                break
        
        # Add space between words in same cell
        if row[col_idx]:
            row[col_idx] += " "
        row[col_idx] += word['text']
    
    return row

def is_likely_header(row, next_row):
    """Check if a row is likely a header row"""
    if not row or not next_row:
        return False
    
    # Check if row has mostly text while next row has data
    text_pattern = re.compile(r'[a-zA-Z]')
    num_text_cells = sum(1 for cell in row if text_pattern.search(cell))
    num_next_row_text = sum(1 for cell in next_row if text_pattern.search(cell))
    
    return num_text_cells > len(row)/2 and num_next_row_text < len(next_row)/2

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            tables = extract_tables_with_spaces(filepath)
            
            if not tables:
                return jsonify({'error': 'No tables found in the PDF'}), 400
            
            excel_filename = filename.replace('.pdf', '.xlsx')
            excel_path = os.path.join(app.config['UPLOAD_FOLDER'], excel_filename)
            
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                for i, table in enumerate(tables):
                    # Auto-detect headers
                    header = 0 if len(table) > 1 and is_likely_header(table[0], table[1]) else None
                    
                    df = pd.DataFrame(table[1:] if header == 0 else table)
                    
                    if header == 0:
                        df.columns = [str(col).strip() for col in table[0]]
                    
                    # Clean column names
                    df.columns = [re.sub(r'\s+', ' ', str(col)).strip() for col in df.columns]
                    
                    sheet_name = f'Table_{i+1}'[:31]  # Excel sheet name limit
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            return jsonify({
                'success': True,
                'excel_file': excel_filename,
                'tables_count': len(tables)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(
        os.path.join(app.config['UPLOAD_FOLDER'], filename),
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    app.run(debug=True)