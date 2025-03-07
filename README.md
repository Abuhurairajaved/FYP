# GraphMedX:AI-Driven Knowledge Graphs for Health Insight

## Project Overview
The GraphMedX project aims to enhance the accessibility and comprehension of medical data through innovative technology integration. By utilizing Optical Character Recognition (OCR) to extract data from medical documents, the project converts unstructured data into a format suitable for analysis. Natural Language Processing (NLP) ensures the accuracy and contextual understanding of the extracted information. The core of the system involves constructing knowledge graphs that visually represent the relationships within the data, facilitating a deeper understanding and supporting better decision-making in medical environments.

## File Descriptions
1. **OCR.ipynb** - Jupyter notebook for OCR functionalities and text processing using Pytesseract and PDF2Image.
2. **KnowledgeGraph.ipynb** - Jupyter notebook for constructing and visualizing knowledge graphs using NetworkX and PyVis.
3. **app.py** - Flask application to handle API requests for patient data processing and visualization.
4. **app1.py** - Flask application for generating and serving graph visualizations of medical data.
5. **upload.py** - Flask application for handling file uploads and processing through configured paths.
6. **config_setup.json** - Configuration file used to manage settings across different parts of the application.
7. **ReactApp** - Directory containing the React application, which provides the user interface for interacting with the backend services.

## Setup Instructions

### Prerequisites
Make sure Python 3, pip, Node.js, and npm are installed on your system. You can download Python and pip from [Python's official site](https://python.org) and Node.js and npm from [Node.js's official site](https://nodejs.org).

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Abuhurairajaved/FYP
   
   ```

2. Install the required Python libraries:
   ```bash
   pip install Flask pandas networkx pyvis pytesseract pdf2image
   ```

3. Install Jupyter if you need to run the notebooks:
   ```bash
   pip install notebook
   ```

4. Navigate to the React application directory and install npm dependencies:
   ```bash
   cd ReactApp
   npm install
   ```

### Running the Applications
1. To run the Flask applications (`app.py`, `app1.py`, `upload.py`):
   ```bash
   python app.py
   python app1.py
   python upload.py
   ```
2. To start the React application:
   - Ensure you are still in the ReactApp directory, then:
     ```bash
     npm start
     ```
   - This command runs the app in development mode. Open [http://localhost:3000](http://localhost:3000) to view it in the browser..

### Configurations
- Ensure the `config_setup.json` file is set up correctly with necessary parameters like paths and IDs before running the applications.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
