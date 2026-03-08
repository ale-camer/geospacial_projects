import folium
import ast
import logging
from services.data_service import get_world_data

logger = logging.getLogger(__name__)

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

def generate_map(selected_countries, visited_color, map_style):
    """Generates the main Folium map with selected highlights."""
    try:
        m = folium.Map(location=[20, 0], zoom_start=2, tiles=map_style)
        world_df = get_world_data()
        
        if world_df is not None and selected_countries:
            filtered_df = world_df[world_df['COUNTRY'].isin(selected_countries)]
            for _, row in filtered_df.iterrows():
                try:
                    # Parse geometry
                    geom = ast.literal_eval(row['GEOMETRY']) if isinstance(row['GEOMETRY'], str) else row['GEOMETRY']
                    
                    folium.GeoJson(
                        geom, 
                        style_function=lambda x, color=visited_color: {
                            'fillColor': color, 'color': 'black', 'weight': 0.5, 'fillOpacity': 0.7
                        }, 
                        tooltip=row['COUNTRY']
                    ).add_to(m)
                except Exception as e:
                    logger.warning(f"Failed to render geometry for {row.get('COUNTRY')}: {e}")
                    
        return apply_print_injection(m)
    except Exception as e:
        logger.error(f"Map generation error: {e}")
        raise
