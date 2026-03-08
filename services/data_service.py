import pandas as pd
import io
import logging
from config.constants import WORLD_BOUNDARIES_PATH, GEO_MAPPING

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE = {'world_data': None}

def get_world_data():
    """Returns world boundaries DataFrame from cache or file."""
    if CACHE['world_data'] is None:
        try:
            CACHE['world_data'] = pd.read_excel(WORLD_BOUNDARIES_PATH)
            logger.info("World boundaries loaded into cache.")
        except Exception as e:
            logger.error(f"CRITICAL ERROR: Could not load world data: {e}")
            raise
    return CACHE['world_data']

def generate_template_buffer():
    """Generates an Excel template in memory and returns the buffer."""
    try:
        countries = sorted(list(set([item[0] for item in GEO_MAPPING])))
        df = pd.DataFrame({
            'COUNTRY': countries,
            'VISITED': [0] * len(countries)
        })
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer
    except Exception as e:
        logger.error(f"Error generating template: {e}")
        raise

def process_upload(file):
    """Processes uploaded Excel and returns list of visited countries."""
    try:
        df = pd.read_excel(file)
        df.columns = [c.upper() for c in df.columns]
        
        if 'COUNTRY' in df.columns and 'VISITED' in df.columns:
            return df[df['VISITED'] == 1]['COUNTRY'].tolist()
        else:
            raise ValueError("Required columns: COUNTRY, VISITED")
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        raise
