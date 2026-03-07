from flask import Flask, render_template, request
import os
from utils.map_utils import load_world_data, generate_world_map_html, load_provinces_data, generate_provinces_map_html

app = Flask(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WORLD_DATA = os.path.join(BASE_DIR, "world_administrative_boundaries.xlsx")
DEFAULT_VISITED_COUNTRIES = os.path.join(BASE_DIR, "visited_countries.xlsx")
DEFAULT_VISITED_PROVINCES = os.path.join(BASE_DIR, "visited_provinces.xlsx")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view_map', methods=['POST'])
def view_map():
    map_type = request.form.get('map_type')
    visited_color = request.form.get('visited_color', '#3498db')
    map_style = request.form.get('map_style', 'CartoDB positron')
    
    if map_type == 'world':
        df = load_world_data(DEFAULT_WORLD_DATA, DEFAULT_VISITED_COUNTRIES)
        html_content = generate_world_map_html(df, visited_color, map_style)
        return html_content
    
    elif map_type == 'provinces':
        df = load_provinces_data(DEFAULT_VISITED_PROVINCES)
        html_content = generate_provinces_map_html(df, visited_color, map_style)
        return html_content
    
    return "Unknown map type", 400

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8000)
