import pandas as pd
import geopandas as gpd
import folium, webbrowser, warnings, os
warnings.filterwarnings("ignore")

def setting_environment(
    path : str = "C:/Users/ale_c/OneDrive/Desktop/GitHub/visited_places/"
    ) -> None:
    os.chdir(path)

def ingesting_input_data(
    personal_data_path : str = "visited_countries.xlsx"
    ) -> pd.DataFrame:
    
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    data = pd.read_excel(personal_data_path)

    df = (
        world
        .merge(
            data,
            left_on='name',
            right_on='country',
            how='left',
            suffixes=('','_y')
        )  
        .dropna()
        .drop(['continent_y', 'country'], axis=1)
    )
    
    return df
    
def map_creation(
    df : pd.DataFrame,
    path : str = "C:/Users/ale_c/OneDrive/Desktop/GitHub/visited_places/"
    ) -> None:

    m = folium.Map(location=[20, 0], zoom_start=2) # creating map
    for idx, row in df[df['visited'] == 1].iterrows(): # populating map
        folium.GeoJson(
            row['geometry'],
            style_function=lambda x: {
                'fillColor': 'blue',
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.7
            },
            tooltip=f"{row['name']}"
        ).add_to(m)
    map_path = os.path.join(path, 'visited_countries_map.html') # saving map
    m.save(map_path)
    
    return map_path

def printing_map(
    map_path : str
    ) -> None:
    
    webbrowser.open('file://' + os.path.realpath(map_path)) # opening map

if __name__ == "__main__":
    setting_environment()  # Set environment
    printing_map(map_creation(ingesting_input_data()))  # Print the map