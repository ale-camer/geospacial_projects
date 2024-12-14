import pandas as pd
import folium, webbrowser, warnings, json, ast
from utils import load_config, setting_default_environment
warnings.filterwarnings("ignore")

config = load_config("config.json")

world_data_name=config["world_data_name"]
personal_data_name=config["personal_data_name"]
map_name=config["map_name"]

def ingesting_data(
        world_data_name: str,
        personal_data_name: str
    ) -> pd.DataFrame:
    
    world_data = pd.read_excel(f'{world_data_name}.xlsx')
    personal_data = pd.read_excel(f'{personal_data_name}.xlsx')

    df = (
        world_data
        .merge(
            personal_data,
            on='COUNTRY',
            how='inner'
        )  
        .drop(
            'CONTINENT',
            axis=1
        )
    )
    
    return df
    
def map_creation(
        df : pd.DataFrame,
        map_name: str
    ) -> None:

    m = folium.Map(
        location=[0, 0], 
        zoom_start=2,
        tiles="CartoDB positron",
        attr="CartoDB"
    )  # creating map
    for idx, row in df[df['VISITED'] == 1].iterrows():  # populating map
        geometry = ast.literal_eval(row['GEOMETRY'])
        folium.GeoJson(
            geometry,
            style_function=lambda x: {
                'fillColor': 'blue',
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.7
            },
            tooltip=f"{row['COUNTRY']}"
        ).add_to(m)
    m.save(f'{map_name}.html') # saving map
    webbrowser.open(f'{map_name}.html') # opening map

if __name__ == "__main__":
    setting_default_environment()  # Set environment
    map_creation(
        ingesting_data(
            world_data_name,
            personal_data_name
        ),
        map_name
    )  # Print the map