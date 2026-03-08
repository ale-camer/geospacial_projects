import re

file_path = '/home/alejandrocamerlengo/Projects/geospacial_projects/templates/index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the new translations object (formatted as it should be in the file)
new_translations = """        const translations = {
            ar: { // Arabic
                title: "خريطة العالم", desc: "تصور البلدان المختارة في جميع أنحاء العالم.",
                download: "📥 تحميل القالب", load: "📄 تحميل إكسل", fullscreen: "⛶ شاشة كاملة", clear: "✗ مسح التحديد",
                search: "بحث...", noSelection: "لا يوجد اختيار", launch: "🚀 إطلاق الخريطة",
                style: "أسلوب", color: "لون", selectAll: "الكل", deselectAll: "لا شيء",
                dataMgmt: "إدارة البيانات", selectView: "الاختيار والعرض", statTotal: "العالم",
                Africa: "أفريقيا", Americas: "الأمريكتان", Asia: "آسيا", Europe: "أوروبا", Oceania: "أوقيانوسيا"
            },
            zh: { // Simplified Chinese
                title: "世界地图", desc: "在地图上可视化全球范围内的所选国家。",
                download: "📥 下载模板", load: "📄 加载 Excel", fullscreen: "⛶ 全屏", clear: "✗ 清除选择",
                search: "搜索...", noSelection: "未选择", launch: "🚀 启动地图",
                style: "风格", color: "颜色", selectAll: "全部", deselectAll: "无",
                dataMgmt: "数据管理", selectView: "选择与视图", statTotal: "世界",
                Africa: "非洲", Americas: "美洲", Asia: "亚洲", Europe: "欧洲", Oceania: "大洋洲"
            },
            da: { // Danish
                title: "Verdenskort", desc: "Visualiser valgte lande globalt",
                download: "📥 Download skabelon", load: "📄 Indlæs Excel", fullscreen: "⛶ Fuldskærm", clear: "✗ Ryd markering",
                search: "Søg...", noSelection: "Ingen markering", launch: "🚀 Start kort",
                style: "Stil", color: "Farve", selectAll: "ALLE", deselectAll: "INGEN",
                dataMgmt: "Datastyring", selectView: "Valg & visning", statTotal: "Verden",
                Africa: "Afrika", Americas: "Amerika", Asia: "Asien", Europe: "Europa", Oceania: "Oceanien"
            },
            de: { // German
                title: "Weltkarte", desc: "Visualisieren Sie ausgewählte Länder auf der Karte.",
                download: "📥 Vorlage Laden", load: "📄 Excel Laden", fullscreen: "⛶ Vollbild", clear: "✗ Auswahl Löschen",
                search: "Suchen...", noSelection: "Keine Auswahl", launch: "🚀 Karte Starten",
                style: "Stil", color: "Farbe", selectAll: "ALLE", deselectAll: "KEINE",
                dataMgmt: "Datenverwaltung", selectView: "Auswahl und Ansicht", statTotal: "Welt",
                Africa: "Afrika", Americas: "Amerika", Asia: "Asien", Europe: "Europa", Oceania: "Ozeanien"
            },
            nl: { // Dutch
                title: "Wereldkaart", desc: "Visualiseer geselecteerde landen wereldwijd",
                download: "📥 Sjabloon downloaden", load: "📄 Excel laden", fullscreen: "⛶ Volledig scherm", clear: "✗ Selectie wissen",
                search: "Zoeken...", noSelection: "Geen selectie", launch: "🚀 Kaart starten",
                style: "Stijl", color: "Kleur", selectAll: "ALLES", deselectAll: "GEEN",
                dataMgmt: "Gegevensbeheer", selectView: "Selectie & weergave", statTotal: "Wereld",
                Africa: "Afrika", Americas: "Amerika", Asia: "Azië", Europe: "Europa", Oceania: "Oceanië"
            },
            en: { // English
                title: "World Map", desc: "Visualize selected countries across the globe.",
                download: "📥 Download Template", load: "📄 Load Excel", fullscreen: "⛶ Fullscreen", clear: "✗ Clear Selection",
                search: "Search...", noSelection: "No selection", launch: "🚀 Launch Map",
                style: "Style", color: "Color", selectAll: "ALL", deselectAll: "NONE",
                dataMgmt: "Data Management", selectView: "Selection & View", statTotal: "World",
                Africa: "Africa", Americas: "Americas", Asia: "Asia", Europe: "Europe", Oceania: "Oceania",
                "Northern Africa": "Northern Africa", "Western Africa": "Western Africa", "Eastern Africa": "Eastern Africa", "Southern Africa": "Southern Africa", "Central Africa": "Central Africa",
                "South America": "South America", "Central America": "Central America", "Caribbean": "Caribbean", "North America": "North America", "Antarctica": "Antarctica",
                "East Asia": "East Asia", "South Asia": "South Asia", "Southeast Asia": "Southeast Asia", "Central Asia": "Central Asia", "Western Asia": "Western Asia",
                "Northern Europe": "Northern Europe", "Western Europe": "Western Europe", "Central Europe": "Central Europe", "Southern Europe": "Southern Europe", "Balkans": "Balkans", "Eastern Europe": "Eastern Europe",
                "Continental": "Continental", "Islands": "Islands"
            },
            es: { // Spanish
                title: "Mapa del Mundo", desc: "Visualizá los países seleccionados en el mapa.",
                download: "📥 Descargar Plantilla", load: "📄 Cargar Excel", fullscreen: "⛶ Pantalla Completa", clear: "✗ Limpiar Selección",
                search: "Buscar...", noSelection: "Sin selección", launch: "🚀 Lanzar Mapa",
                style: "Estilo", color: "Color", selectAll: "TODO", deselectAll: "NADA",
                dataMgmt: "Gestión de Datos", selectView: "Selección y Vista", statTotal: "Mundo",
                Africa: "África", Americas: "Américas", Asia: "Asia", Europe: "Europa", Oceania: "Oceanía",
                "Northern Africa": "África del Norte", "Western Africa": "África Occidental", "Eastern Africa": "África Oriental", "Southern Africa": "África del Sur", "Central Africa": "África Central",
                "South America": "Sudamérica", "Central America": "Centroamérica", "Caribbean": "Caribe", "North America": "Norteamérica", "Antarctica": "Antártida",
                "East Asia": "Asia Oriental", "South Asia": "Asia del Sur", "Southeast Asia": "Sudeste Asiático", "Central Asia": "Asia Central", "Western Asia": "Asia Occidental",
                "Northern Europe": "Europa del Norte", "Western Europe": "Europa Occidental", "Central Europe": "Europa Central", "Southern Europe": "Europa del Sur", "Balkans": "Balcanes", "Eastern Europe": "Europa del Este",
                "Continental": "Continental", "Islands": "Islas"
            },
            fr: { // French
                title: "Carte du Monde", desc: "Visualisez les pays sélectionnés sur la carte.",
                download: "📥 Télécharger Modèle", load: "📄 Charger Excel", fullscreen: "⛶ Plein Écran", clear: "✗ Effacer Sélection",
                search: "Chercher...", noSelection: "Aucune sélection", launch: "🚀 Lancer la Carte",
                style: "Style", color: "Couleur", selectAll: "TOUT", deselectAll: "RIEN",
                dataMgmt: "Gestion des Données", selectView: "Sélection et Vue", statTotal: "Monde",
                Africa: "Afrique", Americas: "Amériques", Asia: "Asie", Europe: "Europe", Oceania: "Océanie"
            },
            hi: { // Hindi
                title: "विश्व मानचित्र", desc: "दुनिया भर में चयनित देशों की कल्पना करें।",
                download: "📥 टेम्पलेट डाउनलोड करें", load: "📄 एक्सेल लोड करें", fullscreen: "⛶ फुलस्क्रीन", clear: "✗ चयन साफ़ करें",
                search: "खोजें...", noSelection: "कोई चयन नहीं", launch: "🚀 मानचित्र लॉन्च करें",
                style: "शैली", color: "रंग", selectAll: "सभी", deselectAll: "कोई नहीं",
                dataMgmt: "डेटा प्रबंधन", selectView: "चयन और दृश्य", statTotal: "विश्व",
                Africa: "अफ़्रीका", Americas: "अमेरिका", Asia: "एशिया", Europe: "यूरोप", Oceania: "ओशिनिया"
            },
            it: { // Italian
                title: "Mappa del Mondo", desc: "Visualizza i paesi selezionati sulla mappa.",
                download: "📥 Scarica Modello", load: "📄 Carica Excel", fullscreen: "⛶ Schermo Intero", clear: "✗ Cancella Selezione",
                search: "Cerca...", noSelection: "Nessuna selezione", launch: "🚀 Lancia Mappa",
                style: "Stile", color: "Colore", selectAll: "TUTTI", deselectAll: "NESSUNO",
                dataMgmt: "Gestione Dati", selectView: "Selezione e Vista", statTotal: "Mondo",
                Africa: "Africa", Americas: "Americhe", Asia: "Asia", Europe: "Europa", Oceania: "Oceania"
            },
            ja: { // Japanese
                title: "世界地図", desc: "地図上で選択した国を視覚化します。",
                download: "📥 テンプレートをダウンロード", load: "📄 Excelを読み込む", fullscreen: "⛶ 全画面表示", clear: "✗ 選択をクリア",
                search: "検索...", noSelection: "選択なし", launch: "🚀 地図を起動",
                style: "スタイル", color: "色", selectAll: "すべて", deselectAll: "なし",
                dataMgmt: "データ管理", selectView: "選択と表示", statTotal: "世界",
                Africa: "アフリカ", Americas: "アメリカ", Asia: "アジア", Europe: "ヨーロッパ", Oceania: "オセアニア"
            },
            ko: { // Korean
                title: "세계 지도", desc: "전 세계의 선택된 국가 시각화",
                download: "📥 템플릿 다운로드", load: "📄 엑셀 불러오기", fullscreen: "⛶ 전체 화면", clear: "✗ 선택 초기화",
                search: "검색...", noSelection: "선택 없음", launch: "🚀 지도 실행",
                style: "스타일", color: "색상", selectAll: "모두", deselectAll: "없음",
                dataMgmt: "데이터 관리", selectView: "선택 및 보기", statTotal: "세계",
                Africa: "아프리카", Americas: "아메리카", Asia: "아시아", Europe: "유럽", Oceania: "오세아니아"
            },
            pt: { // Portuguese
                title: "Mapa do Mundo", desc: "Visualize os países selecionados no mapa.",
                download: "📥 Baixar Modelo", load: "📄 Carregar Excel", fullscreen: "⛶ Tela Cheia", clear: "✗ Limpar Seleção",
                search: "Pesquisar...", noSelection: "Nenhuma seleção", launch: "🚀 Lançar Mapa",
                style: "Estilo", color: "Cor", selectAll: "TODOS", deselectAll: "NENHUM",
                dataMgmt: "Gestão de Dados", selectView: "Seleção e Vista", statTotal: "Mundo",
                Africa: "África", Americas: "Américas", Asia: "Ásia", Europe: "Europa", Oceania: "Oceania"
            },
            ru: { // Russian
                title: "Карта мира", desc: "Визуализируйте выбранные страны на карте.",
                download: "📥 Скачать шаблон", load: "📄 Загрузить Excel", fullscreen: "⛶ Полный экран", clear: "✗ Очистить выбор",
                search: "Поиск...", noSelection: "Нет выбора", launch: "🚀 Запустить карту",
                style: "Стиль", color: "Цвет", selectAll: "ВСЕ", deselectAll: "НИЧЕГО",
                dataMgmt: "Управление данными", selectView: "Выбор и вид", statTotal: "Мир",
                Africa: "Африка", Americas: "Америка", Asia: "Азия", Europe: "Европа", Oceania: "Океания"
            },
            tr: { // Turkish
                title: "Dünya Haritası", desc: "Seçilen ülkeleri harita üzerinde görselleştirin.",
                download: "📥 Şablonu Иndir", load: "📄 Excel Yükle", fullscreen: "⛶ Tam Ekran", clear: "✗ Seçimi Temizle",
                search: "Ara...", noSelection: "Seçim yok", launch: "🚀 Haritayı Başlat",
                style: "Stil", color: "Renk", selectAll: "HEPSİ", deselectAll: "HİÇBİRİ",
                dataMgmt: "Veri Yönetimi", selectView: "Seçim & Görünüm", statTotal: "Dünya",
                Africa: "Afrika", Americas: "Amerikalar", Asia: "Asya", Europe: "Avrupa", Oceania: "Okyanusya"
            }
        };"""

# Regex to find the translations object from start of 'const translations' through its closing brace
# Using DOTALL to match across multiple lines
pattern = r'const translations = \{.*?        \};'
new_content = re.sub(pattern, new_translations, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Translations updated successfully.")
