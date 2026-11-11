import folium
import logging
from services.data_service import get_cached_features

logger = logging.getLogger(__name__)

# Maps UI display names or common variants → exact normalized name in world_administrative_boundaries.xlsx
# If a country isn't rendering on the map, check what name is in the xlsx and add an alias here.
COUNTRY_NAME_ALIASES = {
    'Turkey': 'Turkey',
    'Türkiye': 'Turkey',
    'Congo, Republic of ': 'Congo, Republic of',
    'Republic of the Congo': 'Congo, Republic of',
    'Congo - Brazzaville': 'Congo, Republic of',
    'Congo - Kinshasa': 'Congo, Dem. Rep. of the',
    'Democratic Republic of the Congo': 'Congo, Dem. Rep. of the',
    'China': "China, People's Republic of",
    'South Korea': 'Korea, Republic of',
    'Bahamas': 'Bahamas, The',
    'The Bahamas': 'Bahamas, The',
    'Eswatini': 'Swaziland',
    'Russia': 'Russian Federation',
    'Czechia': 'Czech Republic',
    'Slovakia': 'Slovak Republic',
    'Serbia': 'Republic of Serbia',
    'Kyrgyzstan': 'Kyrgyz Republic',
    'Timor-Leste': 'East Timor',
}

# Public, API-key-free tile endpoints (replacing CARTO endpoints that now stamp 'API KEY REQUIRED' watermarks)
TILE_PROVIDERS = {
    'light': {
        'base_url': 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
        'ref_url': 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}',
        'attr': 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ | Fallback &copy; OpenStreetMap',
    },
    'dark': {
        'base_url': 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
        'ref_url': 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}',
        'attr': 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ | Fallback &copy; OpenStreetMap',
    },
    'standard': {
        'base_url': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        'ref_url': None,
        'attr': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    },
}


def resolve_style_mode(map_style):
    """Maps UI style values ('CartoDB positron', 'CartoDB dark_matter', 'OpenStreetMap') to normalized modes."""
    style_lower = (map_style or '').strip().lower()
    if 'dark' in style_lower:
        return 'dark'
    if 'positron' in style_lower or 'light' in style_lower:
        return 'light'
    return 'standard'


def configure_resilient_basemap(m, style_mode):
    """
    Attaches API-key-free base and reference label tile layers to the Folium map.
    Avoids commercial CARTO basemaps that return 'API KEY REQUIRED' watermarks.
    """
    cfg = TILE_PROVIDERS.get(style_mode, TILE_PROVIDERS['standard'])
    folium.TileLayer(
        tiles=cfg['base_url'],
        attr=cfg['attr'],
        name=f"{style_mode.capitalize()} Base",
        control=False,
    ).add_to(m)

    if cfg.get('ref_url'):
        folium.TileLayer(
            tiles=cfg['ref_url'],
            attr=cfg['attr'],
            name=f"{style_mode.capitalize()} Labels",
            overlay=True,
            control=False,
            opacity=0.9,
        ).add_to(m)


def apply_print_injection(m, style_mode='light'):
    """
    Injects CSS, print controls, theme-matched container styling, and client-side
    automatic fallback to OpenStreetMap if primary tile servers experience errors.
    """
    is_dark = style_mode == 'dark'
    bg_color = '#1a1d24' if is_dark else '#e2e8f0'
    btn_bg = '#1e293b' if is_dark else '#ffffff'
    btn_text = '#f8fafc' if is_dark else '#0f172a'
    btn_border = '#475569' if is_dark else 'rgba(0,0,0,0.2)'

    map_html = m.get_root().render()
    head_injection = """
    <title>World Map</title>
    <link rel="icon" type="image/svg+xml" href="/static/favicon.svg">
    """
    if "</head>" in map_html:
        map_html = map_html.replace("</head>", f"{head_injection}</head>", 1)

    injection = f"""
    <style>
        .leaflet-container {{
            background-color: {bg_color} !important;
        }}
        /* CSS filter fallbacks if primary Esri tiles are unreachable and fallback to OSM triggers */
        .leaflet-container.fallback-light .leaflet-tile-pane {{
            filter: grayscale(88%) brightness(106%) contrast(92%);
        }}
        .leaflet-container.fallback-dark .leaflet-tile-pane {{
            filter: invert(100%) hue-rotate(180deg) brightness(92%) contrast(90%);
        }}
        @media print {{
            .leaflet-interactive {{
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }}
            [n-download-btn] {{ display: none !important; }}
        }}
    </style>
    <div n-download-btn style="position: fixed; top: 10px; left: 50px; z-index: 9999;">
        <button onclick="window.print()" style="padding: 8px 14px; background: {btn_bg}; color: {btn_text}; border: 1.5px solid {btn_border}; border-radius: 8px; cursor: pointer; font-weight: 700; font-family: system-ui, sans-serif; font-size: 13px; box-shadow: 0 2px 8px rgba(0,0,0,0.35);">
            🖨️ Download / Print Map
        </button>
    </div>
    <script>
        // Client-side tile resilience: if the primary tile provider fails (e.g. network block),
        // automatically switch to OpenStreetMap with matching light/dark CSS filter.
        // Hide inner floating print button when embedded inside the in-app modal preview
        (function() {{
            if (window.self !== window.top) {{
                var dlBtn = document.querySelector("[n-download-btn]");
                if (dlBtn) dlBtn.style.display = "none";
            }}
            var styleMode = "{style_mode}";
            var errorCount = 0;
            var fallbackApplied = false;
            window.addEventListener("load", function() {{
                var mapContainer = document.querySelector(".leaflet-container");
                if (!mapContainer) return;
                document.addEventListener("error", function(e) {{
                    if (fallbackApplied) return;
                    var target = e.target;
                    if (target && target.tagName === "IMG" && target.classList.contains("leaflet-tile")) {{
                        errorCount++;
                        if (errorCount >= 4 && styleMode !== "standard") {{
                            fallbackApplied = true;
                            mapContainer.classList.add("fallback-" + styleMode);
                            for (var key in window) {{
                                if (key.indexOf("tile_layer_") === 0 && window[key] && typeof window[key].setUrl === "function") {{
                                    if (window[key]._url && window[key]._url.indexOf("Reference") !== -1) {{
                                        window[key].setOpacity(0);
                                    }} else {{
                                        window[key].setUrl("https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png");
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}, true);
            }});
        }})();
    </script>
    """
    if "</body>" in map_html:
        return map_html.replace("</body>", f"{injection}</body>")
    return map_html + injection


def generate_map(selected_countries, visited_color, map_style):
    """Generates the main Folium map with resilient tiles and high-contrast highlights."""
    try:
        style_mode = resolve_style_mode(map_style)
        is_dark = style_mode == 'dark'

        m = folium.Map(location=[20, 0], zoom_start=2, tiles=None)
        configure_resilient_basemap(m, style_mode)
        features_by_country = get_cached_features()

        # High-contrast stroke & opacity tailored to Dark vs. Light/Standard basemaps
        border_color = '#f8fafc' if is_dark else '#0f172a'
        border_weight = 1.1 if is_dark else 0.9
        fill_opacity = 0.84 if is_dark else 0.78
        hover_border = '#ffffff' if is_dark else '#0f172a'

        # Unvisited country boundary styling so every country border is crisp and visible at all zoom levels
        unvisited_border_color = '#64748b' if is_dark else ('#64748b' if style_mode == 'light' else '#475569')
        unvisited_border_weight = 0.85 if is_dark else (0.8 if style_mode == 'light' else 0.6)
        unvisited_border_opacity = 0.85 if is_dark else (0.8 if style_mode == 'light' else 0.65)
        unvisited_fill_color = '#334155' if is_dark else '#94a3b8'
        unvisited_fill_opacity = 0.12 if is_dark else (0.06 if style_mode == 'light' else 0.0)

        if features_by_country:
            # Normalize selected country names through alias map
            selected_features = []
            seen = set()
            for c in (selected_countries or []):
                clean_c = c.strip() if isinstance(c, str) else c
                target = COUNTRY_NAME_ALIASES.get(clean_c) or COUNTRY_NAME_ALIASES.get(c) or clean_c
                if target in features_by_country:
                    if target not in seen:
                        seen.add(target)
                        selected_features.append(features_by_country[target])
                else:
                    logger.warning(f"Country not found in boundary data: '{c}'. Available similar: {[x for x in features_by_country if str(clean_c).lower()[:4] in x.lower()]}")

            # 1. Render crisp vector borders for all unselected countries first (base vector layer)
            unselected_features = [
                feat for name, feat in features_by_country.items() if name not in seen
            ]
            if unselected_features:
                folium.GeoJson(
                    {
                        'type': 'FeatureCollection',
                        'features': unselected_features,
                    },
                    name='Unvisited Country Borders',
                    style_function=lambda x, ubc=unvisited_border_color, ubw=unvisited_border_weight, ubo=unvisited_border_opacity, ufc=unvisited_fill_color, ufo=unvisited_fill_opacity: {
                        'fillColor': ufc,
                        'color': ubc,
                        'weight': ubw,
                        'opacity': ubo,
                        'fillOpacity': ufo,
                    },
                    highlight_function=lambda x, is_d=is_dark: {
                        'weight': 1.5,
                        'color': '#94a3b8' if is_d else '#334155',
                        'fillOpacity': 0.22,
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=['name'],
                        labels=False,
                        sticky=True,
                    ),
                ).add_to(m)

            # 2. Render highlighted polygons for visited countries on top
            if selected_features:
                feature_collection = {
                    'type': 'FeatureCollection',
                    'features': selected_features,
                }
                folium.GeoJson(
                    feature_collection,
                    name='Visited Countries',
                    style_function=lambda x, color=visited_color, bc=border_color, bw=border_weight, fo=fill_opacity: {
                        'fillColor': color,
                        'color': bc,
                        'weight': bw,
                        'opacity': 0.95,
                        'fillOpacity': fo,
                    },
                    highlight_function=lambda x, hb=hover_border: {
                        'weight': 2.2,
                        'color': hb,
                        'fillOpacity': 0.92,
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=['name'],
                        labels=False,
                        sticky=True,
                    ),
                ).add_to(m)

        return apply_print_injection(m, style_mode=style_mode)
    except Exception as e:
        logger.error(f"Map generation error: {e}")
        raise
