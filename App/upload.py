import os
import json
import subprocess
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads/'
OUTPUT_FOLDER = 'static/graphs/'  # Folder to store the generated graph
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Ensure the uploads and output folders exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the request contains the PDF file
    if 'pdf' not in request.files:
        return jsonify({'success': False, 'message': 'No file part in the request'}), 400

    file = request.files['pdf']
    
    # Check if a file was actually selected
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400

    # Save the uploaded PDF file in the uploads folder
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        print(f"File saved to: {file_path}")
    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({'success': False, 'message': 'Failed to save file'}), 500

    # Prepare the config JSON to pass the PDF path to the notebook
    config_data = {'pdf_path': file_path}
    try:
        with open('config.json', 'w') as config_file:
            json.dump(config_data, config_file)
    except Exception as e:
        print(f"Error writing config file: {e}")
        return jsonify({'success': False, 'message': 'Failed to write config file'}), 500

    # Run the Jupyter notebook using subprocess
    try:
        result = subprocess.run(
            ['jupyter', 'nbconvert', '--to', 'notebook', '--execute', '--inplace', 'OCR1.ipynb',
             '--ExecutePreprocessor.timeout=None'],
            capture_output=True, text=True, check=True
        )
        print(result.stdout)  # Log stdout
        print(result.stderr)  # Log stderr in case of errors

        # Check if the notebook produced the expected output (e.g., an HTML graph file)
        graph_filename = "lab_report_visualization.html"  # Update based on your notebook's output
        graph_filepath = os.path.join(app.config['OUTPUT_FOLDER'], graph_filename)

        if os.path.exists(graph_filepath):
            print(f"Graph file found: {graph_filepath}")
            graph_url = f'/graphs/{graph_filename}'
            return jsonify({'success': True, 'message': 'File processed successfully', 'processed_url': graph_url}), 200
        else:
            print("Graph file not found.")
            return jsonify({'success': False, 'message': 'Graph not generated'}), 500

    except subprocess.CalledProcessError as e:
        print(f"Error processing the notebook: {e.stderr}")
        return jsonify({'success': False, 'message': f'Failed to process the file: {e.stderr}'}), 500


# Serve the generated graph
@app.route('/graphs/<path:filename>')
def serve_graph(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
