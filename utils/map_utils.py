import pandas as pd
import folium
import ast
import os

def load_world_data(world_file, personal_file):
    """
    Loads and merges world administrative boundaries with personal visited data.
    """
    try:
        if isinstance(world_file, str):
            world_data = pd.read_excel(world_file)
        else:
            world_data = pd.read_excel(world_file)
            
        if isinstance(personal_file, str):
            personal_data = pd.read_excel(personal_file)
        else:
            personal_data = pd.read_excel(personal_file)

        # Standardize columns if necessary
        # Assuming original structure for now
        
        df = (
            world_data
            .merge(
                personal_data,
                on='COUNTRY',
                how='inner'
            )
            .drop('CONTINENT', axis=1)
        )
        return df
    except Exception as e:
        print(f"Error loading world data: {e}")
        return None

def generate_world_map_html(df, visited_color="blue", map_style="CartoDB positron"):
    """
    Generates a Folium map for world travel and returns the HTML string.
    """
    m = folium.Map(location=[20, 0], zoom_start=2, tiles=map_style)
    
    if df is not None:
        visited_df = df[df['VISITED'] == 1]
        for idx, row in visited_df.iterrows():
            try:
                # Handle geometry parsing
                if isinstance(row['GEOMETRY'], str):
                    geometry = ast.literal_eval(row['GEOMETRY'])
                else:
                    geometry = row['GEOMETRY']
                    
                folium.GeoJson(
                    geometry,
                    style_function=lambda x, color=visited_color: {
                        'fillColor': color,
                        'color': 'black', # Border color
                        'weight': 0.5,
                        'fillOpacity': 0.7
                    },
                    tooltip=f"{row['COUNTRY']}"
                ).add_to(m)
            except Exception as e:
                pass 
                
    return m.get_root().render()

def load_provinces_data(personal_file):
    """
    Loads Argentina provinces data from Excel.
    Note: This version works without geopandas, using only the data in the Excel file.
    """
    try:
        if isinstance(personal_file, str):
            data = pd.read_excel(personal_file)
        else:
            data = pd.read_excel(personal_file)

        # Clean province names
        if 'province' in data.columns:
            data['province'] = data['province'].str.strip()
        
        return data
    except Exception as e:
        print(f"Error loading province data: {e}")
        return None

def generate_provinces_map_html(df, visited_color="blue", map_style="CartoDB positron"):
    """
    Generates a Folium map for Argentina provinces and returns the HTML string.
    Note: This simplified version only shows visited provinces as markers.
    For full polygon rendering, you would need the geometry data in the Excel.
    """
    m = folium.Map(location=[-38, -64], zoom_start=4, tiles=map_style)
    
    if df is not None:
        visited_df = df[df['visited'] == 1]
        
        if not visited_df.empty:
            # If the Excel has geometry data (like world data), use it
            if 'geometry' in visited_df.columns or 'GEOMETRY' in visited_df.columns:
                geom_col = 'geometry' if 'geometry' in visited_df.columns else 'GEOMETRY'
                
                for idx, row in visited_df.iterrows():
                    try:
                        if isinstance(row[geom_col], str):
                            geometry = ast.literal_eval(row[geom_col])
                        else:
                            geometry = row[geom_col]
                            
                        province_name = row.get('province', row.get('NAME_1', 'Unknown'))
                        
                        folium.GeoJson(
                            geometry,
                            style_function=lambda x, color=visited_color: {
                                'fillColor': color,
                                'color': 'black',
                                'weight': 1,
                                'fillOpacity': 0.6
                            },
                            tooltip=f"{province_name}"
                        ).add_to(m)
                    except Exception as e:
                        pass
            else:
                # Fallback: if no geometry, just show province names as text
                # (This is a degraded experience but won't crash)
                for idx, row in visited_df.iterrows():
                    province_name = row.get('province', 'Unknown')
                    folium.Marker(
                        location=[-38, -64],  # Default center - would need lat/lon in Excel
                        popup=f"Visited: {province_name}",
                        icon=folium.Icon(color='red', icon='info-sign')
                    ).add_to(m)
            
    return m.get_root().render()
