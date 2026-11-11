# Registro de Cambios y Documentación Técnica (`CHANGELOG.md`)

Este documento registra de forma exhaustiva todas las mejoras, correcciones y decisiones técnicas aplicadas sobre la aplicación **World Map Visualization Tool**.

---

## Flujo de Trabajo y Entornos

- **Rama de Producción (`PROD`):** `Finance` (sincronizada con `origin/Finance` y preparada para despliegue en GCP Cloud Run vía `Dockerfile` + `gunicorn`). No se modifica directamente.
- **Rama de Desarrollo (`DEV`):** `dev` (aislada localmente para implementar, probar y validar **un cambio a la vez**).
- **Servidor Local `DEV`:** Ejecutándose con recarga activa (`DEBUG=true`) en `http://localhost:8081` (se usa `8081` para no interferir con otros servicios locales en `8080`).
- **Regla de avance:** Cada cambio se implementa individualmente en `dev`, se documenta en este archivo y en el código fuente, y **solo se avanza al siguiente ítem tras aprobación explícita**.

---

## Hoja de Ruta de Cambios

| # | Cambio | Categoría | Estado |
|---|--------|-----------|--------|
| **1** | Selección y traducción segura de nombres con apóstrofes (`China, People's Republic of`) | Bug funcional | ✅ **Aprobado** |
| **2** | Preservar países seleccionados, paneles abiertos y filtro al cambiar de idioma | Bug funcional | ✅ **Aprobado** |
| **3** | Consistencia geográfica en Antártida, limpieza de nombres (`strip`/`Intl` en inglés) y desambiguación ISO (`Northern Cyprus` / `Somaliland`) | Datos / Bug | ✅ **Aprobado** |
| **4** | Corregir altura del acordeón al salir de Pantalla Completa (`Fullscreen`) | Bug visual | ✅ **Aprobado** |
| **5** | Modo Oscuro (`Dark Mode`) completo y contraste de tonos (Header, Stats, Botones, Chips, Scrollbar) | UI / Estilos | ✅ **Aprobado** |
| **6** | Resiliencia de estilos de mapa (`Light` y `Dark` sin requerir API Key de CARTO + buen contraste de polígonos) | Mapa / Resiliencia | ✅ **Aprobado** |
| **7** | Ordenamiento alfabético de continentes, subclasificaciones y países manteniendo el layout original | UI / Estructura | ✅ **Aprobado** |
| **8** | Favicon e ícono propio de la aplicación (en header, pestaña principal y pestaña del mapa) | UI / Identidad | ✅ **Aprobado** |
| **9** | Corrección de traducciones corruptas, subregiones y estilos en 15 idiomas, `ALL/NONE` y soporte `RTL` | Internacionalización | ✅ **Aprobado** |
| **10** | Persistencia en `localStorage` y exportación de selección actual a Excel (`#` en botón) | UX esencial | ✅ **Aprobado** |
| **11** | Botón `ALL/NONE` (`TODO/NADA`) también a nivel Continente | UX / Selección | ✅ **Aprobado** |
| **12** | Mostrar conteo exacto (`X / Y`) junto al porcentaje en estadísticas (Mundo, Continente y Subregión) | UX esencial | ✅ **Aprobado** |
| **13** | Normalización flexible al subir Excel y notificaciones claras de países cargados/omitidos | UX / Datos | ✅ **Aprobado** |
| **14** | Previsualización integrada del mapa (modal con impresión y apertura en pestaña nueva) | UX / Mapa | ✅ **Aprobado** |
| **15** | Optimización de `generate_map()` (caché de geometrías parseadas + único `FeatureCollection`) | Rendimiento | ✅ **Aprobado** |
| **16** | Fronteras vectoriales nítidas para países no seleccionados en el mapa | UX / Mapa | ✅ **Aprobado** |
| **17** | Seguridad de subida (`MAX_CONTENT_LENGTH`), optimización de fondo WebP y `.dockerignore` | Seguridad / PROD | ✅ **Aprobado** |
| **18** | Subtítulo con misión clara y barra guía de 3 pasos en los 15 idiomas | UX / Onboarding | ✅ **Aprobado** |
| **19** | Prioridad visual al buscador/selección y estado vacío explicativo en `#no-selection` | UX / Jerarquía | ✅ **Aprobado** |
| **20** | Etiquetas contextuales (`📥 Descargar Plantilla` ↔ `💾 Exportar Excel (N)`) y traducción de botones del visor | UX / Microcopy | ✅ **Aprobado** |
| **21** | Contador dinámico en `🚀 Launch Map (N)` y aviso al lanzar sin países seleccionados | UX / Feedback | ✅ **Aprobado** |

---

## Detalle Técnico de Cambios Implementados

### [Cambio #1] Selección y traducción segura de países con caracteres especiales (`China, People's Republic of`)

- **Fecha:** 2026-11-10
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario (validado con capturas en UI y en `/view_map`)

#### 1. Problema detectado y causa raíz
1. **Ruptura de sintaxis JavaScript en eventos inline:**
   En `config/constants.py`, China está registrada como `"China, People's Republic of"` para coincidir exactamente con la clave de `world_administrative_boundaries.xlsx`. En `static/js/main.js`, tanto `render()` como `updateChips()` construían botones HTML interpolando el nombre directamente dentro de comillas simples de JavaScript:
   ```html
   onclick="toggleCountry('China, People's Republic of')"
   ```
   El apóstrofe en `People's` cerraba prematuramente el literal de texto en JavaScript, lanzando un `Uncaught SyntaxError: missing ) after argument list` al intentar seleccionar China en el acordeón o al intentar eliminar su chip activo con el botón `×`.
2. **Ausencia de código ISO para traducción:**
   En `static/js/translations.js`, el objeto `countryIsoCodes` omitía la entrada `"China, People's Republic of": 'CN'`, provocando que `getTranslatedCountryName()` devolviera siempre el nombre técnico en inglés sin importar el idioma seleccionado en la interfaz.

#### 2. Solución técnica aplicada
- **Sanitización HTML (`escapeHtml`):** Se incorporó la función auxiliar `escapeHtml(str)` en `static/js/main.js` para escapar `&`, `"`, `'`, `<` y `>` antes de inyectar valores dinámicos en atributos o nodos de texto HTML (previniendo además inyecciones accidentales en el DOM).
- **Desacoplamiento de datos mediante `data-*` (`HTMLElement.dataset`):**
  - En los botones de país dentro de `render()` y en el botón `×` dentro de `updateChips()`, se reemplazó `onclick="toggleCountry('${c.name}')"` por:
    ```html
    data-country="${safeName}" onclick="toggleCountry(this.dataset.country)"
    ```
  - Del mismo modo, en los botones regionales de selección masiva (`toggleRegion`), se reemplazó la interpolación inline por `data-continent` y `data-region` leídos desde `this.dataset`.
  - El navegador decodifica automáticamente las entidades HTML (`&#39;` → `'`) al acceder a `this.dataset.country`, entregando el string exacto `"China, People's Republic of"` a `toggleCountry()`, `document.getElementById('chip-' + name)` y `<option value="...">` sin evaluar nunca el nombre como código JavaScript.
- **Mapeo ISO 3166-1 alpha-2:** Se añadió `"China, People's Republic of": 'CN'` en `countryIsoCodes` (`static/js/translations.js`), habilitando su traducción nativa automática mediante `Intl.DisplayNames` en los 14 idiomas distintos del inglés (ej. *China* en español, *Chine* en francés, *中国* en chino/japonés).

#### 3. Archivos modificados
- `static/js/main.js`:
  - Nueva función documentada `escapeHtml(str)`.
  - Refactorización de generación de plantillas en `render()` y `updateChips()`.
- `static/js/translations.js`:
  - Incorporación de `"China, People's Republic of": 'CN'` y documentación del diccionario `countryIsoCodes`.

#### 4. Guía de verificación en `DEV` (`http://localhost:8081`)
1. Abrir `http://localhost:8081`, desplegar **Asia** → **East Asia** y hacer clic en **China, People's Republic of**: debe marcarse en azul índigo, agregarse a la caja de chips seleccionados y subir el porcentaje de *East Asia*, *Asia* y *World*.
2. Hacer clic en la `×` del chip activo de China: debe desmarcarse limpiamente sin errores en la consola del navegador (`F12`).
3. Cambiar el idioma a **Español** (o cualquier otro), abrir **Asia** → **Asia Oriental**: debe figurar traducido como **China** y permitir seleccionarse/deseleccionarse normalmente.
4. Con China seleccionada, pulsar **Launch Map**: el mapa Folium debe abrirse con el polígono de China coloreado correctamente.

---

### [Cambio #2] Preservar países seleccionados, paneles abiertos y filtro activo al cambiar de idioma

- **Fecha:** 2026-11-10
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario

#### 1. Problema detectado y causa raíz
1. **Pérdida total de la selección al cambiar de idioma:**
   En `static/js/main.js`, la función `changeLanguage(lang)` invocaba `render()`, la cual sobreescribía `select.innerHTML = options` desde cero con etiquetas `<option>` sin el atributo `selected`. Al ejecutarse inmediatamente después `updateChips()` y `updateStats()`, `select.selectedOptions` estaba vacío, borrando todos los países que el usuario había marcado.
2. **Colapso de paneles abiertos y pérdida del estado visual del chip en el acordeón:**
   - `render()` reconstruía todos los contenedores `.continent-content` con la clase `hidden`, cerrando los continentes que el usuario tenía desplegados.
   - Además, al seleccionar un país (`toggleCountry` / `toggleRegion`), se agregaba `bg-indigo-500` sin quitar `bg-white`. En Modo Oscuro (`body.dark`), el selector `body.dark .bg-white` tenía mayor especificidad CSS (`0,2,1`) que `.bg-indigo-500` (`0,1,0`), impidiendo que el botón del país dentro del acordeón se viera pintado de azul/índigo al estar seleccionado (visible en la captura de validación del Cambio #1).

#### 2. Solución técnica aplicada
- **Captura y restauración de estado en `render()`:**
  - Antes de regenerar el DOM, se capturan en un `Set` los valores de `select.selectedOptions` (`previouslySelected`) y los IDs de los continentes actualmente abiertos (`expandedContinents`).
  - Al construir cada `<option>` y cada `<button id="chip-...">`, se verifica `previouslySelected.has(c.name)` para inyectar el atributo `selected` y aplicar las clases activas (`bg-indigo-500 text-white border-indigo-600`) o inactivas (`bg-white border-gray-200`) de forma mutuamente excluyente.
  - Se restaura el estado expandido (`hidden` / `rotate-180`) de cada continente abierto y, en `changeLanguage()`, se vuelve a aplicar `filterCountries()` si había texto escrito en el buscador (`#search`).
- **Exclusión mutua de clases de fondo (`bg-white` vs `bg-indigo-500`):**
  - En `toggleCountry()`, `toggleRegion()` y `clearSelection()`, se alterna explícitamente `bg-white` y `border-gray-200` en sentido inverso a `bg-indigo-500`, evitando que `body.dark .bg-white` pise el color de selección del chip en Modo Oscuro.

#### 3. Archivos modificados
- `static/js/main.js`:
  - [`render()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L36-L99)
  - [`toggleCountry()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L101-L116)
  - [`toggleRegion()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L118-L137)
  - [`clearSelection()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L245-L252)
  - [`changeLanguage()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L304-L343)

#### 4. Guía de verificación en `DEV` (`http://localhost:8081`)
1. Recargar `http://localhost:8081` (`Ctrl+Shift+R`), seleccionar varios países (por ejemplo **China**, **Argentina** y **Spain**) y dejar un continente desplegado.
2. Cambiar el selector de idioma arriba a la derecha (ej. de **🇺🇸 English** a **🇪🇸 Español** o **🇫🇷 Français**):
   - Los países deben seguir seleccionados, con sus nombres traducidos tanto en los chips superiores (`China ×`, `Argentina ×`, `España ×`) como dentro del acordeón, manteniendo los porcentajes intactos.
   - Además, en Modo Oscuro, el botón del país dentro del acordeón (`EAST ASIA`) ahora sí se pinta de azul índigo cuando está seleccionado.

---

### [Cambio #3] Consistencia geográfica en Antártida, nombres amigables en inglés y desambiguación de territorios

- **Fecha:** 2026-11-10
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario

#### 1. Problema detectado y causa raíz
1. **Continente huérfano `Antarctica` vs subregión `Antarctica`:**
   En `config/constants.py`, `'Antarctica'` estaba asignada a `('Antarctica', 'Americas', 'Antarctica')`, mientras que `'French Southern and Antarctic Lands'` estaba en `('French Southern and Antarctic Lands', 'Antarctica', 'Antarctica')`. Esto creaba un sexto acordeón de continente llamado `Antarctica` que contenía únicamente a las Tierras Australes Francesas (sin la Antártida misma) y que no figuraba en la barra superior de estadísticas (`#stats-summary`).
2. **Espacio en blanco al final de `'Congo, Republic of '`:**
   Tanto en `config/constants.py` como en `world_administrative_boundaries.xlsx`, el nombre tenía un espacio final (`'Congo, Republic of '`), propenso a fallar al cruzar datos o subir archivos Excel limpios.
3. **Nombres crudos de shapefile en Inglés (`lang === 'en'`):**
   En `static/js/translations.js`, `getTranslatedCountryName()` tenía `if (lang === 'en') return englishName;`, devolviendo nombres técnicos crudos del dataset GIS (`"China, People's Republic of"`, `"Bahamas, The"`, `"Korea, Republic of"`, `"Swaziland"`, `"Russian Federation"`, `"Slovak Republic"`) en vez de nombres naturales (`"China"`, `"Bahamas"`, `"South Korea"`, `"Eswatini"`, `"Russia"`, `"Slovakia"`).
4. **Colisión de códigos ISO en `Northern Cyprus` y `Somaliland`:**
   Ambos compartían código ISO con `'Cyprus'` (`'CY'`) y `'Somalia'` (`'SO'`), por lo que `Intl.DisplayNames` generaba dos botones con el mismo nombre exacto (*Chipre* / *Chipre* y *Somalia* / *Somalia*).
5. **Orden alfabético al traducir:**
   Los países se ordenaban en el backend según su clave en inglés, quedando desordenados alfabéticamente cuando el usuario cambiaba a otro idioma (ej. *Alemania* aparecía en la *G* de *Germany*).

#### 2. Solución técnica aplicada
- **Unificación de subregión Antártida:** En `config/constants.py`, `'French Southern and Antarctic Lands'` se ubicó junto a `'Antarctica'` bajo `('Americas', 'Antarctica')`, alineando los 5 continentes del acordeón con los 5 continentes de `#stats-summary`.
- **Normalización de espacios (`strip`):**
  - Se eliminó el espacio final de `'Congo, Republic of'` en `config/constants.py` y `static/js/translations.js`.
  - En `services/data_service.py` (`get_world_data()`), se aplica `.str.strip()` sobre la columna `COUNTRY` al cargar `world_administrative_boundaries.xlsx` en caché.
  - En `services/map_service.py`, se amplió `COUNTRY_NAME_ALIASES` con nombres comunes y variantes limpias (`China`, `South Korea`, `Bahamas`, `Eswatini`, `Russia`, `Czechia`, `Slovakia`, `Serbia`, `Kyrgyzstan`, `Timor-Leste`, `Congo, Republic of `, etc.).
- **Nombres limpios en todos los idiomas (incluido Inglés) y desambiguación:**
  - En `static/js/translations.js`, `getTranslatedCountryName()` ahora utiliza `Intl.DisplayNames([lang], { type: 'region' })` también para `en`, mostrando nombres limpios y modernos (`China`, `South Korea`, `Bahamas`, `Eswatini`, `Russia`, `Czechia`, `Slovakia`) sin alterar la clave interna (`c.name`) usada para cruzar con el mapa.
  - Se creó el diccionario `customTerritoryNames` para `'Northern Cyprus'` y `'Somaliland'` en los 15 idiomas, evitando su colisión con `'Cyprus'` y `'Somalia'`.
- **Ordenamiento alfabético localizado:** En `static/js/main.js` (`render()`), los países de cada subregión se ordenan dinámicamente con `localeCompare(..., currentLang)` según su nombre traducido.

#### 3. Archivos modificados
- [`config/constants.py`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/config/constants.py#L42-L66)
- [`services/data_service.py`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/data_service.py#L12-L24)
- [`services/map_service.py`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/map_service.py#L8-L72)
- [`static/js/translations.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/translations.js#L134-L176)
- [`static/js/main.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L66-L80)

#### 4. Guía de verificación en `DEV` (`http://localhost:8081`)
1. Refrescar `http://localhost:8081` (`Ctrl+Shift+R`).
2. En **Inglés** (`🇺🇸 English`), abrir **Asia → East Asia**: ahora se lee directamente **China** y **South Korea** (en vez de `China, People's Republic of` y `Korea, Republic of`). En **Americas → Caribbean** se lee **Bahamas**, y en **Africa → Southern Africa** se lee **Eswatini**.
3. Verificar que ya no existe un sexto continente suelto llamado `Antarctica` al final del acordeón (ambos territorios antárticos están juntos en **Americas → Antarctica**).
4. En **Asia → Western Asia**, verificar que aparecen diferenciados **Cyprus** y **Northern Cyprus** (o **Chipre** y **Chipre del Norte** en Español); y en **Africa → Eastern Africa**, **Somalia** y **Somaliland** (**Somalilandia** en Español).
5. Verificar que dentro de cada región los países aparecen ordenados alfabéticamente según el idioma activo.

---

### [Cambio #4] Restauración correcta de la altura del acordeón al salir de Pantalla Completa (`Fullscreen`)

- **Fecha:** 2026-11-10
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario

#### 1. Problema detectado y causa raíz
En `templates/index.html`, el contenedor `#accordion` tiene definida por diseño la clase de Tailwind `max-h-[32rem]` (`512px`). Sin embargo, en `static/js/main.js`, el listener del evento `fullscreenchange` asignaba un estilo inline `accordion.style.maxHeight = '16rem'` (`256px`) al salir de pantalla completa (`!document.fullscreenElement`). Como los estilos inline tienen prioridad sobre las clases CSS, el acordeón quedaba permanentemente reducido a la mitad de su tamaño original durante el resto de la sesión.

#### 2. Solución técnica aplicada
- En el listener `fullscreenchange` de `static/js/main.js`:
  - Cuando se activa pantalla completa (`Boolean(document.fullscreenElement)`), se aplica `accordion.style.maxHeight = '70vh'` para aprovechar el alto de la pantalla.
  - Al salir de pantalla completa (ya sea con el botón o con la tecla `Esc`), se limpia la propiedad inline (`accordion.style.maxHeight = ''`), devolviendo el control a la clase original `max-h-[32rem]` de `index.html`.
  - Adicionalmente, se alterna un borde de estado activo (`ring-2 ring-indigo-400`) sobre `#btn-fullscreen` mientras el modo de pantalla completa está activo.

#### 3. Archivos modificados
- [`static/js/main.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L265-L279)

#### 4. Guía de verificación en `DEV` (`http://localhost:8081`)
1. Refrescar `http://localhost:8081` (`Ctrl+Shift+R`) y abrir un continente grande (por ejemplo **Africa** o **Asia**) para observar el alto normal del acordeón (`32rem`).
2. Hacer clic en **⛶ Fullscreen**: la app pasa a pantalla completa, el acordeón se expande a `70vh` y el botón muestra el indicador activo.
3. Salir de pantalla completa (volviendo a tocar **⛶ Fullscreen** o presionando `Esc`): el acordeón recupera exactamente su altura original de `32rem` en vez de achicarse a la mitad (`16rem`).

---

### [Cambio #5] Modo Oscuro (`Dark Mode`) completo y contraste de tonos en toda la interfaz

- **Fecha:** 2026-11-10
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario

#### 1. Problema detectado y causa raíz
En `static/css/style.css`, el Modo Oscuro (`body.dark`) solo tenía 5 reglas genéricas (`.bg-white`, `.bg-gray-50`, `.bg-gray-100`, `.border-gray-200`, `input/select`), dejando múltiples componentes con bajo contraste o colores claros sin adaptar:
1. **Header (`<header>`):** Usaba `bg-white/70` (no alcanzado por `.bg-white`), quedando gris claro con título oscuro (`#card-title` en `text-gray-800`).
2. **Barra de estadísticas (`#stats-summary`):** Mantenía `bg-indigo-50/50` con textos `text-gray-400` y `text-gray-700`, volviéndose grisácea y de muy baja legibilidad.
3. **Botones de herramientas (`#btn-download`, `#btn-load`, `#btn-fullscreen`, `#btn-clear`):** Conservaban colores de texto oscuros (`text-green-700`, `text-gray-700`, `text-indigo-700`, `text-red-700`) sobre fondo oscuro (`#1f2937`), siendo especialmente ilegible el botón `Load Excel`.
4. **Chips seleccionados (`#active-chips > div`) y bordes de subregión (`.border-gray-50`):** Los chips activos quedaban con fondo blanco-lavanda (`bg-indigo-50`) encandilante y las cajas de subregión conservaban un borde blanco (`border-gray-50`), al igual que el track del scrollbar (`#f1f1f1`).

#### 2. Solución técnica aplicada
Se rediseñó integralmente la paleta de Modo Oscuro en `static/css/style.css` (basada en tonos Slate/Indigo de alto contraste WCAG AA/AAA):
- **Header oscuro translúcido:** Fondo `rgba(15, 23, 42, 0.88)` con borde `#334155`, título en `#f8fafc` y subtítulo en `#cbd5e1`.
- **Banner de estadísticas (`#stats-summary`):** Fondo índigo profundo (`rgba(30, 27, 75, 0.65)`), porcentaje mundial en blanco puro (`#ffffff`), etiqueta `WORLD` en `#a5b4fc`, nombres de continentes en `#cbd5e1` y valores en `#f8fafc`.
- **Botones de acción con tonos luminosos semánticos:**
  - `#btn-download`: verde esmeralda claro (`#6ee7b7`) sobre fondo esmeralda translúcido (`rgba(6, 78, 59, 0.35)`).
  - `#btn-load`: texto claro (`#f1f5f9`) y borde `#475569` con hover nítido (`#334155`).
  - `#btn-fullscreen`: índigo luminoso (`#a5b4fc`) sobre `rgba(49, 46, 129, 0.4)`.
  - `#btn-clear`: rojo coral claro (`#fca5a5`) sobre `rgba(127, 29, 29, 0.35)`.
- **Chips activos y acordeón:**
  - Chips en `#active-chips`: fondo índigo translúcido (`rgba(79, 70, 229, 0.28)`), borde `#818cf8` y texto `#e0e7ff`.
  - Cajas `.region-container`: borde unificado `#334155` (eliminando el borde blanco de `.border-gray-50`), títulos en `#cbd5e1` y botones de país con estados inactivo (`#1e293b` / texto `#e2e8f0`), hover (`#334155` / borde `#818cf8`) y seleccionado (`#4f46e5` / texto `#ffffff`).
  - Scrollbar adaptado a oscuro (`track: #0f172a`, `thumb: #475569`).

#### 3. Archivos modificados
- [`static/css/style.css`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/css/style.css#L41-L234)

#### 4. Guía de verificación en `DEV` (`http://localhost:8081`)
1. Refrescar `http://localhost:8081` (`Ctrl+Shift+R`) y activar el **Modo Oscuro** con el botón 🌙/☀️ arriba a la derecha.
2. Comprobar el contraste de:
   - El **Header** superior (ahora oscuro con título blanco).
   - La **barra de estadísticas** (`WORLD` y los 5 continentes ahora resaltan con claridad).
   - Los **4 botones de acción** (`Download Template`, `Load Excel`, `Fullscreen`, `Clear Selection`), especialmente `Load Excel`.
   - Los **chips seleccionados** arriba y los botones de países/subregiones dentro del acordeón.

---

### [Cambio #6] Resiliencia de estilos de mapa (`Light` y `Dark` sin API Key) y alto contraste de polígonos

- **Fecha:** 2026-11-10
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario

#### 1. Problema detectado y causa raíz
1. **Marca de agua `API KEY REQUIRED` en estilos `Light` y `Dark`:**
   Los presets de Folium `CartoDB positron` y `CartoDB dark_matter` apuntan a `https://{s}.basemaps.cartocdn.com/light_all/...` y `dark_all/...`. Los servidores de CARTO comenzaron a responder con tiles marcados con `etag: "wm-...-light/dark"` y una estampa diagonal **"API KEY REQUIRED - carto.com/basemaps/apikey"**.
2. **Bajo contraste de países coloreados sobre el mapa oscuro:**
   En `services/map_service.py`, `folium.GeoJson` aplicaba siempre un borde negro (`'color': 'black'`, `'weight': 0.5`) y opacidad `0.7`. En un mapa oscuro (`Dark`), el borde negro se fundía con el fondo gris oscuro de los continentes y hacía perder definición entre países limítrofes.

#### 2. Solución técnica aplicada
- **Arquitectura de Tiles de Doble Capa sin API Key + Fallback Automático (`services/map_service.py`):**
  - Se creó [`TILE_PROVIDERS`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/map_service.py#L32-L48) y [`configure_resilient_basemap()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/map_service.py#L60-L82), inicializando `folium.Map(..., tiles=None)` y montando proveedores públicos abiertos sin API Key:
    - **Light (`CartoDB positron`):** Esri *World Light Gray Base* + *World Light Gray Reference* (capa de etiquetas nítidas).
    - **Dark (`CartoDB dark_matter`):** Esri *World Dark Gray Base* + *World Dark Gray Reference*.
    - **Standard (`OpenStreetMap`):** OpenStreetMap oficial.
  - **Resiliencia en cliente ante fallos de red (`apply_print_injection`):** Se inyectó un monitor de eventos de error sobre `.leaflet-tile`. Si un proveedor primario fallara o fuera bloqueado por firewall (`>= 4` tiles con error), el mapa conmuta automáticamente en caliente las URLs a `tile.openstreetmap.org` y aplica filtros CSS equivalentes (`.fallback-light` o `.fallback-dark`) sobre `.leaflet-tile-pane` para que el mapa nunca quede en blanco ni pida API Keys.
- **Contraste adaptativo de polígonos y controles:**
  - En modo **Dark**, los polígonos usan borde claro (`#f8fafc`, `weight: 1.0`) y mayor saturación (`fillOpacity: 0.82`), contenedor de fondo `#1a1d24` (sin destellos blancos al hacer zoom) y botón flotante `🖨️ Download / Print Map` adaptado en modo oscuro (`#1e293b` / `#f8fafc`).
  - Se añadió `highlight_function` en todos los estilos para resaltar el país al pasar el cursor (`weight: 2.2`, `fillOpacity: 0.92`).

#### 3. Archivos modificados
- [`services/map_service.py`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/map_service.py#L31-L197)

#### 4. Guía de verificación en `DEV` (`http://localhost:8081`)
1.En `http://localhost:8081`, seleccionar varios países (ej. varios limítrofes en Europa o Sudamérica).
2. Elegir **Style: Light** y pulsar **🚀 Launch Map**: verificar que el mapa claro carga limpio, con etiquetas y **sin** el texto `API KEY REQUIRED`.
3. Volver, elegir **Style: Dark** y pulsar **🚀 Launch Map**: verificar que el mapa oscuro carga sin pedir API Key, que los países seleccionados resaltan con borde claro nítido (especialmente entre países vecinos), que al pasar el mouse se iluminan y que el botón de impresión acompaña el tono oscuro.

---

### [Cambio #7] Ordenamiento alfabético completo (continentes, subclasificaciones y países) sobre el layout original

- **Fecha:** 2026-11-11
- **Rama:** `dev`
- **Estado:** ✅ Ajustado según preferencia del usuario

#### 1. Problema detectado y ajuste solicitado
El usuario prefirió conservar el diseño original de columna única (`max-w-5xl`, `space-y-2`, proporciones originales de botones y chips) en lugar de una grilla multicolumna para las subregiones, solicitando que tanto los **continentes** como cada **subclasificación (subregión)** y sus **países** aparezcan ordenados alfabéticamente según el idioma activo.

#### 2. Solución técnica aplicada
- Se restauró en `templates/index.html`, `static/css/style.css` y `static/js/main.js` el layout original de columna única (`max-w-5xl` y `max-h-[32rem]`).
- En [`render()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L54-L90) se incorporó ordenamiento alfabético localizado (`localeCompare(..., currentLang)`) en los **3 niveles jerárquicos**:
  1. **Continentes** (`sortedContinents`).
  2. **Subclasificaciones / Subregiones** dentro de cada continente (`sortedRegions`).
  3. **Países** dentro de cada subclasificación (`localizedCountries`).

#### 3. Archivos modificados
- [`static/js/main.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L54-L108)
- [`templates/index.html`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/templates/index.html)
- [`static/css/style.css`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/css/style.css)

---

### [Cambio #8] Favicon e ícono propio de la aplicación

- **Fecha:** 2026-11-11
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario

#### 1. Problema detectado y causa raíz
La aplicación carecía de `<link rel="icon">` tanto en la página principal (`templates/index.html`) como en la vista generada del mapa (`/view_map` en `services/map_service.py`), por lo que el navegador mostraba el ícono genérico vacío en las pestañas y usaba un emoji de texto (`🌎`) en el encabezado.

#### 2. Solución técnica aplicada
- Se diseñó y creó [`static/favicon.svg`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/favicon.svg), un ícono vectorial liviano que representa el globo terráqueo con grilla cartográfica, continentes en verde esmeralda, océano con gradiente índigo-azul acorde a la identidad visual de la app y un pin de ubicación.
- En [`templates/index.html`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/templates/index.html#L8-L21), se enlazó `favicon.svg` como `<link rel="icon" type="image/svg+xml">` en el `<head>` y como ícono principal del header.
- En [`services/map_service.py`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/map_service.py#L96-L103) (`apply_print_injection`), se inyectó también `<title>World Map</title>` y `<link rel="icon" type="image/svg+xml" href="/static/favicon.svg">` dentro del `<head>` del documento Folium para que la pestaña del mapa comparta el mismo ícono y título.

#### 3. Archivos creados / modificados
- [`static/favicon.svg`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/favicon.svg) *(nuevo)*
- [`templates/index.html`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/templates/index.html#L8-L21)
- [`services/map_service.py`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/map_service.py#L96-L103)

#### 4. Guía de verificación en `DEV` (`http://localhost:8081`)
1. Refrescar `http://localhost:8081` (`Ctrl+Shift+R`):
   - Verificar que el layout volvió a cómo estaba antes y que tanto los continentes como cada subclasificación interna están ordenados alfabéticamente.
   - Mirar la pestaña del navegador y el encabezado superior izquierdo: ahora lucen el nuevo ícono vectorial del mapa.
2. Hacer clic en **🚀 Launch Map**: verificar que la nueva pestaña de `/view_map` también muestra el título `World Map` y el mismo ícono en la pestaña del navegador.

---

### [Cambio #9] Corrección de traducciones corruptas, 22 subregiones y estilos de mapa en los 15 idiomas, botón `ALL`/`NONE` y soporte `RTL`

- **Fecha:** 2026-11-11
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario

#### 1. Problema detectado y causa raíz
1. **Caracteres corruptos y mezcla de idiomas en `static/js/translations.js`:**
   - **Turco (`tr`):** Contenía caracteres cirílicos en `Şablonu Иndir` (`И` en lugar de `İ`) y `HİЧБИРИ` (`ЧБИР` en lugar de `HİÇBİRİ`).
   - **Hindi (`hi`):** La palabra `Africa` (`अफ़्रीکا`) terminaba con letras árabes (`کا`) en lugar de devanagari (`का`).
   - **Japonés (`ja`):** Mezclaba inglés en `desc` (`選択した country`) y caracteres de chino simplificado en `dataMgmt` (`数据管理`) y `selectView` (`选择与表示`).
   - **Francés (`fr`) y Portugués (`pt`):** Mezclaban palabras en español (`Effacer Selección`, `Aucune selección`, `Nenhuma selección`, `Gestão de Datos`, `Selección y Vista`).
2. **Subregiones y estilos de mapa sin traducir:**
   - Las 22 subclasificaciones geográficas solo estaban traducidas en `en` y `es` (en los otros 13 idiomas quedaban en inglés).
   - Las opciones del selector de estilo del mapa (`Light`, `Standard`, `Dark`) no se traducían nunca.
3. **Botón `ALL` (`selectAll`) estático:**
   - Aunque los 15 idiomas definían `deselectAll` (`NONE` / `NADA` / `RIEN`), la clave nunca se utilizaba; aun con toda una subregión seleccionada al 100%, el botón seguía mostrando `ALL`.
4. **Falta de dirección `RTL` en Árabe (`ar`):**
   - Al elegir Árabe no se actualizaba `document.documentElement.dir = 'rtl'`.

#### 2. Solución técnica aplicada
- Se corrigieron todas las cadenas corruptas en `fr`, `hi`, `ja`, `pt` y `tr` dentro de [`static/js/translations.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/translations.js#L1-L212).
- Se agregaron las traducciones de las **22 subregiones** y de los **3 estilos de mapa** (`styleLight`, `styleStandard`, `styleDark`) en los **15 idiomas**.
- En [`templates/index.html`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/templates/index.html#L171-L176) se añadieron IDs (`opt-style-light`, `opt-style-standard`, `opt-style-dark`) actualizados desde [`changeLanguage()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L334-L380), junto con `document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr'`.
- En [`render()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L88-L96) y [`updateStats()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L202-L215), el botón de cada subregión alterna automáticamente entre `selectAll` (`ALL` / `TODO`) y `deselectAll` (`NONE` / `NADA`) cuando todos sus países están marcados.

#### 3. Archivos modificados
- [`static/js/translations.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/translations.js#L1-L212)
- [`static/js/main.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L88-L380)
- [`templates/index.html`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/templates/index.html#L171-L176)

#### 4. Guía de verificación en `DEV` (`http://localhost:8081`)
1. Refrescar `http://localhost:8081` (`Ctrl+Shift+R`), abrir cualquier continente y hacer clic en **ALL** (`TODO`) en una subregión: todos sus países se seleccionan y el botón cambia automáticamente a **NONE** (`NADA`).
2. Cambiar el idioma a **Francés**, **Portugués**, **Japonés**, **Turco** o **Árabe**:
   - Verificar que todas las subclasificaciones internas y el selector de estilo del mapa (`Claro / Estándar / Oscuro`) se traducen y se reordenan alfabéticamente en ese idioma.
   - En **Árabe (`🇸🇦 العربية`)**, verificar que la interfaz se alinea de derecha a izquierda (`RTL`).

---

### [Cambio #10] Persistencia automática en `localStorage` y exportación de selección actual a Excel

- **Fecha:** 2026-11-11
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario

#### 1. Problema detectado y causa raíz
1. **Pérdida de progreso al recargar o cerrar la página:**
   Anteriormente solo el tema visual (`theme`) se guardaba en `localStorage`. Si el usuario seleccionaba países, elegía un idioma, cambiaba el estilo del mapa o personalizaba el color y recargaba la página (`F5`), perdía toda su configuración y selección.
2. **Imposibilidad de exportar los países seleccionados a Excel:**
   El endpoint `/api/download_template` y `generate_template_buffer()` siempre generaban un archivo Excel con `VISITED = 0` en todos los países, impidiendo que un usuario que armó su selección desde la web pudiera descargarla como respaldo para volver a cargarla más adelante.

#### 2. Solución técnica aplicada
- **Persistencia en cliente (`static/js/main.js` y `templates/index.html`):**
  - Se creó [`savePreferences()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L27-L42), invocada automáticamente al modificar países (`updateChips`), idioma (`changeLanguage`), estilo de mapa (`#map-style-select`) o color (`#visited-color-input`).
  - En [`init()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L44-L88) se restauran `lang`, `mapStyle`, `visitedColor` y `selectedCountries` desde `localStorage` antes de mostrar la interfaz.
- **Exportación inteligente de Excel (`services/data_service.py`, `app.py`, `static/js/main.js`):**
  - [`generate_template_buffer(selected_countries=None)`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/data_service.py#L26-L52) ahora incluye las columnas `CONTINENT`, `REGION`, `COUNTRY` y `VISITED`, marcando con `1` los países seleccionados actualmente y `0` el resto.
  - [`/api/download_template`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/app.py#L32-L59) soporta tanto `GET` como `POST` recibiendo `selected_countries`. Si hay países seleccionados descarga `visited_countries.xlsx` con la selección actual guardada; si no hay ninguno seleccionado, descarga `template_countries.xlsx` en blanco.
  - En [`updateStats()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L285-L296), el botón `#btn-download` actualiza su texto en tiempo real agregando entre paréntesis la cantidad de países seleccionados (`📥 Descargar Plantilla (3)`) cuando `totalVisited > 0`, o volviendo al texto base sin paréntesis cuando la selección está vacía.

#### 3. Archivos modificados
- [`services/data_service.py`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/data_service.py#L26-L52)
- [`app.py`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/app.py#L32-L59)
- [`templates/index.html`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/templates/index.html#L166-L184)
- [`static/js/main.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L27-L88)

#### 4. Guía de verificación en `DEV` (`http://localhost:8081`)
1. Refrescar `http://localhost:8081` (`Ctrl+Shift+R`), elegir un idioma (ej. **Español**), un color, un estilo de mapa y seleccionar varios países.
2. Recargar la página con `F5`: verificar que el idioma, los países seleccionados, los porcentajes, el estilo y el color se mantienen intactos.
3. Con países seleccionados, hacer clic en **📥 Descargar Plantilla**: se descargará `visited_countries.xlsx` con `VISITED = 1` en tus países elegidos (y si limpiás la selección con **✗ Limpiar Selección** y descargás, bajará `template_countries.xlsx` en cero).

---

### [Cambio #11] Botón `ALL` / `NONE` (`TODO` / `NADA`) a nivel Continente

- **Fecha:** 2026-11-11
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario

#### 1. Problema detectado y oportunidad de mejora
Anteriormente solo era posible seleccionar o deseleccionar masivamente países a nivel subclasificación (`toggleRegion`). Para marcar un continente completo (por ejemplo toda Europa o toda Sudamérica/América), el usuario debía abrir el continente y hacer clic en `ALL` dentro de cada una de sus subregiones una por una.

#### 2. Solución técnica aplicada
- En [`render()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L121-L140) se incorporó en el encabezado de cada continente (`.continent-header`) un botón `id="btn-cont-${continent}"` con `onclick="toggleContinent(this.dataset.continent, event)"`.
- Se creó la función [`toggleContinent(cont, event)`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L223-L250), que ejecuta `event.stopPropagation()` (para no abrir ni cerrar el acordeón al tocar el botón) y marca o desmarca todos los países de todas las subregiones del continente de una sola vez.
- En [`updateStats()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L320-L327), el texto del botón continental alterna dinámicamente entre `selectAll` (`ALL` / `TODO`) y `deselectAll` (`NONE` / `NADA`) cuando el continente alcanza el `100%` de países seleccionados.
- Se agregaron estilos para modo claro y modo oscuro (`body.dark button[id^="btn-cont-"]`) en [`static/css/style.css`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/css/style.css#L194-L216).

#### 3. Archivos modificados
- [`static/js/main.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L121-L327)
- [`static/css/style.css`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/css/style.css#L194-L216)

#### 4. Guía de verificación en `DEV` (`http://localhost:8081`)
1. Refrescar `http://localhost:8081` (`Ctrl+Shift+R`).
2. En cualquier barra de continente (incluso sin desplegarlo), hacer clic en el botón **ALL** (`TODO`):
   - Se seleccionan todos los países de ese continente en un solo clic, el continente sube al `100%` en la barra superior, el botón cambia a **NONE** (`NADA`) y el acordeón no se abre ni cierra por accidente.
3. Volver a hacer clic en **NONE** (`NADA`) sobre ese continente: se desmarcan todos sus países.

---

### [Cambio #12] Mostrar conteo exacto (`X/Y`) junto al porcentaje en todas las métricas

- **Fecha:** 2026-11-11
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario

#### 1. Problema detectado y causa raíz
Las estadísticas de la aplicación (`#stat-total`, `#stat-${continent}` y `#stat-reg-${continent}-${region}`) mostraban únicamente el porcentaje redondeado (`Math.round`). Con un universo de 180 territorios, elegir 1 o 2 países mostraba igual `1%`, sin darle al usuario el dato exacto de cuántos países lleva sobre el total de cada región, continente y del mundo.

#### 2. Solución técnica aplicada
- En [`render()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L131-L163) y [`updateStats()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L300-L338) se unificó el formato `X/Y (Z%)` en los **4 puntos de visualización**:
  1. **Total Mundial (`#stat-total`):** `${totalVisited}/${totalCountries} (${totalPct}%)` (ej. `14/180 (8%)`).
  2. **Barra superior de Continentes (`#stat-africa`, etc.):** `${contVisited}/${contTotal} (${contPct}%)` (ej. `5/46 (11%)`).
  3. **Encabezado del Continente en el acordeón (`#stat-acc-${contId}`):** Se añadió el indicador directo junto al título del continente dentro del acordeón para no tener que mirar arriba mientras se navega la lista.
  4. **Encabezado de cada Subclasificación (`#stat-reg-${continent}-${region}`):** `${regVisited}/${countries.length} (${pct}%)`.

#### 3. Archivos modificados
- [`static/js/main.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L131-L338)
- [`static/css/style.css`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/css/style.css#L225-L229)

#### 4. Guía de verificación en `DEV` (`http://localhost:8081`)
1. Refrescar `http://localhost:8081` (`Ctrl+Shift+R`).
2. Observar la barra superior (`World` y los 5 continentes), los títulos de cada continente en el acordeón y los títulos de cada subregión: todos muestran el conteo exacto y el porcentaje (`X/Y (Z%)`).
3. Seleccionar o quitar países de a uno: el numerador (`X/180`) sube o baja inmediatamente en cada clic.

---

### [Cambio #13] Normalización flexible al subir Excel y notificaciones de países cargados / omitidos

- **Fecha:** 2026-11-11
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario

#### 1. Problema detectado y causa raíz
1. **Validación rígida en `process_upload` (`services/data_service.py`):**
   - Solo aceptaba `df['VISITED'] == 1` exacto y nombres de países idénticos carácter por carácter a `GEO_MAPPING`. Si un usuario escribía `"China"`, `"South Korea"`, `"Russia"`, `"USA"`, o marcaba `VISITED` con `"Yes"`, `"Si"`, `"x"` o `"true"`, se descartaban.
2. **Omisión silenciosa de países fuera de la cartografía:**
   - Cuando un Excel incluía países/microestados ausentes en `world_administrative_boundaries.xlsx` (por ejemplo, en `visited_countries.xlsx` figuran `Liechtenstein`, `Scotland` y `Vatican`), `handleFileUpload()` los ignoraba en silencio sin informar cuántos países se cargaron ni cuáles quedaron afuera.
3. **Múltiples re-renderizados en bucle:**
   - `handleFileUpload()` llamaba a `toggleCountry(name)` dentro de un `forEach`, disparando `updateChips()`, `updateStats()` y `savePreferences()` una vez por cada país del Excel.

#### 2. Solución técnica aplicada
- **Normalización e informe detallado en [`process_upload()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/data_service.py#L90-L148):**
  - Se creó [`UPLOAD_COUNTRY_ALIASES`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/data_service.py#L54-L86) y [`TRUTHY_VISITED_VALUES`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/data_service.py#L88) (`1`, `1.0`, `true`, `yes`, `y`, `si`, `sí`, `x`), realizando cruce insensible a mayúsculas/minúsculas y espacios (`strip()`).
  - Devuelve `{'visited': matched, 'unmatched': unmatched}` diferenciando los países reconocidos de los que no existen en el archivo de límites geográficos.
- **Carga por lotes y notificaciones Toast ([`showToast()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L462-L486) y [`handleFileUpload()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L488-L526)):**
  - En lugar de llamar a `toggleCountry()` N veces, se marcan todos los países del lote en una sola pasada y se invoca `updateChips()` una única vez.
  - Se reemplazó el `alert()` nativo por notificaciones flotantes no intrusivas (`showToast`) que informan cuántos países fueron cargados (`✅ 25 countries loaded from Excel`) y, si hubo países fuera del mapa, cuáles fueron (`⚠️ Not in map boundaries (3): Liechtenstein, Scotland, Vatican`).

#### 3. Archivos modificados
- [`services/data_service.py`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/data_service.py#L54-L148)
- [`static/js/main.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L457-L526)

#### 4. Guía de verificación en `DEV` (`http://localhost:8081`)
1. Refrescar `http://localhost:8081` (`Ctrl+Shift+R`).
2. Hacer clic en **📄 Load Excel / Cargar Excel** y seleccionar el archivo `visited_countries.xlsx` de este repositorio:
   - Aparecerá una notificación verde indicando `✅ 25 countries loaded from Excel.` y una notificación ámbar informando `⚠️ Not in map boundaries (3): Liechtenstein, Scotland, Vatican`.

---

### [Cambio #14] Visor de mapa integrado (Modal con opción de Imprimir/PDF y Abrir en Pestaña Nueva)

- **Fecha:** 2026-11-11
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario

#### 1. Problema detectado y causa raíz
El formulario principal tenía `target="_blank"`, obligando al usuario a salir de la aplicación y acumular múltiples pestañas nuevas cada vez que quería probar un cambio de color, estilo (`Light` / `Standard` / `Dark`) o agregar un país.

#### 2. Solución técnica aplicada
- **Modal de previsualización integrado (`#map-modal` en `templates/index.html`):**
  - El formulario `#map-form` envía su petición directamente a `<iframe id="map-preview-frame" name="map-preview-frame">` y ejecuta [`openMapModal()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L588-L598), desplegando el mapa inmediatamente dentro de la misma página sin perder el contexto.
  - En la barra superior del visor se muestra el ícono, el título, la insignia con el conteo mundial actual (`#modal-map-stats`) y 3 acciones directas:
    1. **🖨️ Print / PDF** ([`printPreviewMap()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L605-L611)): dispara la impresión/exportación PDF directamente sobre el `contentWindow` del mapa.
    2. **↗️ New Tab** ([`openMapInNewTab()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L613-L623)): abre el mapa en una pestaña independiente completa si el usuario desea verlo fuera del modal.
    3. **✕ Cerrar** ([`closeMapModal()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L600-L603) o tecla `Esc`): cierra el visor al instante para seguir editando.
- En [`services/map_service.py`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/map_service.py#L132-L137), cuando el mapa se detecta embebido (`window.self !== window.top`), se oculta el botón flotante interno para no duplicar el botón `🖨️ Print / PDF` de la barra del modal, manteniéndolo visible cuando se abre en pestaña nueva (`↗️ New Tab`).

#### 3. Archivos modificados
- [`templates/index.html`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/templates/index.html#L98-L228)
- [`static/js/main.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L586-L633)
- [`static/css/style.css`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/css/style.css#L259-L269)
- [`services/map_service.py`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/map_service.py#L132-L137)

#### 4. Guía de verificación en `DEV` (`http://localhost:8081`)
1. Refrescar `http://localhost:8081` (`Ctrl+Shift+R`) y pulsar **🚀 Launch Map**:
   - Se abre el visor integrado con tu mapa, mostrando en su barra superior tu conteo (`X/180 (Z%)`), el botón **🖨️ Print / PDF**, el botón **↗️ New Tab** y el botón **✕** (o tecla `Esc`) para cerrarlo.
2. Probar cerrar con `Esc`, cambiar el color o estilo y volver a tocar **🚀 Launch Map** (y probar también **↗️ New Tab**).

---

### [Cambio #15] Optimización de `generate_map()` (pre-parseo en caché de geometrías + único `FeatureCollection`)

- **Fecha:** 2026-11-11
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario

#### 1. Problema detectado y causa raíz
1. **Parseo repetitivo de geometrías en cada request:**
   Aunque `get_world_data()` guardaba el DataFrame de Excel en memoria, la columna `GEOMETRY` seguía almacenada como texto (`str`). En cada llamada a `/view_map`, `generate_map()` ejecutaba `ast.literal_eval()` país por país sobre cadenas extensas de coordenadas.
2. **Multiplicación de capas GeoJSON en el HTML de Folium:**
   Se instanciaba un `folium.GeoJson(...)` distinto dentro del bucle por cada país seleccionado. Seleccionar 80 países generaba 80 bloques `L.geoJson(...)` separados con 80 funciones de estilo y 80 listeners en el HTML resultante.

#### 2. Solución técnica aplicada
- **Pre-parseo único al inicializar el caché (`services/data_service.py`):**
  - En [`get_world_data()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/data_service.py#L16-L49) y [`get_cached_features()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/data_service.py#L52-L56), `ast.literal_eval` se ejecuta una única vez al cargar el archivo Excel y construye `CACHE['features_by_country']` con objetos GeoJSON `Feature` listos para usar en `O(1)`.
- **Consolidación en un único `FeatureCollection` (`services/map_service.py`):**
  - En [`generate_map()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/map_service.py#L162-L227), todos los países seleccionados se agrupan en un solo objeto `FeatureCollection` y se montan mediante una única capa `folium.GeoJson` con `folium.GeoJsonTooltip(fields=['name'], labels=False, sticky=True)`.

#### 3. Archivos modificados
- [`services/data_service.py`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/data_service.py#L10-L56)
- [`services/map_service.py`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/map_service.py#L162-L227)

#### 4. Guía de verificación en `DEV` (`http://localhost:8081`)
1. Seleccionar un continente entero (o todos los continentes con **ALL**) y pulsar **🚀 Launch Map**:
   - El mapa se genera y abre de forma instantánea y fluida, mostrando el tooltip con el nombre de cada país al pasar el cursor.

---

### [Cambio #16] Fronteras vectoriales nítidas para países no seleccionados en el mapa

- **Fecha:** 2026-11-11
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario

#### 1. Problema detectado y causa raíz
Los mapas base raster (`Light` y `Dark` de Esri) dibujan las fronteras políticas con trazos muy tenues en niveles de zoom globales (`zoom 2–4`), haciendo que los límites de los países aún no visitados se vieran difuminados y poco definidos.

#### 2. Solución técnica aplicada
- Aprovechando el caché pre-parseado `features_by_country` creado en el Cambio #15, en [`generate_map()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/map_service.py#L182-L265) se incorporó una capa vectorial base (`Unvisited Country Borders`) con un `FeatureCollection` de todos los países no seleccionados:
  - Dibuja bordes vectoriales nítidos (`#64748b` con `weight: 0.8–0.85` en `Light`/`Dark` y `#475569` en `Standard`), garantizando fronteras políticas perfectamente definidas en cualquier nivel de zoom.
  - Incluye resaltado sutil al pasar el cursor (`highlight_function`) y tooltip con el nombre del país, permitiendo identificar cualquier país del mapa aunque no esté marcado como visitado.
- Sobre esa capa base se renderiza la capa `Visited Countries` con trazo de mayor grosor (`weight: 0.9–1.1`) y opacidad (`0.78–0.84`).

#### 3. Archivos modificados
- [`services/map_service.py`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/services/map_service.py#L182-L265)

#### 4. Guía de verificación en `DEV` (`http://localhost:8081`)
1. Pulsar **🚀 Launch Map** en cualquiera de los 3 estilos (`Light`, `Standard`, `Dark`):
   - Verificar que todos los países no elegidos ahora muestran sus fronteras políticas bien definidas y que al pasar el mouse también informan su nombre.

---

### [Cambio #17] Seguridad de subida (`MAX_CONTENT_LENGTH`), optimización de imagen de fondo (`WebP`), actualización de `README.md` y `.dockerignore` para Producción

- **Fecha:** 2026-11-11
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario

#### 1. Problema detectado y causa raíz
1. **Ausencia de límite de tamaño y validación de extensión en `/api/upload`:**
   `app.py` no definía `MAX_CONTENT_LENGTH`, permitiendo que una subida accidental o maliciosa de un archivo pesado consumiera la memoria de la instancia de Cloud Run, y `<input type="file">` en `templates/index.html` no filtraba por `.xlsx,.xls`.
2. **Peso elevado de `static/bg1.png` (`766 KB`):**
   La imagen de fondo pesaba casi `800 KB` para mostrarse detrás de un overlay con 85%–95% de opacidad.
3. **Ausencia de `.dockerignore`:**
   El `COPY . ./` del `Dockerfile` copiaba dentro de la imagen de producción el directorio `.git`, entornos virtuales locales (`.venv`), cachés (`__pycache__`) y el archivo personal `visited_countries.xlsx`.

#### 2. Solución técnica aplicada
- **Protección de subida (`app.py` y `templates/index.html`):**
  - Se configuró `app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024` (5 MB) con su respectivo manejador `@app.errorhandler(413)` y validación de extensión `.xlsx`/`.xls` en `/api/upload`.
  - Se agregó `accept=".xlsx,.xls"` en `#excel-upload` (`templates/index.html`).
- **Compresión WebP con fallback (`static/bg1.webp` y `static/css/style.css`):**
  - Se generó `static/bg1.webp` (`84 KB`, reducción del **89%** respecto a los `766 KB` de `bg1.png`) y se configuró `image-set(url('/static/bg1.webp') type('image/webp'), url('/static/bg1.png') type('image/png'))` en `static/css/style.css`.
- **Aislamiento de imagen Docker (`.dockerignore`) y documentación (`README.md`):**
  - Se creó `.dockerignore` excluyendo `.git`, `.venv`, `__pycache__`, `visited_countries.xlsx` y archivos temporales de análisis.
  - Se actualizó `README.md` reflejando todas las capacidades actuales y enlazando este `CHANGELOG.md`.

#### 3. Archivos creados / modificados
- [`.dockerignore`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/.dockerignore) *(nuevo)*
- [`static/bg1.webp`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/bg1.webp) *(nuevo)*
- [`app.py`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/app.py#L9-L72)
- [`templates/index.html`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/templates/index.html#L116-L117)
- [`static/css/style.css`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/css/style.css#L1-L9)
- [`README.md`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/README.md#L5-L30)

---

### [Cambio #18] Misión clara en subtítulo y guía visual rápida de 3 pasos en los 15 idiomas

- **Fecha:** 2026-11-11
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario

#### 1. Problema detectado y causa raíz
El subtítulo original (`"Visualize selected countries across the globe."`) era demasiado genérico y técnico, y al ingresar por primera vez no existía una guía rápida que explicara en 3 segundos cuál es el flujo de trabajo de la aplicación.

#### 2. Solución técnica aplicada
- **Subtítulo orientado al propósito (`desc` en `static/js/translations.js`):**
  - Se reescribió en los 15 idiomas para comunicar claramente el objetivo (ej. en español: *"Marcá los países que visitaste, mirá tu progreso global y creá tu mapa personalizado."* y en inglés: *"Track visited countries, see your global progress, and create your custom world map."*).
- **Barra de guía rápida de 3 pasos (`#quick-steps` en `templates/index.html`, `static/js/translations.js`, `static/js/main.js` y `static/css/style.css`):**
  - Se incorporó una cinta compacta de 3 pasos (`step1`, `step2`, `step3`) traducida a los 15 idiomas y adaptada tanto a Modo Claro como a Modo Oscuro (`body.dark #quick-steps`):
    `① Elegí países (clic o Cargar Excel)  →  ② Elegí estilo y color  →  ③ Lanzá o imprimí tu mapa`

#### 3. Archivos modificados
- [`templates/index.html`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/templates/index.html#L101-L108)
- [`static/js/translations.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/translations.js#L1-L227)
- [`static/js/main.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L540-L545)
- [`static/css/style.css`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/css/style.css#L266-L272)

#### 4. Guía de verificación en `DEV` (`http://localhost:8081`)
1. Refrescar `http://localhost:8081` (`Ctrl+Shift+R`).
2. Observar el nuevo subtítulo bajo **World Map / Mapa del Mundo** y la barra guía de 3 pasos (`① → ② → ③`) en la parte superior de la tarjeta tanto en Modo Claro como en Modo Oscuro y al cambiar de idioma.

---

### [Cambio #19] Prioridad visual al buscador/selección y estado vacío explicativo en `#no-selection`

- **Fecha:** 2026-11-11
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario

#### 1. Problema detectado y causa raíz
1. **Jerarquía visual invertida:** Al abrir la aplicación, el primer bloque grande debajo del encabezado era la caja de **Gestión de Datos (`Download Template` / `Load Excel`)**, mientras que el buscador de países (`#search`) y el recuadro de países seleccionados (`#active-chips`) quedaban más abajo. Esto hacía parecer que era obligatorio descargar y subir un archivo Excel para empezar a usar la herramienta.
2. **Estado vacío y placeholder poco informativos:** El buscador decía simplemente `"Search..."` / `"Buscar..."`, y cuando no había países seleccionados `#no-selection` mostraba un escueto `"No selection"` / `"Sin selección"`, sin orientar al usuario sobre cómo agregar su primer país.

#### 2. Solución técnica aplicada
- **Reordenamiento jerárquico en [`templates/index.html`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/templates/index.html#L110-L166):**
  - Se ubicó en primer lugar el bloque **Buscador (`#search`) + Países seleccionados (`#active-chips`)** inmediatamente debajo de la guía de 3 pasos (`#quick-steps`).
  - La barra de acciones secundarias (**Gestión de Datos** y **Selección y Vista**) se colocó justo debajo como barra de herramientas compacta antes del acordeón de continentes (`#accordion`).
- **Microcopy explicativo en los 15 idiomas ([`static/js/translations.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/translations.js#L1-L227)):**
  - `search`: Actualizado de `"Buscar..."` a `"Buscar país..."` (`"Search country..."`, `"Rechercher un pays..."`, etc.) en los 15 idiomas.
  - `noSelection`: Actualizado en los 15 idiomas para guiar la acción cuando la lista está vacía (ej. en español: *"Todavía no elegiste países — buscalos arriba, desplegá un continente abajo o cargá tu Excel."* y en inglés: *"No countries selected yet — search above, expand a continent below, or load an Excel file."*).

#### 3. Archivos modificados
- [`templates/index.html`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/templates/index.html#L110-L166)
- [`static/js/translations.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/translations.js#L1-L227)

#### 4. Guía de verificación en `DEV` (`http://localhost:8081`)
1. Refrescar `http://localhost:8081` (`Ctrl+Shift+R`).
2. Verificar que debajo de los 3 pasos aparece directamente el buscador (`🔍 Buscar país...` / `🔍 Search country...`) seguido del cuadro de selección y luego la barra compacta de herramientas.
3. Si tenés países seleccionados, hacé clic en **✗ Limpiar Selección** para ver el nuevo mensaje explicativo del estado vacío en distintos idiomas.

---

### [Cambio #20] Etiquetas contextuales (`📥 Descargar Plantilla` ↔ `💾 Exportar Excel (N)`) y traducción de botones del visor

- **Fecha:** 2026-11-11
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario

#### 1. Problema detectado y causa raíz
1. **Ambigüedad en `#btn-download` al tener países seleccionados:** Aunque el botón exporta los países seleccionados con `VISITED = 1` cuando hay países marcados, su etiqueta seguía diciendo `"📥 Descargar Plantilla (N)"`, lo que sugería que iba a descargar una plantilla vacía en vez de guardar el trabajo actual.
2. **Botones del modal de previsualización sin traducir:** Los botones `🖨️ Print / PDF` y `↗️ New Tab` del visor del mapa estaban fijos en inglés sin adaptarse a los 15 idiomas.

#### 2. Solución técnica aplicada
- **Etiqueta contextual dinámica en [`updateStats()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L340-L347):**
  - Cuando `totalVisited === 0`, el botón muestra `t.download` (`📥 Descargar Plantilla` / `📥 Download Template`).
  - Cuando `totalVisited > 0`, el botón cambia automáticamente a `${t.exportExcel} (${totalVisited})` (`💾 Exportar Excel (5)` / `💾 Export Excel (5)`), reflejando con exactitud que se descargará el archivo con la selección actual guardada.
- **Internacionalización completa de controles del visor ([`static/js/translations.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/translations.js#L1-L242), [`templates/index.html`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/templates/index.html#L217-L226), [`static/js/main.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L556-L560) y [`static/css/style.css`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/css/style.css#L274-L292)):**
  - Se añadieron las claves `exportExcel`, `printPdf` y `newTab` en los 15 idiomas.
  - Se asignaron los IDs `#btn-modal-print` y `#btn-modal-newtab` en el modal y se conectaron a `changeLanguage()`, junto con sus estilos de alto contraste para Modo Oscuro.

#### 3. Archivos modificados
- [`templates/index.html`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/templates/index.html#L217-L226)
- [`static/js/translations.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/translations.js#L1-L242)
- [`static/js/main.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L340-L347)
- [`static/css/style.css`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/css/style.css#L274-L292)

#### 4. Guía de verificación en `DEV` (`http://localhost:8081`)
1. Refrescar `http://localhost:8081` (`Ctrl+Shift+R`).
2. Con `0` países seleccionados, verificar que el botón verde dice **📥 Descargar Plantilla** (`📥 Download Template`).
3. Seleccionar uno o más países: el botón cambia automáticamente a **💾 Exportar Excel (N)** (`💾 Export Excel (N)`).
4. Hacer clic en **🚀 Lanzar Mapa**: verificar que en la barra superior del visor los botones **🖨️ Imprimir / PDF** y **↗️ Nueva Pestaña** aparecen traducidos al idioma elegido.

---

### [Cambio #21] Contador dinámico en `🚀 Launch Map (N)` y aviso al lanzar sin países seleccionados

- **Fecha:** 2026-11-11
- **Rama:** `dev`
- **Estado:** ✅ Aprobado por el usuario

#### 1. Problema detectado y causa raíz
1. **Sin confirmación visual de cantidad en el botón de acción principal (`#btn-launch`):** Cuando el usuario desplazaba la página hasta abajo del todo para lanzar el mapa, el botón decía siempre `"🚀 Launch Map"` sin reflejar cuántos países se iban a pintar.
2. **Apertura de mapa vacío sin feedback cuando `selectedCount === 0`:** Si alguien pulsaba `"🚀 Launch Map"` sin haber seleccionado ningún país, se abría un mapa sin ningún polígono coloreado sin explicarle que antes debía elegir al menos un país.

#### 2. Solución técnica aplicada
- **Contador en tiempo real en `#btn-launch` ([`updateStats()`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L349-L354)):**
  - Muestra `${t.launch} (${totalVisited})` (ej. `🚀 Lanzar Mapa (25)`) cuando `totalVisited > 0`, y `t.launch` cuando `totalVisited === 0`.
- **Validación y notificación amigable al enviar con 0 países ([`openMapModal(event)`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L601-L625), [`templates/index.html`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/templates/index.html#L99) y [`static/js/translations.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/translations.js#L1-L257)):**
  - Si `selectedCount === 0`, se intercepta el envío (`event.preventDefault()`), se muestra un toast traducido en cualquiera de los 15 idiomas (`noSelectionWarn`, ej. *"⚠️ Elegí al menos un país antes de lanzar el mapa."*) y se enfoca automáticamente el buscador (`#search`).

#### 3. Archivos modificados
- [`templates/index.html`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/templates/index.html#L99)
- [`static/js/translations.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/translations.js#L1-L257)
- [`static/js/main.js`](file:///home/alejandrocamerlengo/Projects/geospacial_projects/static/js/main.js#L349-L354)

#### 4. Guía de verificación en `DEV` (`http://localhost:8081`)
1. Refrescar `http://localhost:8081` (`Ctrl+Shift+R`).
2. Seleccionar varios países: verificar que el botón principal al pie muestra **🚀 Lanzar Mapa (N)** (`🚀 Launch Map (N)`).
3. Hacer clic en **✗ Limpiar Selección** (dejando 0 países) y luego pulsar **🚀 Lanzar Mapa**:
   - No se abre un mapa vacío; en su lugar aparece el aviso flotante `⚠️ Elegí al menos un país antes de lanzar el mapa.` y el cursor se posiciona en el buscador.

