let currentLang = 'en';
let countriesData = {};

// --- Helpers ---

/**
 * Escapes special HTML characters so strings containing apostrophes, quotes,
 * or ampersands (e.g., "China, People's Republic of") can be safely placed
 * inside HTML attributes and text nodes without breaking DOM/JS parsing.
 * @param {string} str - Raw string value.
 * @returns {string} HTML-escaped string.
 */
function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}

// --- Core Functions ---

/**
 * Persists current selection and user preferences (language, map style, color) in localStorage.
 */
function savePreferences() {
    try {
        const select = document.getElementById('country-select');
        if (select) {
            const selected = Array.from(select.selectedOptions).map(o => o.value);
            localStorage.setItem('selectedCountries', JSON.stringify(selected));
        }
        localStorage.setItem('lang', currentLang);
        const styleEl = document.getElementById('map-style-select');
        if (styleEl) localStorage.setItem('mapStyle', styleEl.value);
        const colorEl = document.getElementById('visited-color-input');
        if (colorEl) localStorage.setItem('visitedColor', colorEl.value);
    } catch (e) {
        // Ignore storage quota or private-mode restrictions
    }
}

async function init() {
    const resp = await fetch('/api/countries');
    countriesData = await resp.json();

    // Restore saved preferences (theme, language, map style, color)
    if (localStorage.getItem('theme') === 'dark') toggleTheme(true);

    const savedStyle = localStorage.getItem('mapStyle');
    const styleEl = document.getElementById('map-style-select');
    if (savedStyle && styleEl) styleEl.value = savedStyle;

    const savedColor = localStorage.getItem('visitedColor');
    const colorEl = document.getElementById('visited-color-input');
    if (savedColor && colorEl) colorEl.value = savedColor;

    const savedLang = localStorage.getItem('lang');
    const langEl = document.getElementById('lang-select');
    if (savedLang && translations[savedLang]) {
        currentLang = savedLang;
        if (langEl) langEl.value = savedLang;
    }

    // Apply initial render and restore saved country selection
    render();
    try {
        const savedCountries = JSON.parse(localStorage.getItem('selectedCountries') || '[]');
        if (Array.isArray(savedCountries) && savedCountries.length > 0) {
            const select = document.getElementById('country-select');
            const savedSet = new Set(savedCountries);
            Array.from(select.options).forEach(opt => {
                if (savedSet.has(opt.value)) {
                    opt.selected = true;
                    const chip = document.getElementById(`chip-${opt.value}`);
                    if (chip) {
                        chip.classList.remove('bg-white', 'border-gray-200');
                        chip.classList.add('bg-indigo-500', 'text-white', 'border-indigo-600');
                    }
                }
            });
        }
    } catch (e) {
        // Ignore malformed localStorage data
    }

    changeLanguage(currentLang);
}

/**
 * Renders the continent/region accordion and populates the hidden <select> element.
 * Preserves any previously selected countries and open accordion panels across
 * re-renders (e.g., when switching languages).
 */
function render() {
    const container = document.getElementById('accordion');
    const select = document.getElementById('country-select');
    const t = translations[currentLang] || translations.en;

    // Preserve currently selected countries before rebuilding <select> options
    const previouslySelected = new Set(
        Array.from(select.selectedOptions).map(o => o.value)
    );

    // Preserve currently expanded continent panels before rebuilding accordion HTML
    const expandedContinents = new Set(
        Array.from(container.querySelectorAll('.continent-content:not(.hidden)')).map(el => el.id)
    );

    let html = '';
    let options = '';

    // Sort continents alphabetically by their localized display name
    const sortedContinents = Object.entries(countriesData).sort(([contA], [contB]) => {
        const nameA = t[contA] || contA;
        const nameB = t[contB] || contB;
        return nameA.localeCompare(nameB, currentLang);
    });

    for (const [continent, regions] of sortedContinents) {
        const id = continent.toLowerCase().replace(/\s/g, '-');
        const continentName = t[continent] || continent;
        const safeCont = escapeHtml(continent);
        const isExpanded = expandedContinents.has(`content-${id}`);
        const allContCountries = Object.values(regions).flat();
        const allContSelected = allContCountries.length > 0 && allContCountries.every(c => previouslySelected.has(c.name));
        const contBtnLabel = allContSelected ? t.deselectAll : t.selectAll;
        html += `
            <div class="continent-container border border-gray-200 rounded-xl overflow-hidden">
                <div onclick="toggleAcc('${id}')" class="continent-header w-full text-left p-3 bg-gray-50 font-bold text-sm flex justify-between items-center cursor-pointer select-none">
                    <span>${escapeHtml(continentName)} <span id="stat-acc-${id}" class="text-[11px] font-semibold text-indigo-500 ml-1.5">0/${allContCountries.length} (0%)</span></span>
                    <div class="flex items-center gap-3">
                        <button type="button" id="btn-cont-${safeCont}" data-continent="${safeCont}" onclick="toggleContinent(this.dataset.continent, event)" class="text-[10px] font-black text-indigo-500 hover:text-indigo-700 px-2 py-0.5 rounded-md border border-indigo-200 bg-white transition-all">${escapeHtml(contBtnLabel)}</button>
                        <span id="icon-${id}" class="transition-transform duration-200${isExpanded ? ' rotate-180' : ''}">▼</span>
                    </div>
                </div>
                <div id="content-${id}" class="continent-content${isExpanded ? '' : ' hidden'} p-2 space-y-2 bg-white">
        `;

        // Sort subclassifications (subregions) alphabetically by their localized display name
        const sortedRegions = Object.entries(regions).sort(([regA], [regB]) => {
            const regNameA = t[regA] || regA;
            const regNameB = t[regB] || regB;
            return regNameA.localeCompare(regNameB, currentLang);
        });

        for (const [region, countries] of sortedRegions) {
            const regionName = t[region] || region;
            const safeCont = escapeHtml(continent);
            const safeReg = escapeHtml(region);
            // Sort countries alphabetically by their localized display name in the active language
            const localizedCountries = countries
                .map(c => ({ name: c.name, translated: getTranslatedCountryName(c.name, currentLang) }))
                .sort((a, b) => a.translated.localeCompare(b.translated, currentLang));
            const allRegSelected = countries.length > 0 && countries.every(c => previouslySelected.has(c.name));
            const regBtnLabel = allRegSelected ? t.deselectAll : t.selectAll;
            html += `
                <div class="region-container p-2 border border-gray-50 rounded-lg">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-[10px] font-bold text-gray-400 uppercase">${escapeHtml(regionName)} <span id="stat-reg-${safeCont}-${safeReg}" class="text-indigo-500 ml-1">0/${countries.length} (0%)</span></span>
                        <button type="button" id="btn-reg-${safeCont}-${safeReg}" data-continent="${safeCont}" data-region="${safeReg}" onclick="toggleRegion(this.dataset.continent, this.dataset.region)" class="text-[9px] font-black text-indigo-400 hover:text-indigo-600">${escapeHtml(regBtnLabel)}</button>
                    </div>
                    <div class="flex flex-wrap gap-1">
                        ${localizedCountries.map(c => {
                const safeName = escapeHtml(c.name);
                const safeTranslated = escapeHtml(c.translated);
                const isSelected = previouslySelected.has(c.name);
                options += `<option value="${safeName}"${isSelected ? ' selected' : ''}>${safeTranslated}</option>`;
                const stateClasses = isSelected
                    ? 'bg-indigo-500 text-white border-indigo-600'
                    : 'bg-white border-gray-200';
                // Pass country key via data-country instead of inline JS string literal to prevent syntax errors on apostrophes
                return `<button type="button" id="chip-${safeName}" data-country="${safeName}" onclick="toggleCountry(this.dataset.country)"
                                 class="px-2.5 py-1 sm:px-2 sm:py-0.5 border rounded-full text-[11px] sm:text-[10px] ${stateClasses} transition-all">${safeTranslated}</button>`;
            }).join('')}
                    </div>
                </div>`;
        }
        html += `</div></div>`;
    }
    container.innerHTML = html;
    select.innerHTML = options;
}

function toggleCountry(name) {
    const select = document.getElementById('country-select');
    const chip = document.getElementById(`chip-${name}`);
    const opt = Array.from(select.options).find(o => o.value === name);
    if (!opt) return;

    opt.selected = !opt.selected;
    if (chip) {
        chip.classList.toggle('bg-white', !opt.selected);
        chip.classList.toggle('border-gray-200', !opt.selected);
        chip.classList.toggle('bg-indigo-500', opt.selected);
        chip.classList.toggle('text-white', opt.selected);
        chip.classList.toggle('border-indigo-600', opt.selected);
    }
    updateChips();
}

function toggleRegion(cont, reg) {
    const countries = countriesData[cont][reg];
    const allSelected = countries.every(c => {
        const opt = Array.from(document.getElementById('country-select').options).find(o => o.value === c.name);
        return opt && opt.selected;
    });
    countries.forEach(c => {
        const opt = Array.from(document.getElementById('country-select').options).find(o => o.value === c.name);
        if (opt) opt.selected = !allSelected;
        const chip = document.getElementById(`chip-${c.name}`);
        if (chip && opt) {
            chip.classList.toggle('bg-white', !opt.selected);
            chip.classList.toggle('border-gray-200', !opt.selected);
            chip.classList.toggle('bg-indigo-500', opt.selected);
            chip.classList.toggle('text-white', opt.selected);
            chip.classList.toggle('border-indigo-600', opt.selected);
        }
    });
    updateChips();
}

/**
 * Selects or deselects all countries across all subregions of a given continent.
 * Stops event propagation so clicking the button does not collapse/expand the accordion.
 */
function toggleContinent(cont, event) {
    if (event) event.stopPropagation();
    const regions = countriesData[cont];
    if (!regions) return;
    const allCountries = Object.values(regions).flat();
    const select = document.getElementById('country-select');
    const allSelected = allCountries.length > 0 && allCountries.every(c => {
        const opt = Array.from(select.options).find(o => o.value === c.name);
        return opt && opt.selected;
    });
    allCountries.forEach(c => {
        const opt = Array.from(select.options).find(o => o.value === c.name);
        if (opt) opt.selected = !allSelected;
        const chip = document.getElementById(`chip-${c.name}`);
        if (chip && opt) {
            chip.classList.toggle('bg-white', !opt.selected);
            chip.classList.toggle('border-gray-200', !opt.selected);
            chip.classList.toggle('bg-indigo-500', opt.selected);
            chip.classList.toggle('text-white', opt.selected);
            chip.classList.toggle('border-indigo-600', opt.selected);
        }
    });
    updateChips();
}

function updateChips() {
    const area = document.getElementById('active-chips');
    const selected = Array.from(document.getElementById('country-select').selectedOptions);
    const query = document.getElementById('search').value.toLowerCase();

    if (selected.length === 0) {
        area.innerHTML = `<span class="text-xs text-gray-400 w-full text-center py-2">${escapeHtml(translations[currentLang].noSelection)}</span>`;
    } else {
        area.innerHTML = selected.map(o => {
            const safeVal = escapeHtml(o.value);
            const safeText = escapeHtml(o.text);
            return `
            <div class="flex items-center gap-1 px-3 py-1.5 bg-indigo-50 text-indigo-700 rounded-xl text-[11px] font-bold border border-indigo-100 shadow-sm transition-all">
                ${safeText} <button type="button" data-country="${safeVal}" onclick="toggleCountry(this.dataset.country)" class="hover:text-red-500 ml-1 text-sm">×</button>
            </div>
        `;
        }).join('');

        // Re-apply filter if searching
        if (query) filterCountries();
    }
    updateStats();
    savePreferences();
}

function updateStats() {
    const select = document.getElementById('country-select');
    const selected = select ? Array.from(select.selectedOptions).map(o => o.value) : [];
    let totalVisited = 0;
    let totalCountries = 0;

    for (const [continent, regions] of Object.entries(countriesData)) {
        let contVisited = 0;
        let contTotal = 0;

        for (const [region, countries] of Object.entries(regions)) {
            let regVisited = 0;
            countries.forEach(c => {
                if (selected.includes(c.name)) {
                    regVisited++;
                    contVisited++;
                    totalVisited++;
                }
            });
            contTotal += countries.length;
            totalCountries += countries.length;

            const regStatEl = document.getElementById(`stat-reg-${continent}-${region}`);
            if (regStatEl) {
                const pct = countries.length > 0 ? Math.round((regVisited / countries.length) * 100) : 0;
                regStatEl.innerText = `${regVisited}/${countries.length} (${pct}%)`;
            }

            // Dynamically toggle regional button between ALL (selectAll) and NONE (deselectAll)
            const regBtnEl = document.getElementById(`btn-reg-${continent}-${region}`);
            if (regBtnEl) {
                const t = translations[currentLang] || translations.en;
                const allSelected = countries.length > 0 && regVisited === countries.length;
                regBtnEl.innerText = allSelected ? t.deselectAll : t.selectAll;
            }
        }
        const contId = continent.toLowerCase().replace(/\s/g, '-');
        const contPct = contTotal > 0 ? Math.round((contVisited / contTotal) * 100) : 0;
        const contValEl = document.getElementById(`stat-${contId}`);
        if (contValEl) {
            contValEl.innerText = `${contVisited}/${contTotal} (${contPct}%)`;
        }
        const contAccStatEl = document.getElementById(`stat-acc-${contId}`);
        if (contAccStatEl) {
            contAccStatEl.innerText = `${contVisited}/${contTotal} (${contPct}%)`;
        }

        // Dynamically toggle continent button between ALL (selectAll) and NONE (deselectAll)
        const contBtnEl = document.getElementById(`btn-cont-${continent}`);
        if (contBtnEl) {
            const t = translations[currentLang] || translations.en;
            const allContSelected = contTotal > 0 && contVisited === contTotal;
            contBtnEl.innerText = allContSelected ? t.deselectAll : t.selectAll;
        }
    }

    const totalEl = document.getElementById('stat-total');
    if (totalEl) {
        const totalPct = totalCountries > 0 ? Math.round((totalVisited / totalCountries) * 100) : 0;
        totalEl.innerText = `${totalVisited}/${totalCountries} (${totalPct}%)`;
    }

    // Switch button label between "📥 Download Template" (0 selected) and "💾 Export Excel (N)" (> 0 selected)
    const downloadBtn = document.getElementById('btn-download');
    if (downloadBtn) {
        const t = translations[currentLang] || translations.en;
        const exportLabel = t.exportExcel || t.download;
        downloadBtn.innerText = totalVisited > 0 ? `${exportLabel} (${totalVisited})` : t.download;
    }

    // Show selected country count in parentheses on the Launch Map button when > 0
    const launchBtn = document.getElementById('btn-launch');
    if (launchBtn) {
        const t = translations[currentLang] || translations.en;
        launchBtn.innerText = totalVisited > 0 ? `${t.launch} (${totalVisited})` : t.launch;
    }
}

function filterCountries() {
    const query = document.getElementById('search').value.toLowerCase();

    // 1. Filter selected countries (active-chips)
    document.querySelectorAll('#active-chips > div').forEach(chip => {
        const name = chip.innerText.replace('×', '').trim().toLowerCase();
        chip.classList.toggle('hidden', query !== '' && !name.includes(query));
    });

    // 2. Filter available countries (accordion)
    document.querySelectorAll('.continent-container').forEach(cont => {
        let contHasMatch = false;

        cont.querySelectorAll('.region-container').forEach(reg => {
            let regHasMatch = false;

            reg.querySelectorAll('button[id^="chip-"]').forEach(btn => {
                const match = btn.innerText.toLowerCase().includes(query);
                btn.classList.toggle('hidden', query !== '' && !match);
                if (match) { regHasMatch = true; contHasMatch = true; }
            });

            // Hide/Show Region
            reg.classList.toggle('hidden', query !== '' && !regHasMatch);
        });

        // Hide/Show Continent
        cont.classList.toggle('hidden', query !== '' && !contHasMatch);

        // Auto-expand Continent content if query active
        const content = cont.querySelector('.continent-content');
        const icon = cont.querySelector('span[id^="icon-"]');
        if (query !== '') {
            if (contHasMatch) {
                content.classList.remove('hidden');
                icon.classList.add('rotate-180');
            }
        } else {
            // Restore collapsed state
            content.classList.add('hidden');
            icon.classList.remove('rotate-180');
        }
    });
}

function clearSelection() {
    Array.from(document.getElementById('country-select').options).forEach(o => o.selected = false);
    document.querySelectorAll('button[id^="chip-"]').forEach(c => {
        c.classList.remove('bg-indigo-500', 'text-white', 'border-indigo-600');
        c.classList.add('bg-white', 'border-gray-200');
    });
    updateChips();
}

async function downloadTemplate() {
    const select = document.getElementById('country-select');
    const selected = select ? Array.from(select.selectedOptions).map(o => o.value) : [];
    try {
        const resp = await fetch('/api/download_template', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ selected_countries: selected })
        });
        if (!resp.ok) throw new Error('Download failed');
        const blob = await resp.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = selected.length > 0 ? 'visited_countries.xlsx' : 'template_countries.xlsx';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (e) {
        window.location.href = '/api/download_template';
    }
}

function changeBackground(url) {
    document.body.style.backgroundImage = `url('${url}')`;
}

function toggleFullscreen() {
    const el = document.documentElement;
    if (!document.fullscreenElement) {
        el.requestFullscreen().catch(err => {
            alert(`Error attempting to enable full-screen mode: ${err.message}`);
        });
    } else {
        document.exitFullscreen();
    }
}

// Listen for fullscreen changes to adjust UI without overriding default CSS height on exit
document.addEventListener('fullscreenchange', () => {
    const accordion = document.getElementById('accordion');
    const fsBtn = document.getElementById('btn-fullscreen');
    const isFullscreen = Boolean(document.fullscreenElement);

    if (accordion) {
        // Use 70vh in fullscreen; clear inline style on exit so Tailwind's max-h-[32rem] applies
        accordion.style.maxHeight = isFullscreen ? '70vh' : '';
    }
    if (fsBtn) {
        fsBtn.classList.toggle('ring-2', isFullscreen);
        fsBtn.classList.toggle('ring-indigo-400', isFullscreen);
    }
});

/**
 * Displays a non-intrusive floating notification toast at the bottom-right of the screen.
 * @param {string} message - Notification text.
 * @param {'success'|'warning'|'error'} type - Visual tone of the toast.
 */
function showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm';
        document.body.appendChild(container);
    }

    const toneClasses = {
        success: 'bg-emerald-600 text-white border-emerald-500',
        warning: 'bg-amber-500 text-white border-amber-400',
        error: 'bg-red-600 text-white border-red-500'
    };

    const toast = document.createElement('div');
    toast.className = `px-4 py-3 rounded-xl shadow-xl border text-xs font-semibold transition-all duration-300 flex items-start justify-between gap-3 ${toneClasses[type] || toneClasses.success}`;
    toast.innerHTML = `<span>${escapeHtml(message)}</span><button type="button" class="font-bold opacity-80 hover:opacity-100">×</button>`;
    toast.querySelector('button').onclick = () => toast.remove();
    container.appendChild(toast);

    setTimeout(() => {
        if (toast.parentNode) toast.remove();
    }, 6000);
}

async function handleFileUpload(input) {
    const file = input.files[0];
    if (!file) return;
    const fd = new FormData();
    fd.append('file', file);
    try {
        const resp = await fetch('/api/upload', { method: 'POST', body: fd });
        const data = await resp.json();
        if (resp.ok) {
            const visitedList = Array.isArray(data) ? data : (data.visited || []);
            const unmatchedList = Array.isArray(data) ? [] : (data.unmatched || []);

            clearSelection();
            const select = document.getElementById('country-select');
            const visitedSet = new Set(visitedList);
            Array.from(select.options).forEach(opt => {
                if (visitedSet.has(opt.value)) {
                    opt.selected = true;
                    const chip = document.getElementById(`chip-${opt.value}`);
                    if (chip) {
                        chip.classList.remove('bg-white', 'border-gray-200');
                        chip.classList.add('bg-indigo-500', 'text-white', 'border-indigo-600');
                    }
                }
            });
            updateChips();

            showToast(`✅ ${visitedList.length} countries loaded from Excel.`, 'success');
            if (unmatchedList.length > 0) {
                showToast(`⚠️ Not in map boundaries (${unmatchedList.length}): ${unmatchedList.join(', ')}`, 'warning');
            }
        } else {
            showToast(data.error || 'Error processing Excel file.', 'error');
        }
    } catch (e) {
        showToast('Upload failed. Please verify the file is a valid .xlsx document.', 'error');
    }
    input.value = "";
}

function toggleAcc(id) {
    document.getElementById(`content-${id}`).classList.toggle('hidden');
    document.getElementById(`icon-${id}`).classList.toggle('rotate-180');
}

function changeLanguage(lang) {
    currentLang = lang;
    const t = translations[lang] || translations.en;

    // Set document language and text direction (RTL for Arabic, LTR otherwise)
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';

    // Text Elements with fail-safe checks
    const setTxt = (id, text) => {
        const el = document.getElementById(id);
        if (el) el.innerText = text;
    };

    document.title = t.title;
    setTxt('card-title', t.title);
    setTxt('card-desc', t.desc);
    setTxt('step-1', t.step1 || translations.en.step1);
    setTxt('step-2', t.step2 || translations.en.step2);
    setTxt('step-3', t.step3 || translations.en.step3);
    setTxt('btn-download', t.download);
    setTxt('btn-load', t.load);
    setTxt('btn-fullscreen', t.fullscreen);
    setTxt('btn-clear', t.clear);
    setTxt('btn-launch', t.launch);
    setTxt('btn-modal-print', t.printPdf || translations.en.printPdf);
    setTxt('btn-modal-newtab', t.newTab || translations.en.newTab);
    setTxt('label-style', t.style);
    setTxt('label-color', t.color);
    setTxt('opt-style-light', t.styleLight || 'Light');
    setTxt('opt-style-standard', t.styleStandard || 'Standard');
    setTxt('opt-style-dark', t.styleDark || 'Dark');
    setTxt('label-data', t.dataMgmt);
    setTxt('label-view', t.selectView);
    setTxt('stat-label-total', t.statTotal);
    setTxt('stat-label-africa', t.Africa);
    setTxt('stat-label-americas', t.Americas);
    setTxt('stat-label-asia', t.Asia);
    setTxt('stat-label-europe', t.Europe);
    setTxt('stat-label-oceania', t.Oceania);

    const searchEl = document.getElementById('search');
    if (searchEl) searchEl.placeholder = t.search;

    // Re-render dynamic components while preserving selection, open panels, and active search filter
    render();
    updateChips();
    if (searchEl && searchEl.value.trim() !== '') {
        filterCountries();
    }
}

function toggleTheme(initial) {
    const isDark = document.body.classList.toggle('dark');
    document.getElementById('theme-icon').innerText = isDark ? '☀️' : '🌙';
    if (!initial) localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

// --- Integrated Map Modal Controls ---

function openMapModal(event) {
    const select = document.getElementById('country-select');
    const selectedCount = select ? select.selectedOptions.length : 0;
    const t = translations[currentLang] || translations.en;

    if (selectedCount === 0) {
        if (event && typeof event.preventDefault === 'function') {
            event.preventDefault();
        }
        showToast(t.noSelectionWarn || translations.en.noSelectionWarn, 'warning');
        const searchEl = document.getElementById('search');
        if (searchEl) searchEl.focus();
        return false;
    }

    const modal = document.getElementById('map-modal');
    const modalTitle = document.getElementById('modal-map-title');
    const modalStats = document.getElementById('modal-map-stats');
    const statTotal = document.getElementById('stat-total');

    if (modalTitle) modalTitle.innerText = t.title;
    if (modalStats && statTotal) modalStats.innerText = statTotal.innerText;
    if (modal) modal.classList.remove('hidden');
    return true;
}

function closeMapModal() {
    const modal = document.getElementById('map-modal');
    if (modal) modal.classList.add('hidden');
}

function printPreviewMap() {
    const frame = document.getElementById('map-preview-frame');
    if (frame && frame.contentWindow) {
        frame.contentWindow.focus();
        frame.contentWindow.print();
    }
}

function openMapInNewTab() {
    const form = document.getElementById('map-form');
    if (!form) return;
    const prevTarget = form.target;
    const prevOnsubmit = form.onsubmit;
    form.target = '_blank';
    form.onsubmit = null;
    form.submit();
    form.target = prevTarget;
    form.onsubmit = prevOnsubmit;
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const modal = document.getElementById('map-modal');
        if (modal && !modal.classList.contains('hidden')) {
            closeMapModal();
        }
    }
});

// --- Smart Auto-Shrink & Auto-Hide Header on Scroll (Window + Accordion) ---
(function setupHeaderScrollBehavior() {
    let lastWinScrollY = window.scrollY || 0;
    let lastAccScrollY = 0;

    function applyScrollState(currentY, deltaY) {
        const header = document.getElementById('app-header');
        if (!header) return;

        if (currentY <= 18) {
            header.classList.remove('header-compact', 'header-hidden');
            return;
        }

        header.classList.add('header-compact');

        if (deltaY > 6 && currentY > 72) {
            header.classList.add('header-hidden');
        } else if (deltaY < -5) {
            header.classList.remove('header-hidden');
        }
    }

    window.addEventListener('scroll', () => {
        const currentY = window.scrollY || document.documentElement.scrollTop || 0;
        const deltaY = currentY - lastWinScrollY;
        lastWinScrollY = currentY;
        applyScrollState(currentY, deltaY);
    }, { passive: true });

    window.addEventListener('DOMContentLoaded', () => {
        const acc = document.getElementById('accordion');
        if (!acc) return;
        acc.addEventListener('scroll', () => {
            const currentY = acc.scrollTop || 0;
            const deltaY = currentY - lastAccScrollY;
            lastAccScrollY = currentY;
            const effectiveY = Math.max(window.scrollY || 0, currentY);
            applyScrollState(effectiveY, deltaY);
        }, { passive: true });
    });
})();

init();
