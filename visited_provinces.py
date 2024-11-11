import pandas as pd
import geopandas as gpd
import folium, webbrowser, warnings, os
warnings.filterwarnings("ignore")

def setting_environment(
    path : str = "C:/Users/ale_c/OneDrive/Desktop/GitHub/visited_places/"
    ) -> None:
    os.chdir(path)

def ingesting_input_data(
    personal_data_path : str = "visited_provinces.xlsx"
    ) -> pd.DataFrame:
    
    provinces = gpd.read_file("https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_ARG_1.json")
    data = pd.read_excel(personal_data_path)

    df = (
        provinces
        .merge(
            data,
            left_on='NAME_1',
            right_on='province',
            how='left'
        )
        .loc[lambda x: x['visited'] == 1]
        .filter(['NAME_1', 'geometry'])
        .rename(columns = {'NAME_1' : 'name'})
    )
    
    return df

def map_creation(
    df : pd.DataFrame,
    path : str = "C:/Users/ale_c/OneDrive/Desktop/GitHub/visited_places/"
    ) -> None:

    # Centrado en Argentina
    m = folium.Map(location=[-38, -64], zoom_start=4)  # Ajuste de coordenadas para centrar el mapa en Argentina

    # Resaltar las fronteras de Argentina
    folium.GeoJson(
        gpd.read_file("https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_ARG_0.json").geometry,
        style_function=lambda x: {
            'fillColor': 'white',    # Sin relleno
            'color': 'red',          # Resaltar el borde con rojo
            'weight': 3,             # Grosor de la línea
            'fillOpacity': 0.0       # Sin opacidad en el relleno
        }
    ).add_to(m)

    for idx, row in df.iterrows():  # populating map
        folium.GeoJson(
            row['geometry'],
            style_function=lambda x: {
                'fillColor': 'blue',    # Color del relleno
                'color': 'black',       # Color de la línea
                'weight': 0.5,          # Grosor de la línea
                'fillOpacity': 0.5      # Opacidad del relleno
            },
            tooltip=f"{row['name']}"
        ).add_to(m)
    
    map_path = os.path.join(path, 'visited_provinces_map.html')  # saving map
    m.save(map_path)
    
    return map_path

def printing_map(
    map_path : str
    ) -> None:
    
    webbrowser.open('file://' + os.path.realpath(map_path)) # opening map

if __name__ == "__main__":
    setting_environment()  # Set environment
    printing_map(map_creation(ingesting_input_data()))  # Print the map
