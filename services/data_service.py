import pandas as pd
import io
import ast
import logging
from config.constants import WORLD_BOUNDARIES_PATH, GEO_MAPPING

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE = {
    'world_data': None,
    'features_by_country': None,
}

def get_world_data():
    """
    Returns world boundaries DataFrame from cache or file, with normalized country names
    and pre-parsed GeoJSON geometries so ast.literal_eval only runs once at startup.
    """
    if CACHE['world_data'] is None:
        try:
            df = pd.read_excel(WORLD_BOUNDARIES_PATH)
            if 'COUNTRY' in df.columns:
                df['COUNTRY'] = df['COUNTRY'].astype(str).str.strip()
            if 'GEOMETRY' in df.columns:
                df['GEOMETRY'] = df['GEOMETRY'].apply(
                    lambda g: ast.literal_eval(g) if isinstance(g, str) else g
                )
            CACHE['world_data'] = df

            features = {}
            for _, row in df.iterrows():
                country = row.get('COUNTRY')
                geom = row.get('GEOMETRY')
                if country and isinstance(geom, dict):
                    features[country] = {
                        'type': 'Feature',
                        'properties': {'name': country},
                        'geometry': geom,
                    }
            CACHE['features_by_country'] = features
            logger.info(f"World boundaries loaded and {len(features)} GeoJSON features pre-parsed into cache.")
        except Exception as e:
            logger.error(f"CRITICAL ERROR: Could not load world data: {e}")
            raise
    return CACHE['world_data']


def get_cached_features():
    """Returns dict mapping canonical country name -> pre-parsed GeoJSON Feature."""
    if CACHE['features_by_country'] is None:
        get_world_data()
    return CACHE['features_by_country']

def generate_template_buffer(selected_countries=None):
    """
    Generates an Excel file in memory and returns the BytesIO buffer.
    If selected_countries is provided, marks those countries with VISITED=1
    (allowing the user to export their current selection); otherwise sets all to 0.
    """
    try:
        selected_set = {str(c).strip() for c in (selected_countries or []) if c}
        rows = sorted(GEO_MAPPING, key=lambda item: (item[1], item[2], item[0]))
        df = pd.DataFrame([
            {
                'CONTINENT': continent,
                'REGION': region,
                'COUNTRY': country,
                'VISITED': 1 if country in selected_set else 0,
            }
            for country, continent, region in rows
        ])

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer
    except Exception as e:
        logger.error(f"Error generating template: {e}")
        raise

# Common country aliases for Excel upload normalization → canonical GEO_MAPPING key
UPLOAD_COUNTRY_ALIASES = {
    'turkey': 'Turkey',
    'türkiye': 'Turkey',
    'congo, republic of': 'Congo, Republic of',
    'republic of the congo': 'Congo, Republic of',
    'congo - brazzaville': 'Congo, Republic of',
    'congo - kinshasa': 'Congo, Dem. Rep. of the',
    'democratic republic of the congo': 'Congo, Dem. Rep. of the',
    'drc': 'Congo, Dem. Rep. of the',
    'china': "China, People's Republic of",
    "people's republic of china": "China, People's Republic of",
    'south korea': 'Korea, Republic of',
    'republic of korea': 'Korea, Republic of',
    'bahamas': 'Bahamas, The',
    'the bahamas': 'Bahamas, The',
    'eswatini': 'Swaziland',
    'russia': 'Russian Federation',
    'czechia': 'Czech Republic',
    'slovakia': 'Slovak Republic',
    'serbia': 'Republic of Serbia',
    'kyrgyzstan': 'Kyrgyz Republic',
    'timor-leste': 'East Timor',
    'usa': 'United States',
    'united states of america': 'United States',
    'uk': 'United Kingdom',
    'great britain': 'United Kingdom',
    'cote d\'ivoire': 'Ivory Coast',
    'côte d’ivoire': 'Ivory Coast',
    'côte d\'ivoire': 'Ivory Coast',
    'palestine': 'West Bank',
    'palestinian territories': 'West Bank',
}

TRUTHY_VISITED_VALUES = {'1', '1.0', 'true', 'yes', 'y', 'si', 'sí', 'x'}


def process_upload(file):
    """
    Processes uploaded Excel and returns a dict with:
    - 'visited': list of matched canonical country names from GEO_MAPPING
    - 'unmatched': list of country names marked visited in Excel but absent from map boundaries
    """
    try:
        df = pd.read_excel(file)
        df.columns = [str(c).strip().upper() for c in df.columns]

        if 'COUNTRY' not in df.columns or 'VISITED' not in df.columns:
            raise ValueError("Required columns: COUNTRY, VISITED")

        canonical_by_lower = {item[0].lower(): item[0] for item in GEO_MAPPING}
        matched = []
        unmatched = []
        seen_matched = set()

        for _, row in df.iterrows():
            raw_visited = row.get('VISITED')
            if pd.isna(raw_visited):
                continue
            is_visited = (
                raw_visited is True
                or raw_visited == 1
                or str(raw_visited).strip().lower() in TRUTHY_VISITED_VALUES
            )
            if not is_visited:
                continue

            raw_country = row.get('COUNTRY')
            if pd.isna(raw_country):
                continue
            clean_name = str(raw_country).strip()
            if not clean_name:
                continue

            lower_name = clean_name.lower()
            canonical = (
                canonical_by_lower.get(lower_name)
                or UPLOAD_COUNTRY_ALIASES.get(lower_name)
            )
            if canonical:
                if canonical not in seen_matched:
                    seen_matched.add(canonical)
                    matched.append(canonical)
            else:
                unmatched.append(clean_name)

        return {
            'visited': matched,
            'unmatched': unmatched,
        }
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        raise
