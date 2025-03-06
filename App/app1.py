import os
import json
import subprocess
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OUTPUT_FOLDER = 'static/graphs/'  # Folder to store the generated graphs
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Ensure the output folder exists
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

@app.route('/generate_graphs', methods=['POST'])
def generate_graphs():
    # Check for patient ID in the request
    data = request.get_json()
    patient_id = data.get('patient_id')
    if not patient_id:
        return jsonify({'success': False, 'message': 'Patient ID is required'}), 400

    # Pass the patient ID to the notebook via config
    config_data = {'patient_id': patient_id}
    with open('config.json', 'w') as config_file:
        json.dump(config_data, config_file)

    # Run the Jupyter notebook
    try:
        result = subprocess.run(
            ['jupyter', 'nbconvert', '--to', 'notebook', '--execute', '--inplace', 'knowledge_graphs.ipynb',
             '--ExecutePreprocessor.timeout=None'],
            capture_output=True, text=True, check=True
        )
        print(result.stdout)  # Log stdout
        print(result.stderr)  # Log stderr in case of errors

        # Paths for the generated graph files
        graph_filename1 = "patient_journey.html"
        graph_filename2 = "lab_reports_network.html"
        
        # Full paths
        graph_filepath1 = os.path.join(app.config['OUTPUT_FOLDER'], graph_filename1)
        graph_filepath2 = os.path.join(app.config['OUTPUT_FOLDER'], graph_filename2)

        # Check if both graphs exist
        if os.path.exists(graph_filepath1) and os.path.exists(graph_filepath2):
            return jsonify({
                'success': True,
                'graph_url1': f'/graphs/{graph_filename1}',
                'graph_url2': f'/graphs/{graph_filename2}'
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Graphs not generated'}), 500

    except subprocess.CalledProcessError as e:
        print(f"Error processing the notebook: {e.stderr}")
        return jsonify({'success': False, 'message': 'Failed to process the file'}), 500

# Route to serve the generated graphs
@app.route('/graphs/<path:filename>')
def serve_graph(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
