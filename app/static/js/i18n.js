// TechPrice Bilingual i18n Translation Engine (Thai / English)

const TRANSLATIONS = {
    th: {
        // Navigation
        nav_catalog: 'รวมสินค้า & เปรียบเทียบราคา',
        nav_compare: 'เปรียบเทียบสเปก',
        nav_deals: 'ดีลลดราคา',
        nav_watchlist: 'รายการติดตาม',
        nav_scrapers: 'ระบบดึงราคา',
        nav_api: 'REST API',
        btn_refresh_prices: 'รีเฟรชราคา',
        sign_in: 'เข้าสู่ระบบ',
        create_account: 'สมัครสมาชิก',
        admin_portal: 'จัดการระบบ (Admin)',
        sign_out: 'ออกจากระบบ',
        my_watchlist: 'รายการติดตามของฉัน',
        demo_login: 'เข้าสู่ระบบด้วยบัญชีทดสอบ',

        // Mobile Nav
        mobile_catalog: 'รวมสินค้า & เปรียบเทียบราคา',
        mobile_compare: 'เปรียบเทียบสเปก',
        mobile_deals: 'ดีลลดราคาพิเศษ',
        mobile_watchlist: 'รายการติดตาม & แจ้งเตือน',
        mobile_scrapers: 'ระบบดึงราคาไทย (JIB, iHaveCPU, BaNANA, Advice)',
        mobile_api: 'REST API สำหรับนักพัฒนา',
        mobile_docs: 'เอกสาร Swagger API',

        // Hero Section
        hero_badge: 'ระบบติดตามและแจ้งเตือนราคาอุปกรณ์ไอทีประเทศไทย',
        hero_title_prefix: 'เปรียบเทียบ',
        hero_title_gradient: 'ราคาอุปกรณ์ไอที',
        hero_title_suffix: 'จากร้านค้าชั้นนำในไทย',
        hero_desc: 'ระบบรวบรวมราคาแบบเรียลไทม์ เปรียบเทียบราคาการ์ดจอ ซีพียู โน้ตบุ๊ก SSD จอมอนิเตอร์ จาก JIB, iHaveCPU, BaNANA IT และ Advice',
        search_placeholder: 'ค้นหาการ์ดจอ (RTX 5090, 4070), ซีพียู (9800X3D), โน้ตบุ๊ก, SSD...',
        search_btn: 'ค้นหา',

        // Stats Row
        stat_hardware: 'สินค้าที่ติดตามในระบบ',
        stat_stores: 'ร้านค้าไอทีไทย',
        stat_stores_desc: 'JIB, iHaveCPU, BaNANA, Advice',
        stat_listings: 'รายการราคาเปรียบเทียบ',
        stat_listings_desc: 'ราคาอัปเดตแบบเรียลไทม์',
        stat_alerts: 'ระบบแจ้งเตือน',
        stat_alerts_desc: 'แจ้งเตือนเมื่อราคาลดลง',

        // Categories
        cat_all: 'สินค้าทั้งหมด',
        'Graphics Cards (GPU)': 'การ์ดจอ (GPU)',
        'Processors (CPU)': 'ซีพียู (CPU)',
        'Laptops & Notebooks': 'โน้ตบุ๊ก & แล็ปท็อป',
        'Memory (RAM)': 'แรม (RAM)',
        'Storage (SSD & HDD)': 'ที่เก็บข้อมูล (SSD & HDD)',
        'Monitors & Displays': 'จอมอนิเตอร์ & หน้าจอ',
        'Motherboards': 'เมนบอร์ด (Mainboard)',
        'Power Supplies (PSU)': 'พาวเวอร์ซัพพลาย (PSU)',
        'PC Cases & Cooling': 'เคส & ชุดระบายความร้อน',
        'Gaming Peripherals': 'เกมมิ่งเกียร์ & อุปกรณ์เสริม',

        // Secondary Filters
        filter_store_label: 'ร้านค้า:',
        filter_all_stores: 'ทุกร้านค้าไทย',
        filter_max_price_label: 'ราคาสูงสุด (฿):',
        filter_max_price_placeholder: 'ไม่จำกัด ฿',
        filter_brand_label: 'แบรนด์:',
        filter_all_brands: 'ทุกแบรนด์',
        sort_label: 'เรียงตาม:',
        sort_cheapest: 'ราคาถูกที่สุดก่อน',
        sort_discount: 'ลดราคาสูงสุด %',
        sort_expensive: 'ราคาสูงสุดก่อน',
        sort_name: 'ชื่อสินค้า (A-Z)',
        sort_newest: 'สินค้ามาใหม่',
        showing_items: 'แสดงสินค้า {count} รายการ',
        loading_items: 'กำลังโหลดรายการสินค้า...',
        failed_load_products: 'ไม่สามารถโหลดข้อมูลสินค้าได้',
        no_items_found: 'ไม่พบสินค้าอุปกรณ์ไอที',
        no_items_desc: 'ลองปรับคำค้นหาหรือตัวกรองใหม่อีกครั้ง',
        reset_filters: 'ล้างตัวกรองทั้งหมด',

        // Product Cards
        card_lowest_price: 'ราคาต่ำสุดในไทย',
        card_msrp: 'ราคาเปิดตัว',
        card_save: 'ประหยัด',
        card_official_price: 'ราคาปกติ',
        card_compare_btn: 'เปรียบเทียบราคา',
        card_add_compare: 'เพิ่มลงตารางเปรียบเทียบ',
        card_thai_stores: 'ร้านค้า',

        // Comparison Modal
        modal_title: 'ตารางเปรียบเทียบราคาร้านค้าไทย',
        modal_sorted: 'เรียงจากราคาถูกที่สุดไปแพงที่สุด',
        modal_th_store: 'ร้านค้า',
        modal_th_stock: 'สถานะสต็อก',
        modal_th_price: 'ราคา',
        modal_th_shipping: 'ค่าจัดส่ง',
        modal_th_total: 'ราคารวม & ส่วนต่าง',
        modal_th_action: 'สั่งซื้อ',
        modal_best_deal: 'ราคาดีที่สุด:',
        modal_save_up_to: 'ประหยัดได้สูงสุด',
        modal_history_title: 'กราฟแนวโน้มราคา 30 วัน',
        modal_days_7: '7 วัน',
        modal_days_14: '14 วัน',
        modal_days_30: '30 วัน',
        modal_days_90: '90 วัน',
        modal_hist_lowest: 'ต่ำสุดตลอดกาล',
        modal_hist_highest: 'สูงสุดตลอดกาล',
        modal_hist_current: 'ต่ำสุดปัจจุบัน',
        modal_specs_title: 'สเปกอุปกรณ์หลัก',
        modal_no_specs: 'ไม่มีข้อมูลสเปกเพิ่มเติม',
        cheapest_badge: 'ราคาถูกที่สุด',
        low_stock: 'สินค้าใกล้หมด',
        modal_alert_title: 'ตั้งการแจ้งเตือนเมื่อราคาลด',
        modal_alert_desc: 'ระบบติดตาม JIB, iHaveCPU, BaNANA และ Advice ตลอดเวลา รับการแจ้งเตือนทันทีเมื่อราคาต่ำกว่าเป้าหมายของคุณ',
        modal_alert_email_placeholder: 'กรอกอีเมลของคุณ (ไม่จำเป็นหากเข้าสู่ระบบแล้ว)',
        modal_alert_price_placeholder: 'ราคาเป้าหมาย ฿',
        modal_alert_btn: 'ติดตามราคานี้',
        modal_warranty_guarantee: 'รับประกันศูนย์บริการไทยแท้ทุกชิ้น',
        modal_close: 'ปิด',
        free_shipping: 'ส่งฟรี',
        in_stock: 'มีสินค้า',
        out_of_stock: 'สินค้าหมด',
        buy_on: 'ซื้อที่',

        // Notifications
        notif_header: 'การแจ้งเตือนราคาลด',
        notif_mark_read: 'อ่านทั้งหมดแล้ว',
        notif_manage_watchlist: 'จัดการรายการติดตามทั้งหมด',

        // Footer
        footer_title: 'TechPrice ประเทศไทย',
        footer_desc: 'ระบบรวบรวมและเปรียบเทียบราคาไอที JIB, iHaveCPU, BaNANA, Advice',
        footer_export: 'ส่งออกไฟล์ CSV',
        footer_json: 'JSON API',
        footer_openapi: 'เอกสาร OpenAPI',
        footer_copyright: '© 2026 แพลตฟอร์ม TechPrice'
    },
    en: {
        // Navigation
        nav_catalog: 'Catalog & Prices',
        nav_compare: 'Head-to-Head',
        nav_deals: 'Hot Deals',
        nav_watchlist: 'Watchlist',
        nav_scrapers: 'Scrapers',
        nav_api: 'REST API',
        btn_refresh_prices: 'Refresh Prices',
        sign_in: 'Sign In',
        create_account: 'Create Account',
        admin_portal: 'Admin Portal',
        sign_out: 'Sign Out',
        my_watchlist: 'My Watchlist',
        demo_login: 'Demo Account Sign In',

        // Mobile Nav
        mobile_catalog: 'Catalog & Prices',
        mobile_compare: 'Head-to-Head Compare',
        mobile_deals: 'Hot Deals & Flash Sales',
        mobile_watchlist: 'My Watchlist & Alerts',
        mobile_scrapers: 'Thai Scrapers (JIB, iHaveCPU, BaNANA, Advice)',
        mobile_api: 'REST API Explorer',
        mobile_docs: 'Swagger API Docs',

        // Hero Section
        hero_badge: 'Thailand IT Hardware Price Intelligence & Alerts',
        hero_title_prefix: 'Compare',
        hero_title_gradient: 'IT Equipment Prices',
        hero_title_suffix: 'Across Thai Stores',
        hero_desc: 'Real-time price collector and side-by-side comparison engine for GPUs, CPUs, Laptops, SSDs, and Monitors across JIB, iHaveCPU, BaNANA IT, and Advice.',
        search_placeholder: 'Search GPUs (RTX 5090, 5080, 4070), CPUs (9800X3D), Laptops, SSDs...',
        search_btn: 'Search',

        // Stats Row
        stat_hardware: 'Hardware Tracked',
        stat_stores: 'Thai Stores',
        stat_stores_desc: 'JIB, iHaveCPU, BaNANA, Advice',
        stat_listings: 'Live Price Listings',
        stat_listings_desc: 'Real-time updated quotes',
        stat_alerts: 'Alerts System',
        stat_alerts_desc: 'Price Drop Notifications',

        // Categories
        cat_all: 'All Hardware',
        'Graphics Cards (GPU)': 'Graphics Cards (GPU)',
        'Processors (CPU)': 'Processors (CPU)',
        'Laptops & Notebooks': 'Laptops & Notebooks',
        'Memory (RAM)': 'Memory (RAM)',
        'Storage (SSD & HDD)': 'Storage (SSD & HDD)',
        'Monitors & Displays': 'Monitors & Displays',
        'Motherboards': 'Motherboards',
        'Power Supplies (PSU)': 'Power Supplies (PSU)',
        'PC Cases & Cooling': 'PC Cases & Cooling',
        'Gaming Peripherals': 'Gaming Peripherals',

        // Secondary Filters
        filter_store_label: 'Store:',
        filter_all_stores: 'All Thai Stores',
        filter_max_price_label: 'Max Price (฿):',
        filter_max_price_placeholder: 'Any ฿',
        filter_brand_label: 'Brand:',
        filter_all_brands: 'All Brands',
        sort_label: 'Sort By:',
        sort_cheapest: 'Lowest Price First',
        sort_discount: 'Biggest Discount %',
        sort_expensive: 'Highest Price First',
        sort_name: 'Product Name (A-Z)',
        sort_newest: 'Newest Added',
        showing_items: 'Showing {count} IT items',
        loading_items: 'Loading products...',
        failed_load_products: 'Failed to load IT products.',
        no_items_found: 'No IT Equipment Found',
        no_items_desc: 'Try adjusting your search terms or filters.',
        reset_filters: 'Reset All Filters',

        // Product Cards
        card_lowest_price: 'Lowest Thai Market Price',
        card_msrp: 'Official MSRP',
        card_save: 'Save',
        card_official_price: 'Official Price',
        card_compare_btn: 'Compare Prices',
        card_add_compare: 'Add to Head-to-Head Compare',
        card_thai_stores: 'Thai Stores',

        // Comparison Modal
        modal_title: 'Thai Retailer Price Comparison',
        modal_sorted: 'Sorted from lowest to highest',
        modal_th_store: 'Platform Store',
        modal_th_stock: 'Stock Status',
        modal_th_price: 'Price',
        modal_th_shipping: 'Shipping',
        modal_th_total: 'Total & Diff',
        modal_th_action: 'Action',
        modal_best_deal: 'Best Deal:',
        modal_save_up_to: 'Save up to',
        modal_history_title: '30-Day Store Price Trend',
        modal_days_7: '7 Days',
        modal_days_14: '14 Days',
        modal_days_30: '30 Days',
        modal_days_90: '90 Days',
        modal_hist_lowest: 'All-Time Lowest',
        modal_hist_highest: 'All-Time Highest',
        modal_hist_current: 'Current Lowest',
        modal_specs_title: 'Key Hardware Specifications',
        modal_no_specs: 'No detailed specs available.',
        cheapest_badge: 'CHEAPEST',
        low_stock: 'Low Stock',
        modal_alert_title: 'Set Instant Price Drop Alert',
        modal_alert_desc: 'We continuously monitor JIB, iHaveCPU, BaNANA, and Advice. Receive an instant alert when price drops below your target.',
        modal_alert_email_placeholder: 'Enter your email (optional if logged in)',
        modal_alert_price_placeholder: 'Target ฿',
        modal_alert_btn: 'Track Target',
        modal_warranty_guarantee: 'Thai official retailer warranties guaranteed',
        modal_close: 'Close',
        free_shipping: 'Free',
        in_stock: 'In Stock',
        out_of_stock: 'Out of Stock',
        buy_on: 'Buy on',

        // Notifications
        notif_header: 'Price Drop Alerts',
        notif_mark_read: 'Mark All Read',
        notif_manage_watchlist: 'Manage All Alerts & Watchlist',

        // Footer
        footer_title: 'TechPrice Thailand',
        footer_desc: 'JIB, iHaveCPU, BaNANA, Advice IT Aggregator',
        footer_export: 'Export CSV',
        footer_json: 'JSON API',
        footer_openapi: 'OpenAPI Spec',
        footer_copyright: '© 2026 TechPrice Platform'
    }
};

let currentLanguage = localStorage.getItem('techprice_lang') || 'th';

function getLanguage() {
    return currentLanguage;
}

function t(key, params = {}) {
    const dict = TRANSLATIONS[currentLanguage] || TRANSLATIONS.th;
    let text = dict[key] || TRANSLATIONS.en[key] || key;
    for (const [k, v] of Object.entries(params)) {
        text = text.replace(new RegExp('\\{' + k + '\\}', 'g'), v);
    }
    return text;
}

function setLanguage(lang) {
    if (lang !== 'th' && lang !== 'en') lang = 'th';
    currentLanguage = lang;
    localStorage.setItem('techprice_lang', lang);
    document.documentElement.lang = lang;

    updateLanguageButtons();
    applyStaticTranslations();

    if (typeof window.onLanguageChanged === 'function') {
        window.onLanguageChanged(lang);
    }
}

function updateLanguageButtons() {
    const btnTh = document.getElementById('lang-btn-th');
    const btnEn = document.getElementById('lang-btn-en');

    if (btnTh && btnEn) {
        if (currentLanguage === 'th') {
            btnTh.className = 'px-2 py-1 rounded-md transition-all text-white bg-cyan-600 shadow-sm flex items-center gap-1 font-bold text-xs';
            btnEn.className = 'px-2 py-1 rounded-md transition-all text-gray-400 hover:text-white flex items-center gap-1 font-medium text-xs';
        } else {
            btnTh.className = 'px-2 py-1 rounded-md transition-all text-gray-400 hover:text-white flex items-center gap-1 font-medium text-xs';
            btnEn.className = 'px-2 py-1 rounded-md transition-all text-white bg-cyan-600 shadow-sm flex items-center gap-1 font-bold text-xs';
        }
    }
}

function applyStaticTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (key && TRANSLATIONS[currentLanguage]?.[key]) {
            el.textContent = TRANSLATIONS[currentLanguage][key];
        }
    });

    document.querySelectorAll('[data-i18n-html]').forEach(el => {
        const key = el.getAttribute('data-i18n-html');
        if (key && TRANSLATIONS[currentLanguage]?.[key]) {
            el.innerHTML = TRANSLATIONS[currentLanguage][key];
        }
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (key && TRANSLATIONS[currentLanguage]?.[key]) {
            el.placeholder = TRANSLATIONS[currentLanguage][key];
        }
    });

    document.querySelectorAll('[data-category-name]').forEach(el => {
        const original = el.getAttribute('data-category-name');
        if (currentLanguage === 'th') {
            el.textContent = TRANSLATIONS.th[original] || original;
        } else {
            el.textContent = original;
        }
    });

    document.querySelectorAll('option[data-i18n]').forEach(opt => {
        const key = opt.getAttribute('data-i18n');
        if (key && TRANSLATIONS[currentLanguage]?.[key]) {
            opt.textContent = TRANSLATIONS[currentLanguage][key];
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    document.documentElement.lang = currentLanguage;
    updateLanguageButtons();
    applyStaticTranslations();
});
