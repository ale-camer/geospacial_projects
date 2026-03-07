from flask import Flask, render_template, request, jsonify
import pandas as pd
import folium
import ast
import os

app = Flask(__name__)

# --- Configuration & Constants ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORLD_BOUNDARIES_PATH = os.path.join(BASE_DIR, "world_administrative_boundaries.xlsx")

# In-memory cache for performance
CACHE = {'world_data': None}

# --- Data Mapping (Continents & Regions) ---
# Each tuple: (Country Name, Continent, Sub-Region)
# Cross-listed: Turkey appears in both Asia and Europe as requested.
GEO_MAPPING = [
    # Africa
    ('Egypt', 'Africa', 'Northern Africa'), ('Algeria', 'Africa', 'Northern Africa'), 
    ('Morocco', 'Africa', 'Northern Africa'), ('Tunisia', 'Africa', 'Northern Africa'), 
    ('Libya', 'Africa', 'Northern Africa'), ('Sudan', 'Africa', 'Northern Africa'),
    ('Nigeria', 'Africa', 'Western Africa'), ('Ghana', 'Africa', 'Western Africa'), 
    ('Senegal', 'Africa', 'Western Africa'), ('Ivory Coast', 'Africa', 'Western Africa'),
    ('Ethiopia', 'Africa', 'Eastern Africa'), ('Kenya', 'Africa', 'Eastern Africa'), 
    ('Tanzania', 'Africa', 'Eastern Africa'), ('Uganda', 'Africa', 'Eastern Africa'),
    ('Somalia', 'Africa', 'Eastern Africa'), ('Djibouti', 'Africa', 'Eastern Africa'),
    ('South Africa', 'Africa', 'Southern Africa'), ('Namibia', 'Africa', 'Southern Africa'), 
    ('Botswana', 'Africa', 'Southern Africa'), ('Zimbabwe', 'Africa', 'Southern Africa'),
    ('Congo (Kinshasa)', 'Africa', 'Central Africa'), ('Congo (Brazzaville)', 'Africa', 'Central Africa'), 
    ('Angola', 'Africa', 'Central Africa'), ('Gabon', 'Africa', 'Central Africa'),
    ('Mozambique', 'Africa', 'Southern Africa'), ('Lesotho', 'Africa', 'Southern Africa'), 
    ('Eswatini', 'Africa', 'Southern Africa'), ('Eritrea', 'Africa', 'Eastern Africa'), 
    ('Madagascar', 'Africa', 'Eastern Africa'),

    # Americas
    ('Argentina', 'Americas', 'South America'), ('Brazil', 'Americas', 'South America'), 
    ('Chile', 'Americas', 'South America'), ('Colombia', 'Americas', 'South America'), 
    ('Peru', 'Americas', 'South America'), ('Uruguay', 'Americas', 'South America'), 
    ('Paraguay', 'Americas', 'South America'), ('Bolivia', 'Americas', 'South America'),
    ('Ecuador', 'Americas', 'South America'), ('Venezuela', 'Americas', 'South America'), 
    ('Suriname', 'Americas', 'South America'), ('Guyana', 'Americas', 'South America'),
    ('French Guiana', 'Americas', 'South America'), ('Falkland Islands', 'Americas', 'South America'),
    ('South Georgia and the South Sandwich Islands', 'Americas', 'South America'),
    ('Panama', 'Americas', 'Central America'), ('Costa Rica', 'Americas', 'Central America'), 
    ('Nicaragua', 'Americas', 'Central America'), ('Honduras', 'Americas', 'Central America'), 
    ('El Salvador', 'Americas', 'Central America'), ('Guatemala', 'Americas', 'Central America'), 
    ('Belize', 'Americas', 'Central America'),
    ('Cuba', 'Americas', 'Caribbean'), ('Jamaica', 'Americas', 'Caribbean'), 
    ('Haiti', 'Americas', 'Caribbean'), ('Dominican Republic', 'Americas', 'Caribbean'),
    ('Puerto Rico', 'Americas', 'Caribbean'), ('Bahamas', 'Americas', 'Caribbean'), 
    ('Barbados', 'Americas', 'Caribbean'), ('Trinidad and Tobago', 'Americas', 'Caribbean'),
    ('Saint Lucia', 'Americas', 'Caribbean'), ('Grenada', 'Americas', 'Caribbean'),
    ('Saint Vincent and the Grenadines', 'Americas', 'Caribbean'), ('Antigua and Barbuda', 'Americas', 'Caribbean'),
    ('Saint Kitts and Nevis', 'Americas', 'Caribbean'), ('Dominica', 'Americas', 'Caribbean'),
    ('Aruba', 'Americas', 'Caribbean'), ('Cayman Islands', 'Americas', 'Caribbean'),
    ('British Virgin Islands', 'Americas', 'Caribbean'), ('United States Virgin Islands', 'Americas', 'Caribbean'),
    ('Anguilla', 'Americas', 'Caribbean'), ('Montserrat', 'Americas', 'Caribbean'),
    ('Curaçao', 'Americas', 'Caribbean'), ('Sint Maarten', 'Americas', 'Caribbean'),
    ('United States', 'Americas', 'North America'), ('Canada', 'Americas', 'North America'), 
    ('Mexico', 'Americas', 'North America'), ('Greenland', 'Americas', 'North America'),
    ('Bermuda', 'Americas', 'North America'), ('Saint Pierre and Miquelon', 'Americas', 'North America'),
    ('Antarctica', 'Americas', 'Antarctica'),

    # Asia
    ('China', 'Asia', 'East Asia'), ('Japan', 'Asia', 'East Asia'), 
    ('South Korea', 'Asia', 'East Asia'), ('North Korea', 'Asia', 'East Asia'), 
    ('Taiwan', 'Asia', 'East Asia'), ('Mongolia', 'Asia', 'East Asia'),
    ('India', 'Asia', 'South Asia'), ('Pakistan', 'Asia', 'South Asia'), 
    ('Bangladesh', 'Asia', 'South Asia'), ('Sri Lanka', 'Asia', 'South Asia'), 
    ('Nepal', 'Asia', 'South Asia'), ('Bhutan', 'Asia', 'South Asia'), ('Maldives', 'Asia', 'South Asia'),
    ('Afghanistan', 'Asia', 'South Asia'),
    ('Indonesia', 'Asia', 'Southeast Asia'), ('Thailand', 'Asia', 'Southeast Asia'), 
    ('Vietnam', 'Asia', 'Southeast Asia'), ('Malaysia', 'Asia', 'Southeast Asia'), 
    ('Philippines', 'Asia', 'Southeast Asia'), ('Singapore', 'Asia', 'Southeast Asia'),
    ('Myanmar', 'Asia', 'Southeast Asia'), ('Cambodia', 'Asia', 'Southeast Asia'), 
    ('Laos', 'Asia', 'Southeast Asia'), ('Brunei', 'Asia', 'Southeast Asia'), ('Timor-Leste', 'Asia', 'Southeast Asia'),
    ('Kazakhstan', 'Asia', 'Central Asia'), ('Uzbekistan', 'Asia', 'Central Asia'), 
    ('Turkmenistan', 'Asia', 'Central Asia'), ('Kyrgyzstan', 'Asia', 'Central Asia'),
    ('Tajikistan', 'Asia', 'Central Asia'),
    ('Saudi Arabia', 'Asia', 'Western Asia'), ('United Arab Emirates', 'Asia', 'Western Asia'), 
    ('Israel', 'Asia', 'Western Asia'), ('Turkey', 'Asia', 'Western Asia'),
    ('Iran', 'Asia', 'Western Asia'), ('Iraq', 'Asia', 'Western Asia'), 
    ('Jordan', 'Asia', 'Western Asia'), ('Lebanon', 'Asia', 'Western Asia'),
    ('Syria', 'Asia', 'Western Asia'), ('Yemen', 'Asia', 'Western Asia'), 
    ('Oman', 'Asia', 'Western Asia'), ('Qatar', 'Asia', 'Western Asia'),
    ('Kuwait', 'Asia', 'Western Asia'), ('Bahrain', 'Asia', 'Western Asia'),
    ('Armenia', 'Asia', 'Western Asia'), ('Azerbaijan', 'Asia', 'Western Asia'), ('Georgia', 'Asia', 'Western Asia'),

    # Europe
    ('United Kingdom', 'Europe', 'Northern Europe'), ('Ireland', 'Europe', 'Northern Europe'), 
    ('Norway', 'Europe', 'Northern Europe'), ('Sweden', 'Europe', 'Northern Europe'), 
    ('Denmark', 'Europe', 'Northern Europe'), ('Finland', 'Europe', 'Northern Europe'), 
    ('Iceland', 'Europe', 'Northern Europe'), ('Estonia', 'Europe', 'Northern Europe'),
    ('Latvia', 'Europe', 'Northern Europe'), ('Lithuania', 'Europe', 'Northern Europe'),
    ('France', 'Europe', 'Western Europe'), ('Germany', 'Europe', 'Central Europe'), 
    ('Netherlands', 'Europe', 'Western Europe'), ('Belgium', 'Europe', 'Western Europe'), 
    ('Switzerland', 'Europe', 'Western Europe'), ('Austria', 'Europe', 'Western Europe'),
    ('Liechtenstein', 'Europe', 'Western Europe'), ('Monaco', 'Europe', 'Western Europe'),
    ('Spain', 'Europe', 'Southern Europe'), ('Italy', 'Europe', 'Southern Europe'), 
    ('Portugal', 'Europe', 'Southern Europe'), ('Greece', 'Europe', 'Southern Europe'), 
    ('Malta', 'Europe', 'Southern Europe'), ('Cyprus', 'Europe', 'Southern Europe'),
    ('Andorra', 'Europe', 'Southern Europe'), ('Vatican City', 'Europe', 'Southern Europe'), ('San Marino', 'Europe', 'Southern Europe'),
    ('Croatia', 'Europe', 'Balkans'), ('Serbia', 'Europe', 'Balkans'), ('Bosnia and Herzegovina', 'Europe', 'Balkans'),
    ('Montenegro', 'Europe', 'Balkans'), ('Albania', 'Europe', 'Balkans'), ('North Macedonia', 'Europe', 'Balkans'),
    ('Bulgaria', 'Europe', 'Balkans'), ('Slovenia', 'Europe', 'Balkans'), ('Romania', 'Europe', 'Balkans'),
    ('Poland', 'Europe', 'Eastern Europe'), ('Ukraine', 'Europe', 'Eastern Europe'), 
    ('Russia', 'Europe', 'Eastern Europe'), ('Belarus', 'Europe', 'Eastern Europe'), ('Moldova', 'Europe', 'Eastern Europe'),
    ('Czech Republic', 'Europe', 'Central Europe'), ('Slovakia', 'Europe', 'Central Europe'), ('Hungary', 'Europe', 'Central Europe'),
    ('Turkey', 'Europe', 'Western Asia'),

    # Oceania
    ('Australia', 'Oceania', 'Continental'), ('New Zealand', 'Oceania', 'Continental'), 
    ('Fiji', 'Oceania', 'Islands'), ('Papua New Guinea', 'Oceania', 'Islands'),
    ('Solomon Islands', 'Oceania', 'Islands'), ('Vanuatu', 'Oceania', 'Islands'),
    ('Samoa', 'Oceania', 'Islands'), ('Kiribati', 'Oceania', 'Islands'), ('Tonga', 'Oceania', 'Islands'),
    ('Micronesia', 'Oceania', 'Islands'), ('Palau', 'Oceania', 'Islands'), ('Marshall Islands', 'Oceania', 'Islands'),
    ('Nauru', 'Oceania', 'Islands'), ('Tuvalu', 'Oceania', 'Islands'),
]

# --- Helper Functions ---

def get_world_data():
    """Returns world boundaries DataFrame from cache or file."""
    if CACHE['world_data'] is None:
        try:
            CACHE['world_data'] = pd.read_excel(WORLD_BOUNDARIES_PATH)
        except Exception as e:
            print(f"CRITICAL ERROR: Could not load world data: {e}")
    return CACHE['world_data']

def apply_print_injection(m):
    """Injects CSS and HTML for map printing and downloading."""
    map_html = m.get_root().render()
    injection = """
    <style>
        @media print {
            .leaflet-interactive {
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            [n-download-btn] { display: none !important; }
        }
    </style>
    <div n-download-btn style="position: fixed; top: 10px; left: 50px; z-index: 9999;">
        <button onclick="window.print()" style="padding: 8px 12px; background: white; border: 2px solid rgba(0,0,0,0.2); border-radius: 4px; cursor: pointer; font-weight: bold; box-shadow: 0 1px 5px rgba(0,0,0,0.4);">
            🖨️ Download / Print Map
        </button>
    </div>
    """
    if "</body>" in map_html:
        return map_html.replace("</body>", f"{injection}</body>")
    return map_html + injection

# --- Routes ---

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
    
    # Sort within each region
    for continent in data:
        for region in data[continent]:
            data[continent][region].sort(key=lambda x: x['name'])
            
    return jsonify(data)

@app.route('/api/download_template')
def download_template():
    """API: Generates and downloads an Excel template for country selection."""
    try:
        # Get unique countries from GEO_MAPPING
        countries = sorted(list(set([item[0] for item in GEO_MAPPING])))
        df = pd.DataFrame({
            'COUNTRY': countries,
            'VISITED': [0] * len(countries)
        })
        
        output_path = os.path.join(BASE_DIR, "template_countries.xlsx")
        df.to_excel(output_path, index=False)
        
        from flask import send_file
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """API: Processes Excel and returns list of visited countries."""
    try:
        if 'file' not in request.files: return jsonify({"error": "No file"}), 400
        file = request.files['file']
        if file.filename == '': return jsonify({"error": "Empty filename"}), 400
        
        df = pd.read_excel(file)
        df.columns = [c.upper() for c in df.columns] # Normalize
        
        if 'COUNTRY' in df.columns and 'VISITED' in df.columns:
            visited = df[df['VISITED'] == 1]['COUNTRY'].tolist()
            return jsonify(visited)
        return jsonify({"error": "Required columns: COUNTRY, VISITED"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/view_map', methods=['POST'])
def view_map():
    """Route: Generates the interactive Folium map."""
    selected_countries = request.form.getlist('selected_countries')
    visited_color = request.form.get('visited_color', '#3498db')
    map_style = request.form.get('map_style', 'CartoDB positron')
    
    m = folium.Map(location=[20, 0], zoom_start=2, tiles=map_style)
    world_df = get_world_data()
    
    if world_df is not None and selected_countries:
        filtered_df = world_df[world_df['COUNTRY'].isin(selected_countries)]
        for _, row in filtered_df.iterrows():
            try:
                geom = ast.literal_eval(row['GEOMETRY']) if isinstance(row['GEOMETRY'], str) else row['GEOMETRY']
                folium.GeoJson(geom, style_function=lambda x, color=visited_color: {
                    'fillColor': color, 'color': 'black', 'weight': 0.5, 'fillOpacity': 0.7
                }, tooltip=row['COUNTRY']).add_to(m)
            except: pass
            
    return apply_print_injection(m)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8000)
