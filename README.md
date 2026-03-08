# World Map Visualization Tool 🌎

An interactive, multi-language web application to visualize selected countries on a global map. Built with **Flask** and **Folium**, this tool allows users to track visited countries, visualize statistics by continent, and customize map aesthetics.

## ✨ Features

- **Interactive Selection**: Choose countries via a modern accordion interface or search by name.
- **Multilingual Support**: Fully translated into **15 languages**:
  - Arabic (ar), Chinese (zh), Danish (da), Dutch (nl), English (en), French (fr), German (de), Hindi (hi), Italian (it), Japanese (ja), Korean (ko), Portuguese (pt), Russian (ru), Spanish (es), Turkish (tr).
- **Data Management**:
  - 📥 **Download Template**: Get an Excel file with all available countries.
  - 📄 **Load Excel**: Upload your own visited countries list to auto-populate the map.
- **Real-time Statistics**: View the percentage of "visited" countries by Continent and Region.
- **Customization**:
  - **Map Styles**: Choose between Light (Positron), Standard (OSM), or Dark (Dark Matter).
  - **Color Picker**: Personalize the highlight color for selected countries.
  - **Dark Mode**: Seamless toggle for a premium viewing experience.
- **Modular Frontend**: Clean separation of structure (HTML), style (CSS), and logic (JS) for high maintainability.

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
