let currentLang = 'en';
let countriesData = {};

// --- Core Functions ---

async function init() {
    const resp = await fetch('/api/countries');
    countriesData = await resp.json();
    render();
    if (localStorage.getItem('theme') === 'dark') toggleTheme(true);
}

function render() {
    const container = document.getElementById('accordion');
    const select = document.getElementById('country-select');
    const t = translations[currentLang] || translations.en;
    let html = '';
    let options = '';

    for (const [continent, regions] of Object.entries(countriesData)) {
        const id = continent.toLowerCase().replace(/\s/g, '-');
        const continentName = t[continent] || continent;
        html += `
            <div class="continent-container border border-gray-200 rounded-xl overflow-hidden">
                <button type="button" onclick="toggleAcc('${id}')" class="w-full text-left p-3 bg-gray-50 font-bold text-sm flex justify-between">
                    ${continentName} <span id="icon-${id}" class="transition-transform duration-200">▼</span>
                </button>
                <div id="content-${id}" class="continent-content hidden p-2 space-y-2 bg-white">
        `;
        for (const [region, countries] of Object.entries(regions)) {
            const regionName = t[region] || region;
            html += `
                <div class="region-container p-2 border border-gray-50 rounded-lg">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-[10px] font-bold text-gray-400 uppercase">${regionName} <span id="stat-reg-${continent}-${region}" class="text-indigo-500 ml-1">0%</span></span>
                        <button type="button" onclick="toggleRegion('${continent}','${region}')" class="text-[9px] font-black text-indigo-400 hover:text-indigo-600">${t.selectAll}</button>
                    </div>
                    <div class="flex flex-wrap gap-1">
                        ${countries.map(c => {
                options += `<option value="${c.name}">${c.name}</option>`;
                return `<button type="button" id="chip-${c.name}" onclick="toggleCountry('${c.name}')"
                                 class="px-2 py-0.5 border border-gray-200 rounded-full text-[10px] bg-white transition-all">${c.name}</button>`;
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
    chip.classList.toggle('bg-indigo-500', opt.selected);
    chip.classList.toggle('text-white', opt.selected);
    chip.classList.toggle('border-indigo-600', opt.selected);
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
        if (chip) {
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
        area.innerHTML = `<span class="text-xs text-gray-400 w-full text-center py-2">${translations[currentLang].noSelection}</span>`;
    } else {
        area.innerHTML = selected.map(o => `
            <div class="flex items-center gap-1 px-3 py-1.5 bg-indigo-50 text-indigo-700 rounded-xl text-[11px] font-bold border border-indigo-100 shadow-sm transition-all">
                ${o.value} <button type="button" onclick="toggleCountry('${o.value}')" class="hover:text-red-500 ml-1 text-sm">×</button>
            </div>
        `).join('');

        // Re-apply filter if searching
        if (query) filterCountries();
    }
    updateStats();
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
                regStatEl.innerText = `${pct}%`;
            }
        }
        const contId = continent.toLowerCase().replace(/\s/g, '-');
        const contValEl = document.getElementById(`stat-${contId}`);
        if (contValEl) {
            const pct = contTotal > 0 ? Math.round((contVisited / contTotal) * 100) : 0;
            contValEl.innerText = `${pct}%`;
        }
    }

    const totalEl = document.getElementById('stat-total');
    if (totalEl) {
        const totalPct = totalCountries > 0 ? Math.round((totalVisited / totalCountries) * 100) : 0;
        totalEl.innerText = `${totalPct}%`;
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
    });
    updateChips();
}

async function downloadTemplate() {
    window.location.href = '/api/download_template';
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

// Listen for fullscreen changes to adjust UI
document.addEventListener('fullscreenchange', () => {
    const accordion = document.getElementById('accordion');
    if (document.fullscreenElement) {
        accordion.style.maxHeight = '70vh';
    } else {
        accordion.style.maxHeight = '16rem';
    }
});

async function handleFileUpload(input) {
    const file = input.files[0];
    if (!file) return;
    const fd = new FormData();
    fd.append('file', file);
    try {
        const resp = await fetch('/api/upload', { method: 'POST', body: fd });
        const visited = await resp.json();
        if (resp.ok) {
            clearSelection();
            visited.forEach(name => toggleCountry(name));
        } else alert(visited.error);
    } catch (e) { alert("Upload failed"); }
    input.value = "";
}

function toggleAcc(id) {
    document.getElementById(`content-${id}`).classList.toggle('hidden');
    document.getElementById(`icon-${id}`).classList.toggle('rotate-180');
}

function changeLanguage(lang) {
    currentLang = lang;
    const t = translations[lang] || translations.en;

    // Text Elements with fail-safe checks
    const setTxt = (id, text) => {
        const el = document.getElementById(id);
        if (el) el.innerText = text;
    };

    document.title = t.title;
    setTxt('card-title', t.title);
    setTxt('card-desc', t.desc);
    setTxt('btn-download', t.download);
    setTxt('btn-load', t.load);
    setTxt('btn-fullscreen', t.fullscreen);
    setTxt('btn-clear', t.clear);
    setTxt('btn-launch', t.launch);
    setTxt('label-style', t.style);
    setTxt('label-color', t.color);
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

    // Re-render dynamic components
    render();
    updateChips();
    updateStats();
}

function toggleTheme(initial) {
    const isDark = document.body.classList.toggle('dark');
    document.getElementById('theme-icon').innerText = isDark ? '☀️' : '🌙';
    if (!initial) localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

init();
