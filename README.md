# World Map Visualization Tool 🌎

An interactive, multi-language web application to visualize selected countries on a global map. Built with **Flask** and **Folium**, this tool allows users to track visited countries, visualize statistics by continent, and customize map aesthetics.

## ✨ Features

- **Interactive Selection**:
  - Choose countries individually via a clean accordion interface or instant search filter.
  - Bulk `ALL` / `NONE` selection toggles at both **Continent** and **Sub-Region** levels.
  - Alphabetical ordering localized dynamically to the active language across all 3 levels (Continents, Sub-Regions, and Countries).
- **Multilingual Support (15 Languages + RTL)**:
  - Arabic (`ar`, with automatic `RTL` layout), Chinese (`zh`), Danish (`da`), Dutch (`nl`), English (`en`), French (`fr`), German (`de`), Hindi (`hi`), Italian (`it`), Japanese (`ja`), Korean (`ko`), Portuguese (`pt`), Russian (`ru`), Spanish (`es`), Turkish (`tr`).
- **Data Management & Persistence**:
  - 💾 **Automatic Browser Persistence**: Remembers selected countries, language, theme, map style, and highlight color across page reloads via `localStorage`.
  - 📥 **Smart Excel Export / Template**: Downloads a blank template when no countries are selected, or exports your current selection (`VISITED = 1`) with a live counter (`📥 Download Template (N)`).
  - 📄 **Flexible Excel Import**: Recognizes common country aliases, case/whitespace variations, and multiple truthy indicators (`1`, `true`, `yes`, `si`, `x`), displaying toast notifications for loaded and unmatched entries.
- **Real-time Exact Statistics**:
  - Displays both exact counts and percentages (`visited/total (%)`) globally, per continent, and per sub-region.
- **Integrated & Resilient Map Visualization**:
  - **In-App Preview Modal**: Inspect, print/save to PDF (`🖨️`), or open in a standalone tab (`↗️`) without leaving the page.
  - **API-Key-Free Resilient Basemaps**: Light, Standard, and Dark styles backed by open Esri Canvas & OpenStreetMap layers with automatic client-side fallback and crisp vector borders for both visited and unvisited countries.
  - **High-Contrast Dark Mode**: Complete dark theme across header, statistics, action buttons, chips, and map modal.
- **Exhaustive Technical Documentation**: See [`CHANGELOG.md`](./CHANGELOG.md) for the complete engineering log of all architectural and UX improvements.

## 🚀 Tech Stack

- **Backend**: Python 3.11+, Flask.
- **Frontend**: HTML5, Tailwind CSS, JavaScript (Vanilla).
- **Mapping**: Folium (Leaflet.js wrapper).
- **Data Handling**: Pandas, OpenPyXL.
- **Containerization**: Docker.

## 📥 Installation & Setup

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ale-camer/geospacial_projects.git
   cd geospacial_projects
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or .venv\Scripts\activate on Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```
   The app will be available at `http://localhost:8080`.

### Docker Deployment

1. **Build the image**:
   ```bash
   docker build -t world-map-app .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8080:8080 world-map-app
   ```

## 📁 Project Structure

```
├── app.py                # Flask entry point
├── config/               # Geographic data and mappings
├── services/             # Backend logic (Excel & Maps)
├── templates/
│   └── index.html        # Clean HTML structure
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles & Dark Mode
│   ├── js/
│   │   ├── main.js       # App logic & event handlers
│   │   └── translations.js # Dictionary for 15 languages
│   └── bg1.png           # Assets
├── requirements.txt      # Python dependencies
└── Dockerfile            # Production deployment config
```

---
Developed by [ale-camer](https://github.com/ale-camer).
