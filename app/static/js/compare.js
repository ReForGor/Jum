// TechPrice Head-to-Head Multi-Product Comparator (Thai Retail Edition)

let compareIds = [];
let allAvailableProducts = [];

function formatTHB(amount) {
    if (amount === null || amount === undefined) return 'N/A';
    return `฿${Math.round(amount).toLocaleString('th-TH')}`;
}

async function initComparator() {
    try {
        const res = await fetch('/api/products?limit=1000');
        allAvailableProducts = await res.json();
    } catch(err) {
        console.error('Failed to load products for comparator', err);
    }

    const saved = JSON.parse(localStorage.getItem('techprice_compare') || '[]');
    compareIds = saved.filter(id => typeof id === 'number');

    renderSlots();
    if (compareIds.length >= 2) {
        fetchAndRenderComparison();
    } else {
        document.getElementById('comparison-matrix-container')?.classList.add('hidden');
        document.getElementById('compare-empty-state')?.classList.remove('hidden');
    }
}

function renderSlots() {
    const container = document.getElementById('picker-slots');
    if (!container) return;

    let html = '';
    for (let slot = 0; slot < 4; slot++) {
        const prodId = compareIds[slot];
        const prod = prodId ? allAvailableProducts.find(p => p.id === prodId) : null;

        if (prod) {
            html += `
            <div class="bg-[#111827] border border-cyan-500/40 rounded-xl p-4 flex flex-col justify-between shadow-lg relative group">
                <button onclick="removeCompareItem(${prod.id})" class="absolute top-2 right-2 w-6 h-6 rounded-full bg-gray-800 hover:bg-red-600 text-gray-400 hover:text-white flex items-center justify-center text-xs transition-colors shadow">
                    <i class="fa-solid fa-xmark"></i>
                </button>
                <div class="flex items-center gap-3">
                    <img src="${prod.image_url || 'https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=400&q=85'}" class="w-12 h-12 rounded-lg object-contain p-1 bg-gray-900 border border-gray-700 shrink-0">
                    <div class="pr-6">
                        <span class="text-[10px] font-bold text-cyan-400 uppercase">${prod.brand}</span>
                        <h4 class="text-xs font-bold text-white line-clamp-1">${prod.name}</h4>
                        <div class="text-xs font-extrabold text-emerald-400 mt-0.5">${formatTHB(prod.lowest_price || prod.msrp)}</div>
                    </div>
                </div>
            </div>
            `;
        } else {
            html += `
            <div class="border-2 border-dashed border-gray-800 hover:border-gray-700 rounded-xl p-4 flex flex-col items-center justify-center min-h-[80px] bg-gray-900/30 transition-colors">
                <select onchange="addCompareItem(parseInt(this.value))" class="w-full bg-gray-900 border border-gray-700 text-gray-300 text-xs rounded-lg p-2 focus:ring-1 focus:ring-cyan-500">
                    <option value="">+ Add Hardware ${slot + 1}</option>
                    ${allAvailableProducts
                        .filter(p => !compareIds.includes(p.id))
                        .map(p => `<option value="${p.id}">${p.name} (${formatTHB(p.lowest_price || p.msrp)})</option>`)
                        .join('')}
                </select>
            </div>
            `;
        }
    }
    container.innerHTML = html;
}

async function fetchAndRenderComparison() {
    if (compareIds.length < 2) return;

    const matrixContainer = document.getElementById('comparison-matrix-container');
    const emptyState = document.getElementById('compare-empty-state');
    const headRow = document.getElementById('compare-table-head-row');
    const tbody = document.getElementById('compare-table-tbody');

    if (!matrixContainer || !tbody) return;

    emptyState.classList.add('hidden');
    matrixContainer.classList.remove('hidden');

    try {
        const res = await fetch(`/api/compare?ids=${compareIds.join(',')}`);
        const data = await res.json();

        // Render Head Row with Product Cards
        headRow.innerHTML = `
            <th class="p-4 w-48 text-xs font-bold uppercase text-gray-400 tracking-wider bg-gray-900 border-r border-gray-800">
                Specifications
            </th>
            ${data.products.map(p => {
                const isWinner = p.id === data.price_winner_id;
                return `
                <th class="p-4 w-64 text-left border-r border-gray-800 bg-gray-900/90 relative ${isWinner ? 'bg-cyan-950/20' : ''}">
                    ${isWinner ? `
                        <div class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px] font-extrabold mb-2">
                            <i class="fa-solid fa-crown text-amber-400 text-[9px]"></i> Lowest Price in Thailand
                        </div>
                    ` : '<div class="h-5 mb-2"></div>'}
                    <div class="flex items-center gap-3 mb-3">
                        <img src="${p.image_url || 'https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=400&q=85'}" class="w-12 h-12 rounded-lg object-contain p-1 border border-gray-700 bg-gray-800 shrink-0">
                        <div>
                            <span class="text-[10px] uppercase font-bold text-gray-400">${p.brand}</span>
                            <div class="text-xs font-bold text-white line-clamp-2">${p.name}</div>
                        </div>
                    </div>
                    <div class="flex items-baseline justify-between pt-2 border-t border-gray-800">
                        <div>
                            <span class="text-[10px] text-gray-500 block">Lowest Price</span>
                            <span class="text-base font-extrabold ${isWinner ? 'text-emerald-400' : 'text-white'}">${formatTHB(p.lowest_price || p.msrp)}</span>
                        </div>
                        ${p.best_store ? `
                            <div class="text-right">
                                <span class="text-[10px] text-gray-500 block">Best Thai Store</span>
                                <span class="text-xs font-bold text-cyan-400">${p.best_store}</span>
                            </div>
                        ` : ''}
                    </div>
                </th>
                `;
            }).join('')}
        `;

        // Render Specification Rows
        tbody.innerHTML = data.spec_matrix.map(row => {
            const isHighlightRow = ['lowest_price', 'best_store', 'vram', 'cores_threads', 'tdp', 'display', 'capacity'].includes(row.spec_key);
            return `
            <tr class="${isHighlightRow ? 'bg-gray-900/40 font-semibold' : 'hover:bg-gray-800/30'} transition-colors">
                <td class="py-3 px-4 text-gray-300 font-medium text-xs border-r border-gray-800 bg-[#0f172a]/80">
                    ${row.spec_label}
                </td>
                ${data.products.map(p => {
                    let val = row.values[p.id] || '—';
                    if (row.spec_key === 'msrp' && typeof val === 'string' && val.startsWith('$')) {
                        val = formatTHB(p.msrp);
                    }
                    if (row.spec_key === 'lowest_price' && typeof val === 'string' && val.startsWith('$')) {
                        val = formatTHB(p.lowest_price);
                    }
                    const isLowestCell = row.spec_key === 'lowest_price' && p.id === data.price_winner_id;
                    return `
                    <td class="py-3 px-4 text-xs border-r border-gray-800 ${isLowestCell ? 'text-emerald-400 font-extrabold bg-emerald-950/10' : 'text-gray-200'}">
                        ${val}
                    </td>
                    `;
                }).join('')}
            </tr>
            `;
        }).join('');

        // Store Purchase Buttons Row
        tbody.innerHTML += `
        <tr class="bg-gray-900/80">
            <td class="py-4 px-4 text-gray-400 font-bold text-xs border-r border-gray-800">
                Direct Store Links
            </td>
            ${data.products.map(p => {
                const bestListing = p.platforms && p.platforms.length > 0 ? p.platforms[0] : null;
                const url = bestListing ? bestListing.product_url : `https://www.google.com/search?q=${encodeURIComponent(p.name)}`;
                return `
                <td class="py-4 px-4 border-r border-gray-800">
                    <a href="${url}" target="_blank" class="w-full py-2 px-3 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs transition-colors flex items-center justify-center gap-1.5 shadow">
                        <span>Buy on ${p.best_store || 'Store'}</span>
                        <i class="fa-solid fa-arrow-up-right-from-square text-[9px]"></i>
                    </a>
                </td>
                `;
            }).join('')}
        </tr>
        `;

    } catch(err) {
        console.error('Error rendering comparison matrix:', err);
    }
}

function addCompareItem(id) {
    if (!id) return;
    if (compareIds.includes(id)) return;
    if (compareIds.length >= 4) {
        showToast('Maximum 4 products allowed in comparison.', 'warning');
        return;
    }
    compareIds.push(id);
    localStorage.setItem('techprice_compare', JSON.stringify(compareIds));
    renderSlots();
    if (compareIds.length >= 2) {
        fetchAndRenderComparison();
    }
}

function removeCompareItem(id) {
    compareIds = compareIds.filter(i => i !== id);
    localStorage.setItem('techprice_compare', JSON.stringify(compareIds));
    renderSlots();
    if (compareIds.length >= 2) {
        fetchAndRenderComparison();
    } else {
        document.getElementById('comparison-matrix-container')?.classList.add('hidden');
        document.getElementById('compare-empty-state')?.classList.remove('hidden');
    }
}

function clearComparison() {
    compareIds = [];
    localStorage.removeItem('techprice_compare');
    renderSlots();
    document.getElementById('comparison-matrix-container')?.classList.add('hidden');
    document.getElementById('compare-empty-state')?.classList.remove('hidden');
    showToast('Comparison cleared.', 'info');
}

function loadSampleComparison() {
    compareIds = [1, 2, 3];
    localStorage.setItem('techprice_compare', JSON.stringify(compareIds));
    renderSlots();
    fetchAndRenderComparison();
    showToast('Loaded sample GPU comparison matrix (RTX 5090 vs 5080 vs RX 7900 XTX)!', 'success');
}

document.addEventListener('DOMContentLoaded', initComparator);
