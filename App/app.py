from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import networkx as nx
from pyvis.network import Network
import os
import traceback

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

# Ensure the static folder exists
if not os.path.exists('static'):
    os.makedirs('static')

# Helper function to check if all CSV files exist
def check_csv_files_exist(files):
    for file in files:
        if not os.path.exists(file):
            return False, file
    return True, None

@app.route('/api/patient-journey')
def patient_journey():
    try:
        # CSV files required
        required_files = ['small_dataset/PATIENTS.csv', 'small_dataset/ADMISSIONS.csv', 
                          'small_dataset/DIAGNOSES_ICD.csv', 'small_dataset/PROCEDURES_ICD.csv', 
                          'small_dataset/PRESCRIPTIONS.csv']
        files_exist, missing_file = check_csv_files_exist(required_files)
        if not files_exist:
            return jsonify({'error': f"{missing_file} not found"}), 404

        # Load CSV files
        patients_df = pd.read_csv('small_dataset/PATIENTS.csv')
        admissions_df = pd.read_csv('small_dataset/ADMISSIONS.csv')
        diagnoses_df = pd.read_csv('small_dataset/DIAGNOSES_ICD.csv')
        procedures_df = pd.read_csv('small_dataset/PROCEDURES_ICD.csv')
        prescriptions_df = pd.read_csv('small_dataset/PRESCRIPTIONS.csv')

        first_patient_id = patients_df['subject_id'].iloc[0]

        admissions_df = admissions_df[admissions_df['subject_id'] == first_patient_id]
        diagnoses_df = diagnoses_df[diagnoses_df['hadm_id'].isin(admissions_df['hadm_id'])]
        procedures_df = procedures_df[procedures_df['hadm_id'].isin(admissions_df['hadm_id'])]
        prescriptions_df = prescriptions_df[prescriptions_df['hadm_id'].isin(admissions_df['hadm_id'])]

        G = nx.DiGraph()

        G.add_node(str(first_patient_id), title=f"Patient {first_patient_id}", color="lightblue", size=25)

        for idx, row in admissions_df.iterrows():
            G.add_node(str(row['hadm_id']), title=f"Admission {row['hadm_id']}", color="yellow", size=20)
            G.add_edge(str(first_patient_id), str(row['hadm_id']), title='had admission')

        for idx, row in diagnoses_df.iterrows():
            G.add_node(str(row['icd9_code']), title=f"Diagnosis {row['icd9_code']}", color="green", size=15)
            G.add_edge(str(row['hadm_id']), str(row['icd9_code']), title='has diagnosis')

        for idx, row in procedures_df.iterrows():
            G.add_node(str(row['icd9_code']), title=f"Procedure {row['icd9_code']}", color="red", size=15)
            G.add_edge(str(row['hadm_id']), str(row['icd9_code']), title='underwent procedure')

        for idx, row in prescriptions_df.iterrows():
            G.add_node(str(row['drug']), title=f"Prescribed {row['drug']}", color="purple", size=15)
            G.add_edge(str(row['hadm_id']), str(row['drug']), title='was prescribed')

        net = Network(width='1000px', height='2000px', notebook=False)
        net.from_nx(G)
        html_filename = 'patient_journey_graph.html'
        html_path = os.path.join(app.static_folder, html_filename)
        net.write_html(html_path)

        return jsonify({'html_path': f'/static/{html_filename}'})

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/diagnosis-codes')
def diagnosis_codes():
    try:
        required_file = 'small_dataset/D_ICD_DIAGNOSES.csv'
        if not os.path.exists(required_file):
            return jsonify({'error': f"{required_file} not found"}), 404

        diagnoses_df = pd.read_csv(required_file)
        diagnosis_codes = diagnoses_df['icd9_code'].unique().tolist()

        G = nx.Graph()
        diagnoses_df = diagnoses_df[['icd9_code', 'short_title']].head(10)

        for index, row in diagnoses_df.iterrows():
            icd_node = f"ICD9 Code: {row['icd9_code']}"
            title_node = f"Title: {row['short_title']}"
            G.add_node(icd_node, title=icd_node, label=icd_node, size=15)
            G.add_node(title_node, title=title_node, label=title_node, size=15)
            G.add_edge(icd_node, title_node, title="refers to", label="refers to", length=100, color='green')

        net = Network(width='1000px', height='1000px', notebook=False, directed=False)
        net.from_nx(G)
        html_filename = 'diagnoses_network.html'
        html_path = os.path.join(app.static_folder, html_filename)
        net.write_html(html_path)

        return jsonify({'html_path': f'/static/{html_filename}'})

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/lab-reports')
def lab_reports():
    try:
        required_files = ['small_dataset/PATIENTS.csv', 'small_dataset/ADMISSIONS.csv', 
                          'small_dataset/LABEVENTS.csv', 'small_dataset/D_LABITEMS.csv']
        files_exist, missing_file = check_csv_files_exist(required_files)
        if not files_exist:
            return jsonify({'error': f"{missing_file} not found"}), 404

        patients_df = pd.read_csv('small_dataset/PATIENTS.csv')
        admissions_df = pd.read_csv('small_dataset/ADMISSIONS.csv')
        labevents_df = pd.read_csv('small_dataset/LABEVENTS.csv')
        d_labitems_df = pd.read_csv('small_dataset/D_LABITEMS.csv')

        first_patient_id = patients_df['subject_id'].iloc[0]
        admissions_df_filtered = admissions_df[admissions_df['subject_id'] == first_patient_id]
        labevents_df_filtered = labevents_df[labevents_df['hadm_id'].isin(admissions_df_filtered['hadm_id'])]

        G = nx.DiGraph()
        G.add_node(str(first_patient_id), title=f"Patient {first_patient_id}", color="lightblue", size=25)

        for idx, row in admissions_df_filtered.iterrows():
            G.add_node(str(row['hadm_id']), title=f"Admission {row['hadm_id']}", color="yellow", size=20)
            G.add_edge(str(first_patient_id), str(row['hadm_id']), title='had admission')

        for idx, row in labevents_df_filtered.iterrows():
            item_desc = d_labitems_df[d_labitems_df['itemid'] == row['itemid']].iloc[0]['label']
            test_name = f"Test {row['itemid']} - {item_desc}"
            G.add_node(test_name, title=f"{test_name}: {row['value']} {row['valueuom']}", color="orange", size=15)
            G.add_edge(str(row['hadm_id']), test_name, title='lab result')

        net = Network(width='1000px', height='2000px', notebook=False)
        net.from_nx(G)
        html_filename = 'lab_reports_graph.html'
        html_path = os.path.join(app.static_folder, html_filename)
        net.write_html(html_path)

        return jsonify({'html_path': f'/static/{html_filename}'})

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Serve static files
@app.route('/static/<path:filename>')
def serve_static_file(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(debug=True)
