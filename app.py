import os
import logging
from flask import Flask, render_template, request, jsonify, send_file
from config.constants import GEO_MAPPING
from services.data_service import generate_template_buffer, process_upload
from services.map_service import generate_map

# Application Setup
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/countries')
def get_countries():
    """API: Returns countries grouped by Continent and Region, sorted alphabetically."""
    data = {}
    for country, continent, region in GEO_MAPPING:
        if continent not in data: data[continent] = {}
        if region not in data[continent]: data[continent][region] = []
        data[continent][region].append({'name': country})
    
    for continent in data:
        for region in data[continent]:
            data[continent][region].sort(key=lambda x: x['name'])
            
    return jsonify(data)

@app.route('/api/download_template')
def download_template():
    """API: Generates and downloads an Excel template from memory (BytesIO)."""
    try:
        buffer = generate_template_buffer()
        return send_file(
            buffer,
            as_attachment=True,
            download_name="template_countries.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        logger.error(f"Download template failed: {e}")
        return jsonify({"error": "Failed to generate template"}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """API: Processes Excel and returns list of visited countries."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400
        
        visited = process_upload(file)
        return jsonify(visited)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Upload processing failed: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/view_map', methods=['POST'])
def view_map_route():
    """Route: Generates the interactive Folium map."""
    try:
        selected_countries = request.form.getlist('selected_countries')
        visited_color = request.form.get('visited_color', '#3498db')
        map_style = request.form.get('map_style', 'CartoDB positron')
        
        html_content = generate_map(selected_countries, visited_color, map_style)
        return html_content
    except Exception as e:
        logger.error(f"Map route failed: {e}")
        return "Error generating map", 500

if __name__ == '__main__':
    # Production settings for GCP
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
