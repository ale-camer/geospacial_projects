from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import shutil
import os
from utils.map_utils import load_world_data, generate_world_map_html, load_provinces_data, generate_provinces_map_html

app = FastAPI()

# Templates
templates = Jinja2Templates(directory="templates")

# Note: Static files mount removed for MVP since directory is empty

# Paths - defaulting to project root for simplicity in this MVP
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WORLD_DATA = os.path.join(BASE_DIR, "world_administrative_boundaries.xlsx")
DEFAULT_VISITED_COUNTRIES = os.path.join(BASE_DIR, "visited_countries.xlsx")
DEFAULT_VISITED_PROVINCES = os.path.join(BASE_DIR, "visited_provinces.xlsx")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate_map", response_class=HTMLResponse)
async def generate_map(
    request: Request,
    map_type: str = Form(...),
    visited_color: str = Form(...),
    map_style: str = Form(...)
):
    try:
        # For MVP, we are using default files. 
        # Ideally we'd handle file uploads here (to be added in next iteration)
        
        map_html_content = ""
        
        if map_type == "world":
            df = load_world_data(DEFAULT_WORLD_DATA, DEFAULT_VISITED_COUNTRIES)
            # We need to get the Folium Map object and get its HTML representation
            # But generate_world_map_html returns the rendered HTML string of the map directly?
            # Let's check map_utils. Oh, it returns m.get_root().render(). 
            # This is a full HTML document. We might want just the body or iframe it.
            # Usually easiest to serve it as a standalone page or iframe.
            
            # Let's adjust utils to return the Map object if we want to embed, or return full HTML string.
            # Assuming map_utils returns full HTML string for now.
            
            # We need to render the map into our template. 
            # Folium object .get_root().render() returns a full HTML struct (html, head, body, scripts). 
            # Injecting that into another HTML template is tricky.
            # Better approach: 
            # 1. Generate map, save to static/temp.html, return iframe source?
            # 2. Extract specific parts of Folium output?
            # 3. Just return the Folium HTML response directly as a purely map page?
            
            # Let's go with option 3 for simplicity first: The "Map View" is just the map.
            # Or Option 1: save to an HTML file and let the frontend iframe it.
            
            # Actually, let's create a specific endpoint that returns the map HTML
            # and verify how Folium integrates.
            pass

    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "error": str(e)})

# Redefining logic to be simpler:
# POST returns a "result" page which has an iframe pointing to the map content?
# Or just return the map directly.

@app.post("/view_map", response_class=HTMLResponse)
async def view_map(
    request: Request,
    map_type: str = Form(...),
    visited_color: str = Form(...),     
    map_style: str = Form(...)
):
    # Logic to return the raw Folium HTML
    if map_type == "world":
        df = load_world_data(DEFAULT_WORLD_DATA, DEFAULT_VISITED_COUNTRIES)
        # We need to access the map object to render it
        # Let's modify map_utils to return the Map object in memory, then we render headers here?
        # No, map_utils returns HTML string (render()). Folium's render() output is a complete HTML page.
        # So we can just return it as HTMLResponse.
        
        # We need to modify map_utils to accept our params
        # Wait, the current map_utils signature is: generate_world_map_html(df, visited_color, map_style)
        # But in map_utils.py I only implemented simple generation without color/style args in the signature?
        # Let me check map_utils.py content again.
        # Ah, I see I did define: generate_world_map_html(df, visited_color="blue", map_style="CartoDB positron")
        # So I can pass them!
        
        # Mapping frontend style names to folium tiles:
        tiles = map_style # Assume frontend sends valid tile string
        
        # Actually generate logic
        # For now, let's redefine the utils in memory or update map_utils if needed.
        # It seems I did assume map_utils had these args.
        
        # Hack: The map_utils.py I wrote relies on 'm.get_root().render()' which returns a JSON-like struct? 
        # No, .render() returns the HTML string content (Wait, getting mixed up with get_root().render() vs _repr_html_())
        # m.get_root().render() returns the full HTML string of the page.
        
        # Wait, folium m.get_root().render() might return the object representation. 
        # m.get_root().html.render() ?
        # Actually standard is `m.get_root().render()` which returns the string HTML.
        
        from utils.map_utils import generate_world_map_html
        
        html_content = generate_world_map_html(df, visited_color, map_style)
        return HTMLResponse(content=html_content)

    elif map_type == "provinces":
         df = load_provinces_data(DEFAULT_VISITED_PROVINCES)
         from utils.map_utils import generate_provinces_map_html
         html_content = generate_provinces_map_html(df, visited_color, map_style)
         return HTMLResponse(content=html_content)
         
    return HTMLResponse(content="Unknown map type", status_code=400)
    
