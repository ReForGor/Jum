// TechPrice Frontend Core Application (Thai IT Retail Edition)

let currentCategory = 'All';
let currentSearch = '';
let currentStore = '';
let currentBrand = 'All';
let currentMaxPrice = null;
let currentSort = 'cheapest';
let currentCurrency = 'THB'; // Default THB ฿
let currentModalProductId = null;
let priceChartInstance = null;
let searchDebounceTimer = null;
let currentUser = null;

const CURRENCY_RATES = {
    THB: { rate: 1.0, symbol: '฿' },
    USD: { rate: 0.028, symbol: '$' },
    EUR: { rate: 0.026, symbol: '€' },
    GBP: { rate: 0.022, symbol: '£' },
    SGD: { rate: 0.038, symbol: 'S$' },
    JPY: { rate: 4.35, symbol: '¥' }
};

// Format price with active currency
function formatCurrency(amountInTHB) {
    if (amountInTHB === null || amountInTHB === undefined) return 'N/A';
    const curr = CURRENCY_RATES[currentCurrency] || CURRENCY_RATES.THB;
    const converted = amountInTHB * curr.rate;
    if (currentCurrency === 'THB' || currentCurrency === 'JPY') {
        return `${curr.symbol}${Math.round(converted).toLocaleString('th-TH')}`;
    }
    return `${curr.symbol}${converted.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function changeCurrency(currCode) {
    currentCurrency = currCode;
    loadProducts();
    if (currentModalProductId) {
        openProductModal(currentModalProductId);
    }
    showToast(`Currency set to ${currCode}`, 'info');
}

// ----------------- Authentication Management -----------------

async function checkAuthState() {
    try {
        const res = await fetch('/api/auth/me');
        if (res.ok) {
            currentUser = await res.json();
            document.getElementById('user-guest-box')?.classList.add('hidden');
            const loggedInBox = document.getElementById('user-logged-in-box');
            if (loggedInBox) {
                loggedInBox.classList.remove('hidden');
                loggedInBox.classList.add('flex');
            }
            document.getElementById('nav-user-name').textContent = currentUser.username;
            document.getElementById('dropdown-full-name').textContent = currentUser.full_name || currentUser.username;
            document.getElementById('dropdown-email').textContent = currentUser.email;

            // Admin Role UI Toggle
            const adminBadge = document.getElementById('nav-admin-badge');
            const adminLink = document.getElementById('nav-admin-link');
            if (currentUser.is_admin) {
                if (adminBadge) adminBadge.classList.remove('hidden');
                if (adminLink) {
                    adminLink.classList.remove('hidden');
                    adminLink.classList.add('flex');
                }
            } else {
                if (adminBadge) adminBadge.classList.add('hidden');
                if (adminLink) adminLink.classList.add('hidden');
            }
        } else {
            currentUser = null;
            document.getElementById('user-guest-box')?.classList.remove('hidden');
            const loggedInBox = document.getElementById('user-logged-in-box');
            if (loggedInBox) {
                loggedInBox.classList.add('hidden');
                loggedInBox.classList.remove('flex');
            }
        }
    } catch(err) {
        currentUser = null;
    }
    checkNotificationsCount();
}

function openAuthModal(tab = 'login') {
    document.getElementById('auth-modal')?.classList.remove('hidden');
    switchAuthTab(tab);
}

function closeAuthModal() {
    document.getElementById('auth-modal')?.classList.add('hidden');
}

function switchAuthTab(tab) {
    const loginForm = document.getElementById('login-form');
    const regForm = document.getElementById('register-form');
    const tabLogin = document.getElementById('tab-btn-login');
    const tabReg = document.getElementById('tab-btn-register');

    if (tab === 'login') {
        loginForm?.classList.remove('hidden');
        regForm?.classList.add('hidden');
        tabLogin?.classList.add('text-cyan-400', 'border-b-2', 'border-cyan-400');
        tabLogin?.classList.remove('text-gray-400');
        tabReg?.classList.remove('text-cyan-400', 'border-b-2', 'border-cyan-400');
        tabReg?.classList.add('text-gray-400');
    } else {
        loginForm?.classList.add('hidden');
        regForm?.classList.remove('hidden');
        tabReg?.classList.add('text-cyan-400', 'border-b-2', 'border-cyan-400');
        tabReg?.classList.remove('text-gray-400');
        tabLogin?.classList.remove('text-cyan-400', 'border-b-2', 'border-cyan-400');
        tabLogin?.classList.add('text-gray-400');
    }
}

async function handleLoginSubmit(e) {
    e.preventDefault();
    const loginId = document.getElementById('login-id').value;
    const password = document.getElementById('login-password').value;

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ email_or_username: loginId, password: password })
        });
        const data = await res.json();
        if (res.ok) {
            showToast(`Welcome back, ${data.user.username}!`, 'success');
            closeAuthModal();
            checkAuthState();
        } else {
            showToast(data.detail || 'Login failed', 'error');
        }
    } catch(err) {
        showToast('Login request error', 'error');
    }
}

async function handleRegisterSubmit(e) {
    e.preventDefault();
    const fullName = document.getElementById('reg-name').value;
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;

    try {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ full_name: fullName, username: username, email: email, password: password })
        });
        const data = await res.json();
        if (res.ok) {
            showToast(`Account created! Welcome, ${data.user.username}!`, 'success');
            closeAuthModal();
            checkAuthState();
        } else {
            showToast(data.detail || 'Registration failed', 'error');
        }
    } catch(err) {
        showToast('Registration error', 'error');
    }
}

async function handleLogout() {
    await fetch('/api/auth/logout', { method: 'POST' });
    showToast('Logged out successfully', 'info');
    document.getElementById('user-dropdown')?.classList.add('hidden');
    checkAuthState();
}

function toggleUserDropdown() {
    document.getElementById('user-dropdown')?.classList.toggle('hidden');
}

// ----------------- Notification Center -----------------

async function checkNotificationsCount() {
    try {
        const res = await fetch('/api/notifications?limit=20');
        const notifs = await res.json();
        const unreadCount = notifs.filter(n => !n.is_read).length;
        const badge = document.getElementById('notif-badge');
        if (badge) {
            if (unreadCount > 0) {
                badge.textContent = unreadCount;
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
        }
    } catch(err) {
        console.error('Failed to check notifications', err);
    }
}

async function toggleNotificationDropdown() {
    const dropdown = document.getElementById('notif-dropdown');
    if (!dropdown) return;
    dropdown.classList.toggle('hidden');

    if (!dropdown.classList.contains('hidden')) {
        const list = document.getElementById('notif-items-list');
        list.innerHTML = '<div class="p-4 text-center text-xs text-gray-500"><i class="fa-solid fa-spinner fa-spin mr-1"></i> Loading alerts...</div>';

        try {
            const res = await fetch('/api/notifications?limit=15');
            const notifs = await res.json();

            if (notifs.length === 0) {
                list.innerHTML = `
                <div class="p-6 text-center text-xs text-gray-400">
                    <i class="fa-solid fa-bell-slash text-gray-600 text-xl mb-1 block"></i>
                    No price drop alerts yet.
                </div>`;
                return;
            }

            list.innerHTML = notifs.map(n => {
                const timeStr = new Date(n.created_at).toLocaleDateString('th-TH', { hour: '2-digit', minute: '2-digit' });
                return `
                <div class="p-3 ${n.is_read ? 'bg-transparent' : 'bg-cyan-950/20'} hover:bg-gray-800/60 transition-colors flex items-start gap-3 relative group">
                    <img src="${n.product_image || 'https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=100'}" class="w-10 h-10 rounded-lg object-cover bg-gray-900 border border-gray-700 mt-0.5">
                    <div class="flex-1 pr-4">
                        <div class="flex items-center gap-1.5 mb-0.5">
                            <span class="text-[10px] font-bold text-amber-400 uppercase">${n.store_name || 'Thai Store'}</span>
                            <span class="text-[10px] text-gray-500">• ${timeStr}</span>
                        </div>
                        <div class="text-xs font-bold text-white mb-1 line-clamp-1">${n.title}</div>
                        <div class="text-[11px] text-gray-300 mb-2 leading-relaxed">${n.message}</div>
                        
                        <div class="flex items-center gap-2">
                            ${n.product_url ? `
                                <a href="${n.product_url}" target="_blank" class="px-2 py-0.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-[10px] transition-colors flex items-center gap-1">
                                    <span>Buy ฿${n.new_price.toLocaleString('th-TH')}</span>
                                    <i class="fa-solid fa-arrow-up-right-from-square text-[8px]"></i>
                                </a>
                            ` : ''}
                            ${!n.is_read ? `
                                <button onclick="markNotificationRead(${n.id})" class="text-[10px] text-gray-400 hover:text-cyan-400">
                                    Mark Read
                                </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
                `;
            }).join('');
        } catch(err) {
            list.innerHTML = '<div class="p-3 text-xs text-red-400">Failed to load alerts.</div>';
        }
    }
}

async function markNotificationRead(id) {
    await fetch(`/api/notifications/${id}/read`, { method: 'POST' });
    checkNotificationsCount();
    toggleNotificationDropdown();
    toggleNotificationDropdown(); // refresh dropdown
}

async function markAllNotificationsRead() {
    await fetch('/api/notifications/read-all', { method: 'POST' });
    checkNotificationsCount();
    showToast('All notifications marked as read', 'info');
    toggleNotificationDropdown();
    toggleNotificationDropdown();
}

// ----------------- Product Catalog -----------------

async function loadProducts() {
    const grid = document.getElementById('product-grid');
    const emptyState = document.getElementById('empty-state');
    const resultsCount = document.getElementById('results-count');

    if (!grid) return;

    grid.innerHTML = Array(6).fill(0).map(() => `
        <div class="bg-[#111827] border border-gray-800 rounded-2xl p-5 animate-pulse space-y-4">
            <div class="h-44 bg-gray-800 rounded-xl"></div>
            <div class="h-4 bg-gray-800 rounded w-1/3"></div>
            <div class="h-5 bg-gray-800 rounded w-3/4"></div>
            <div class="h-8 bg-gray-800 rounded"></div>
        </div>
    `).join('');

    try {
        let url = `/api/products?sort_by=${currentSort}&limit=1000`;
        if (currentCategory && currentCategory !== 'All') url += `&category=${encodeURIComponent(currentCategory)}`;
        if (currentSearch) url += `&q=${encodeURIComponent(currentSearch)}`;
        if (currentStore) url += `&store_slug=${encodeURIComponent(currentStore)}`;
        if (currentBrand && currentBrand !== 'All') url += `&brand=${encodeURIComponent(currentBrand)}`;
        if (currentMaxPrice) url += `&max_price=${currentMaxPrice}`;

        const res = await fetch(url);
        const products = await res.json();
        const totalCount = res.headers.get('X-Total-Count') || products.length;

        if (resultsCount) {
            resultsCount.textContent = t('showing_items', { count: products.length });
        }

        if (products.length === 0) {
            grid.innerHTML = '';
            if (emptyState) emptyState.classList.remove('hidden');
            return;
        }

        if (emptyState) emptyState.classList.add('hidden');

        grid.innerHTML = products.map(p => renderProductCard(p)).join('');

    } catch (err) {
        console.error('Error loading products:', err);
        grid.innerHTML = `<div class="col-span-full text-center text-red-400 py-12">${t('failed_load_products')}</div>`;
    }
}

function renderProductCard(p) {
    const lowest = p.lowest_price !== null ? formatCurrency(p.lowest_price) : formatCurrency(p.msrp);
    const msrp = p.msrp ? formatCurrency(p.msrp) : null;
    const hasDiscount = p.max_discount_percent > 0;
    const savingsAmount = p.msrp && p.lowest_price && p.msrp > p.lowest_price ? formatCurrency(p.msrp - p.lowest_price) : null;
    const categoryName = t(p.category) || p.category;

    return `
    <div class="bg-[#111827] border border-gray-800 hover:border-cyan-500/50 rounded-2xl p-5 flex flex-col justify-between shadow-xl transition-all hover:shadow-cyan-900/10 group">
        <div>
            <!-- Image & Badges -->
            <div class="relative mb-4 overflow-hidden rounded-xl bg-gray-950/80 h-48 flex items-center justify-center border border-gray-800 p-3">
                <img 
                    src="${p.image_url || 'https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=1200&q=85'}" 
                    alt="${p.name}" 
                    class="max-h-full max-w-full object-contain group-hover:scale-105 transition-transform duration-300 drop-shadow-md"
                    loading="lazy"
                >
                <!-- Category Badge -->
                <div class="absolute top-2 left-2 bg-black/75 backdrop-blur-md px-2 py-0.5 rounded-md text-[10px] text-cyan-300 font-semibold border border-cyan-900/50">
                    ${categoryName}
                </div>

                ${hasDiscount ? `
                    <div class="absolute top-2 right-2 bg-gradient-to-r from-red-600 to-amber-600 text-white font-extrabold text-[11px] px-2 py-0.5 rounded-md shadow flex items-center gap-1">
                        <i class="fa-solid fa-tag text-[9px]"></i> -${p.max_discount_percent}%
                    </div>
                ` : ''}

                <!-- Stores Count Pill (Strict 4-Store Verification) -->
                <div class="absolute bottom-2 right-2 bg-black/80 backdrop-blur-md px-2 py-0.5 rounded text-[10px] text-emerald-400 font-bold flex items-center gap-1 border border-emerald-800/80">
                    <i class="fa-solid fa-circle-check text-emerald-400 text-[9px]"></i> ${t('all_4_stores_badge')}
                </div>
            </div>

            <!-- Brand & Name -->
            <div class="flex items-center gap-2 mb-1">
                <span class="text-[10px] font-extrabold uppercase tracking-wider text-gray-400 px-1.5 py-0.5 bg-gray-800/80 rounded border border-gray-700/60">${p.brand}</span>
                ${p.model_no ? `<span class="text-[10px] font-mono text-gray-500">${p.model_no}</span>` : ''}
            </div>
            
            <h3 class="text-sm font-bold text-white mb-2 line-clamp-2 group-hover:text-cyan-400 transition-colors" title="${p.name}">
                ${p.name}
            </h3>

            <!-- Price Breakdown Banner -->
            <div class="rounded-xl bg-gray-900/90 border border-gray-800 p-3 mb-3">
                <div class="flex items-baseline justify-between mb-1">
                    <div>
                        <span class="text-[10px] text-gray-400 block">${t('card_lowest_price')}</span>
                        <span class="text-xl font-extrabold text-emerald-400">${lowest}</span>
                    </div>
                    ${msrp ? `
                        <div class="text-right">
                            <span class="text-[10px] text-gray-500 block">${t('card_msrp')}</span>
                            <span class="text-xs text-gray-500 line-through">${msrp}</span>
                        </div>
                    ` : ''}
                </div>

                <div class="flex items-center justify-between text-[11px] pt-2 border-t border-gray-800/80">
                    <span class="text-gray-400 flex items-center gap-1">
                        <i class="fa-solid fa-crown text-amber-400 text-[10px]"></i>
                        <strong class="text-gray-200">${p.best_store_name || 'JIB / iHaveCPU / Advice'}</strong>
                    </span>
                    ${p.best_product_url ? `
                        <a href="${p.best_product_url}" target="_blank" class="px-2 py-0.5 rounded bg-emerald-900/70 hover:bg-emerald-600 text-emerald-300 hover:text-white border border-emerald-700/80 font-bold text-[10px] transition-all flex items-center gap-1" title="ไปยังร้านค้าเพื่อใส่ตะกร้า">
                            <i class="fa-solid fa-cart-shopping text-[9px]"></i>
                            <span>${t('go_to_cart')}</span>
                            <i class="fa-solid fa-arrow-up-right-from-square text-[8px]"></i>
                        </a>
                    ` : (savingsAmount ? `<span class="text-emerald-400 font-medium">${t('card_save')} ${savingsAmount}</span>` : `<span class="text-gray-500">${t('card_official_price')}</span>`)}
                </div>
            </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center gap-2 pt-2">
            <button 
                onclick="openProductModal(${p.id})" 
                class="flex-1 py-2 px-3 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs transition-colors flex items-center justify-center gap-1.5 shadow-md"
            >
                <i class="fa-solid fa-arrows-split-up-and-left text-[11px]"></i>
                <span>${t('card_compare_btn')}</span>
            </button>

            <button 
                onclick="addToHeadToHead(${p.id}, '${p.name.replace(/'/g, "\\'")}')" 
                class="p-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-cyan-400 border border-gray-700 text-xs transition-colors"
                title="${t('card_add_compare')}"
            >
                <i class="fa-solid fa-scale-balanced"></i>
            </button>
        </div>
    </div>
    `;
}

// ----------------- Filter Handlers -----------------

function setCategory(cat) {
    currentCategory = cat;
    document.querySelectorAll('.category-btn').forEach(btn => {
        const btnCat = btn.getAttribute('data-category') || btn.textContent.trim();
        if (btnCat === cat || (cat === 'All' && (btnCat === 'All' || btnCat.startsWith('All Hardware')))) {
            btn.classList.add('active', 'bg-cyan-600', 'text-white');
            btn.classList.remove('bg-gray-800/80', 'text-gray-300');
        } else {
            btn.classList.remove('active', 'bg-cyan-600', 'text-white');
            btn.classList.add('bg-gray-800/80', 'text-gray-300');
        }
    });
    loadProducts();
}

function applyFilters() {
    const searchInput = document.getElementById('search-input');
    const storeFilter = document.getElementById('store-filter');
    const brandFilter = document.getElementById('brand-filter');
    const maxPriceInput = document.getElementById('max-price-input');
    const sortSelect = document.getElementById('sort-select');

    if (searchInput) currentSearch = searchInput.value.trim();
    if (storeFilter) currentStore = storeFilter.value;
    if (brandFilter) currentBrand = brandFilter.value;
    if (maxPriceInput) currentMaxPrice = maxPriceInput.value ? parseFloat(maxPriceInput.value) : null;
    if (sortSelect) currentSort = sortSelect.value;

    loadProducts();
}

function resetAllFilters() {
    currentCategory = 'All';
    currentSearch = '';
    currentStore = '';
    currentBrand = 'All';
    currentMaxPrice = null;
    currentSort = 'cheapest';

    const searchInput = document.getElementById('search-input');
    const storeFilter = document.getElementById('store-filter');
    const brandFilter = document.getElementById('brand-filter');
    const maxPriceInput = document.getElementById('max-price-input');
    const sortSelect = document.getElementById('sort-select');

    if (searchInput) searchInput.value = '';
    if (storeFilter) storeFilter.value = '';
    if (brandFilter) brandFilter.value = 'All';
    if (maxPriceInput) maxPriceInput.value = '';
    if (sortSelect) sortSelect.value = 'cheapest';

    setCategory('All');
}

// ----------------- Live Search Autocomplete -----------------

function handleSearchInput(query) {
    const clearBtn = document.getElementById('clear-search-btn');
    const suggestionsBox = document.getElementById('search-suggestions');
    if (!suggestionsBox) return;

    if (query.trim().length > 0 && clearBtn) {
        clearBtn.classList.remove('hidden');
    } else if (clearBtn) {
        clearBtn.classList.add('hidden');
    }

    clearTimeout(searchDebounceTimer);

    if (query.trim().length < 2) {
        suggestionsBox.classList.add('hidden');
        return;
    }

    searchDebounceTimer = setTimeout(async () => {
        try {
            const res = await fetch(`/api/search/suggestions?q=${encodeURIComponent(query.trim())}&limit=6`);
            const items = await res.json();

            if (items.length === 0) {
                suggestionsBox.innerHTML = `<div class="p-3 text-xs text-gray-500">No matching hardware found</div>`;
                suggestionsBox.classList.remove('hidden');
                return;
            }

            suggestionsBox.innerHTML = items.map(item => `
                <div onclick="selectSuggestion(${item.id})" class="p-3 hover:bg-gray-800/80 cursor-pointer flex items-center justify-between gap-3 transition-colors">
                    <div class="flex items-center gap-3">
                        <img src="${item.image_url || 'https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=400&q=85'}" class="w-9 h-9 rounded-lg object-contain p-0.5 border border-gray-700 bg-gray-900 shrink-0">
                        <div>
                            <div class="text-xs font-bold text-white">${item.name}</div>
                            <div class="text-[10px] text-gray-400">${item.brand} • ${item.category}</div>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-xs font-bold text-emerald-400">${formatCurrency(item.lowest_price)}</div>
                        <div class="text-[10px] text-gray-500">${item.store_count} Thai Stores</div>
                    </div>
                </div>
            `).join('');
            suggestionsBox.classList.remove('hidden');
        } catch (err) {
            console.error(err);
        }
    }, 200);
}

function clearSearch() {
    const input = document.getElementById('search-input');
    const clearBtn = document.getElementById('clear-search-btn');
    const suggestionsBox = document.getElementById('search-suggestions');
    if (input) input.value = '';
    if (clearBtn) clearBtn.classList.add('hidden');
    if (suggestionsBox) suggestionsBox.classList.add('hidden');
    currentSearch = '';
    loadProducts();
}

function selectSuggestion(id) {
    const suggestionsBox = document.getElementById('search-suggestions');
    if (suggestionsBox) suggestionsBox.classList.add('hidden');
    openProductModal(id);
}

document.addEventListener('click', (e) => {
    const suggestionsBox = document.getElementById('search-suggestions');
    const searchInput = document.getElementById('search-input');
    if (suggestionsBox && searchInput && !suggestionsBox.contains(e.target) && !searchInput.contains(e.target)) {
        suggestionsBox.classList.add('hidden');
    }
    const notifDropdown = document.getElementById('notif-dropdown');
    const notifBell = document.getElementById('notif-bell-btn');
    if (notifDropdown && notifBell && !notifDropdown.contains(e.target) && !notifBell.contains(e.target)) {
        notifDropdown.classList.add('hidden');
    }
});

// ----------------- Platform Comparison Modal -----------------

async function openProductModal(productId) {
    currentModalProductId = productId;
    const modal = document.getElementById('compare-modal');
    if (!modal) return;

    modal.classList.remove('hidden');

    try {
        const res = await fetch(`/api/products/${productId}`);
        const data = await res.json();

        document.getElementById('modal-product-img').src = data.image_url || 'https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=1200&q=85';
        document.getElementById('modal-product-name').textContent = data.name;
        document.getElementById('modal-product-brand').textContent = data.brand;
        document.getElementById('modal-product-category').textContent = t(data.category) || data.category;
        document.getElementById('modal-product-msrp').textContent = data.msrp ? formatCurrency(data.msrp) : 'N/A';
        document.getElementById('modal-product-lowest').textContent = `${formatCurrency(data.lowest_price)} (${data.best_store || 'Thai Store'})`;

        const savingsBadge = document.getElementById('modal-savings-badge');
        if (data.total_savings && data.total_savings > 0) {
            savingsBadge.textContent = `${t('modal_save_up_to')} ${formatCurrency(data.total_savings)}`;
            savingsBadge.classList.remove('hidden');
        } else {
            savingsBadge.classList.add('hidden');
        }

        // Render Platform Pricing Table (JIB, iHaveCPU, BaNANA, Advice)
        const tbody = document.getElementById('modal-platforms-tbody');
        tbody.innerHTML = (data.platforms || []).map(plat => {
            const isLowest = plat.is_lowest;
            const diffText = isLowest 
                ? `<span class="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 font-bold border border-emerald-800 text-[10px]">🔥 ${t('cheapest_badge')}</span>`
                : `<span class="text-gray-400 font-mono text-[11px]">+${formatCurrency(plat.price_diff_from_lowest)}</span>`;

            const stockColor = plat.stock_status === 'in_stock' ? 'text-emerald-400 bg-emerald-950/80 border-emerald-800/80' : 
                               plat.stock_status === 'low_stock' ? 'text-amber-400 bg-amber-950/80 border-amber-800/80' : 'text-red-400 bg-red-950/80 border-red-800/80';
            const stockLabel = plat.stock_status === 'in_stock' ? t('in_stock') : (plat.stock_status === 'low_stock' ? t('low_stock') : t('out_of_stock'));

            return `
            <tr class="${isLowest ? 'bg-cyan-950/20' : 'hover:bg-gray-800/40'} transition-colors">
                <td class="py-3.5 px-4">
                    <div class="flex items-center gap-2.5">
                        <div class="w-3.5 h-3.5 rounded-full" style="background-color: ${plat.store_color}"></div>
                        <span class="font-bold text-white text-xs sm:text-sm">${plat.store_name}</span>
                    </div>
                </td>
                <td class="py-3.5 px-4">
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${stockColor}">
                        ${stockLabel}
                    </span>
                </td>
                <td class="py-3.5 px-4">
                    <span class="text-sm font-extrabold ${isLowest ? 'text-emerald-400' : 'text-white'}">
                        ${formatCurrency(plat.price)}
                    </span>
                    ${plat.original_price ? `<span class="text-[10px] text-gray-500 line-through ml-1">${formatCurrency(plat.original_price)}</span>` : ''}
                </td>
                <td class="py-3.5 px-4 text-emerald-400 font-semibold text-xs">
                    ${t('free_shipping').toUpperCase()}
                </td>
                <td class="py-3.5 px-4">
                    <div class="flex flex-col">
                        <span class="font-bold text-white text-xs">${formatCurrency(plat.total_price)}</span>
                        ${diffText}
                    </div>
                </td>
                <td class="py-3.5 px-4 text-right">
                    <a 
                        href="${plat.product_url}" 
                        target="_blank" 
                        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg ${isLowest ? 'bg-emerald-600 hover:bg-emerald-500 text-white' : 'bg-gray-800 hover:bg-gray-700 text-gray-200'} font-semibold text-xs transition-colors shadow"
                        title="ไปยังร้านค้าเพื่อใส่ตะกร้าและสั่งซื้อ"
                    >
                        <i class="fa-solid fa-cart-shopping text-[11px]"></i>
                        <span>${t('buy_on')} ${plat.store_name}</span>
                        <i class="fa-solid fa-arrow-up-right-from-square text-[9px]"></i>
                    </a>
                </td>
            </tr>
            `;
        }).join('');

        // Render Specs Grid
        const specsGrid = document.getElementById('modal-specs-grid');
        const specs = data.specs || {};
        if (Object.keys(specs).length === 0) {
            specsGrid.innerHTML = `<div class="text-gray-500 italic">${t('modal_no_specs')}</div>`;
        } else {
            specsGrid.innerHTML = Object.entries(specs).map(([k, v]) => `
                <div class="p-2.5 rounded-lg bg-gray-900 border border-gray-800 flex justify-between gap-2">
                    <span class="text-gray-400 capitalize">${k.replace(/_/g, ' ')}:</span>
                    <span class="font-medium text-gray-200 text-right">${v}</span>
                </div>
            `).join('');
        }

        // Set alert form default suggested price (5% lower)
        const alertPriceInput = document.getElementById('alert-price');
        if (alertPriceInput && data.lowest_price) {
            alertPriceInput.value = Math.round((data.lowest_price * 0.95) / 10) * 10;
        }

        // Pre-fill email if logged in
        if (currentUser && document.getElementById('alert-email')) {
            document.getElementById('alert-email').value = currentUser.email;
        }

        // Load 30-day price history chart
        loadProductHistory(productId, 30);

    } catch (err) {
        console.error('Error opening product modal:', err);
    }
}

function closeModal() {
    const modal = document.getElementById('compare-modal');
    if (modal) modal.classList.add('hidden');
}

// ----------------- Price History Chart.js -----------------

async function loadProductHistory(productId, days = 30) {
    try {
        const res = await fetch(`/api/prices/history/${productId}?days=${days}`);
        const data = await res.json();

        // Update stat badges
        document.getElementById('stat-hist-lowest').textContent = formatCurrency(data.lowest_historical_price);
        document.getElementById('stat-hist-highest').textContent = formatCurrency(data.highest_historical_price);
        document.getElementById('stat-hist-current').textContent = formatCurrency(data.current_lowest_price);

        // Update range button active state
        document.querySelectorAll('.chart-range-btn').forEach(btn => {
            if (parseInt(btn.getAttribute('data-days')) === days) {
                btn.classList.add('active', 'bg-cyan-600', 'text-white', 'font-semibold');
                btn.classList.remove('text-gray-400');
            } else {
                btn.classList.remove('active', 'bg-cyan-600', 'text-white', 'font-semibold');
                btn.classList.add('text-gray-400');
            }
        });

        // Collect all distinct dates and sort chronologically
        const dateMap = new Map();
        (data.series || []).forEach(s => {
            (s.data_points || []).forEach(dp => {
                const iso = dp.iso_date || (dp.timestamp ? dp.timestamp.split('T')[0] : dp.date);
                if (!dateMap.has(iso)) {
                    dateMap.set(iso, dp.date || iso);
                }
            });
        });

        // Chronologically sort dates (YYYY-MM-DD sorts perfectly in natural order)
        const sortedIsoDates = Array.from(dateMap.keys()).sort();
        const labels = sortedIsoDates.map(iso => dateMap.get(iso));

        // Build datasets
        const datasets = (data.series || []).map(s => {
            const priceMap = {};
            (s.data_points || []).forEach(dp => {
                const iso = dp.iso_date || (dp.timestamp ? dp.timestamp.split('T')[0] : dp.date);
                priceMap[iso] = dp.price;
            });

            let runningPrice = null;
            const plotData = sortedIsoDates.map(iso => {
                if (priceMap[iso] !== undefined && priceMap[iso] !== null) {
                    runningPrice = priceMap[iso];
                    return runningPrice;
                }
                return runningPrice;
            });

            return {
                label: s.store_name,
                data: plotData,
                borderColor: s.store_color || '#06b6d4',
                backgroundColor: s.store_color ? `${s.store_color}22` : 'rgba(6, 182, 212, 0.1)',
                borderWidth: 2,
                tension: 0.1,
                pointRadius: 3,
                pointHoverRadius: 6,
                spanGaps: true
            };
        });

        const ctx = document.getElementById('priceHistoryChart').getContext('2d');
        if (priceChartInstance) {
            priceChartInstance.destroy();
        }

        priceChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#94a3b8',
                            font: { size: 11, family: 'Inter' },
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        backgroundColor: '#0f172a',
                        borderColor: '#1e293b',
                        borderWidth: 1,
                        titleColor: '#f8fafc',
                        bodyColor: '#cbd5e1',
                        callbacks: {
                            label: function(context) {
                                return ` ${context.dataset.label}: ${formatCurrency(context.parsed.y)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: '#1e293b' },
                        ticks: { color: '#64748b', font: { size: 10 } }
                    },
                    y: {
                        grid: { color: '#1e293b' },
                        ticks: {
                            color: '#64748b',
                            font: { size: 10 },
                            callback: function(val) {
                                return formatCurrency(val);
                            }
                        }
                    }
                }
            }
        });

    } catch (err) {
        console.error('Error loading history chart:', err);
    }
}

// ----------------- Price Alert Form -----------------

async function handleCreateAlert(e) {
    e.preventDefault();
    if (!currentModalProductId) return;

    const email = document.getElementById('alert-email')?.value || (currentUser ? currentUser.email : '');
    const targetPrice = parseFloat(document.getElementById('alert-price').value);

    try {
        const res = await fetch('/api/alerts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                product_id: currentModalProductId,
                email: email,
                target_price: targetPrice,
                currency: 'THB'
            })
        });

        if (res.ok) {
            const emailMsg = email ? ` (ส่งอีเมลแจ้งไปที่ ${email})` : '';
            showToast(`ตั้งแจ้งเตือนราคา ${formatCurrency(targetPrice)} สำเร็จ!${emailMsg}`, 'success');
            checkNotificationsCount();
        } else {
            const data = await res.json();
            showToast(data.detail || 'Failed to create alert.', 'error');
        }
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// ----------------- Head to Head Comparison Helper -----------------

function addToHeadToHead(id, name) {
    let compareList = JSON.parse(localStorage.getItem('techprice_compare') || '[]');
    if (compareList.includes(id)) {
        showToast(`${name} is already in comparison list!`, 'info');
        return;
    }
    if (compareList.length >= 4) {
        showToast('Maximum 4 items can be compared at once.', 'warning');
        return;
    }
    compareList.push(id);
    localStorage.setItem('techprice_compare', JSON.stringify(compareList));
    showToast(`Added ${name} to Head-to-Head Compare!`, 'success');
}

// ----------------- Global Scraper Action -----------------

async function triggerGlobalScrape() {
    const btn = document.getElementById('global-scrape-btn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-arrows-rotate fa-spin text-cyan-400"></i> Scraping JIB, iHaveCPU...';
    }

    try {
        const res = await fetch('/api/scrapers/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ simulate_live: true })
        });
        const data = await res.json();
        showToast(`Refreshed prices across JIB, iHaveCPU, BaNANA, Advice! (${data.triggered_alerts} alerts triggered)`, 'success');
        loadProducts();
        checkNotificationsCount();
    } catch (err) {
        showToast('Scraper run failed.', 'error');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-arrows-rotate text-cyan-400"></i> <span>Refresh Prices</span>';
        }
    }
}

// ----------------- Toast Notifications -----------------

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast-enter pointer-events-auto flex items-center gap-2.5 px-4 py-3 rounded-xl shadow-2xl text-xs font-medium text-white transition-all max-w-sm';

    if (type === 'success') {
        toast.classList.add('bg-emerald-600', 'border', 'border-emerald-500');
        toast.innerHTML = `<i class="fa-solid fa-circle-check text-base"></i> <span>${message}</span>`;
    } else if (type === 'error') {
        toast.classList.add('bg-red-600', 'border', 'border-red-500');
        toast.innerHTML = `<i class="fa-solid fa-triangle-exclamation text-base"></i> <span>${message}</span>`;
    } else if (type === 'warning') {
        toast.classList.add('bg-amber-600', 'border', 'border-amber-500');
        toast.innerHTML = `<i class="fa-solid fa-bell text-base"></i> <span>${message}</span>`;
    } else {
        toast.classList.add('bg-gray-800', 'border', 'border-cyan-500/50');
        toast.innerHTML = `<i class="fa-solid fa-circle-info text-cyan-400 text-base"></i> <span>${message}</span>`;
    }

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    if (menu) menu.classList.toggle('hidden');
}

// Language Switch Callback
window.onLanguageChanged = function(lang) {
    loadProducts();
    const modal = document.getElementById('compare-modal');
    if (currentModalProductId && modal && !modal.classList.contains('hidden')) {
        openProductModal(currentModalProductId);
    }
};

// Init on DOM load
document.addEventListener('DOMContentLoaded', () => {
    checkAuthState();
    loadProducts();
});
