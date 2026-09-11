import re
import urllib.parse
from typing import Optional

# Direct keyword mappings for verified hardware items to ensure exact match on Thai stores
PRODUCT_CLEAN_KEYWORDS = {
    # GPUs
    "nvidia-geforce-rtx-5090-32gb": "RTX 5090",
    "nvidia-geforce-rtx-5080-16gb": "RTX 5080",
    "amd-radeon-rx-7900-xtx-24gb": "RX 7900 XTX",
    "nvidia-geforce-rtx-4070-ti-super-16gb": "RTX 4070 Ti Super",
    "nvidia-geforce-rtx-4090-24gb": "RTX 4090",
    "nvidia-geforce-rtx-4080-super-16gb": "RTX 4080 Super",
    "nvidia-geforce-rtx-4070-super-12gb": "RTX 4070 Super",
    "nvidia-geforce-rtx-4060-ti-16gb": "RTX 4060 Ti",
    "amd-radeon-rx-7800-xt-16gb": "RX 7800 XT",
    "amd-radeon-rx-7700-xt-12gb": "RX 7700 XT",

    # CPUs
    "amd-ryzen-7-9800x3d": "Ryzen 7 9800X3D",
    "amd-ryzen-9-9950x": "Ryzen 9 9950X",
    "intel-core-ultra-9-285k": "Core Ultra 9 285K",
    "amd-ryzen-7-7800x3d": "Ryzen 7 7800X3D",
    "amd-ryzen-5-9600x": "Ryzen 5 9600X",
    "intel-core-i9-14900k": "Core i9-14900K",
    "intel-core-i7-14700k": "Core i7-14700K",
    "intel-core-i5-14600k": "Core i5-14600K",

    # Laptops
    "apple-macbook-pro-16-m4-max": "MacBook Pro 16 M4",
    "asus-rog-zephyrus-g16-oled": "ROG Zephyrus G16",
    "lenovo-legion-pro-7i-rtx4080": "Legion Pro 7",
    "acer-predator-helios-16-rtx4070": "Predator Helios 16",
    "apple-macbook-air-15-m3": "MacBook Air 15 M3",

    # Storage
    "samsung-990-pro-2tb-nvme-ssd": "Samsung 990 PRO",
    "crucial-t705-2tb-gen5-ssd": "Crucial T705",
    "wd-black-sn850x-2tb-nvme": "WD Black SN850X",
    "kingston-kc3000-2tb-nvme": "Kingston KC3000",

    # RAM
    "corsair-vengeance-rgb-ddr5-64gb-6000mhz": "Corsair Vengeance DDR5",
    "gskill-trident-z5-rgb-ddr5-32gb-6400": "Trident Z5",
    "kingston-fury-beast-rgb-ddr5-32gb-6000": "Kingston FURY Beast",

    # Monitors
    "lg-ultragear-32gs95ue-32-oled": "LG UltraGear 32GS95UE",
    "dell-alienware-aw3423dwf-34-curved-qd-oled": "Alienware AW3423DWF",
    "asus-rog-swift-oled-pg32ucdm": "ROG Swift OLED PG32UCDM",
    "samsung-odyssey-oled-g9-49": "Odyssey OLED G9",

    # Motherboards
    "asus-rog-maximus-z890-hero": "ROG MAXIMUS Z890 HERO",
    "msi-mag-b650-tomahawk-wifi": "MAG B650 TOMAHAWK WIFI",
    "gigabyte-x870-aorus-elite-wifi7": "X870 AORUS ELITE WIFI7",

    # Power & Cooling & Peripherals
    "corsair-rm1000x-shift-1000w-gold": "Corsair RM1000x",
    "nzxt-kraken-elite-360-rgb": "NZXT Kraken Elite 360",
    "lian-li-o11-dynamic-evo-rgb": "Lian Li O11 Dynamic EVO",
    "logitech-g-pro-x-superlight-2": "Logitech G PRO X SUPERLIGHT 2",
    "razer-viper-v3-pro-wireless": "Razer Viper V3 Pro",
    "wooting-60he-plus-analog-keyboard": "Wooting 60HE"
}

def clean_search_keyword(
    product_name: str, 
    brand: str = "", 
    model_no: str = "",
    product_slug: str = ""
) -> str:
    # 1. Direct slug lookup
    if product_slug and product_slug in PRODUCT_CLEAN_KEYWORDS:
        return PRODUCT_CLEAN_KEYWORDS[product_slug]
        
    p_lower = (product_name or "").lower()
    
    # 2. Known clean keyword match within product name (longest match first)
    for s_key, clean_val in sorted(PRODUCT_CLEAN_KEYWORDS.items(), key=lambda x: len(x[1]), reverse=True):
        if clean_val.lower() in p_lower:
            return clean_val
            
    # 3. Dynamic generic cleaning
    s = product_name or ""
    # Remove bracketed contents: (2x16GB), (GPU), [White], etc.
    s = re.sub(r'\([^)]*\)', ' ', s)
    s = re.sub(r'\[[^\]]*\]', ' ', s)
    # Remove quotes, slashes, and noisy punctuation
    s = re.sub(r'["\'`“”‘’/\\|]', ' ', s)
    
    # Remove marketing prefixes & filler terms that break store searches
    noise = [
        r'\bNVIDIA\s+GeForce\b', r'\bAMD\s+Radeon\b',
        r'\bDesktop Processor\b', r'\bGaming Processor\b', r'\bGaming Monitor\b',
        r'\bGaming Desktop\b', r'\bDesktop PC\b', r'\bPower Supply Unit\b',
        r'\bAll-in-One Liquid Cooler\b', r'\bLiquid Cooler\b', r'\bAIO Cooler\b',
        r'\bPCIe\s*[0-9.]+\s*(?:NVMe)?\s*(?:M\.2)?\s*SSD\b',
        r'\bNVMe\s*M\.2\s*SSD\b', r'\bNVMe\s*SSD\b', r'\bM\.2\s*SSD\b',
        r'\bGDDR7\b', r'\bGDDR6X\b', r'\bGDDR6\b', r'\bGDDR5\b',
        r'\b[0-9]+-Core\b', r'\b[0-9]+-Thread\b',
        r'\bFlagship Blackwell\b', r'\bRDNA 3\b', r'\bRDNA 2\b',
        r'\bAM5 Processor\b', r'\bLGA1700 Processor\b', r'\bLGA1851 Processor\b',
        r'\bProcessor\b', r'\bMotherboard\b',
        r'\bGaming Graphics Card\b', r'\bGraphics Card\b',
        r'\bWireless Gaming Mouse\b', r'\bUltra-Lightweight Wireless Mouse\b',
        r'\bRapid Trigger Analog Keyboard\b'
    ]
    for pattern in noise:
        s = re.sub(pattern, ' ', s, flags=re.I)
    
    s = re.sub(r'\s+', ' ', s).strip()
    if len(s) < 3 and model_no:
        s = f"{brand} {model_no}".strip()
    elif len(s) < 3:
        s = product_name.strip()
    return s

def is_direct_product_url(url: Optional[str], store_slug: str = "") -> bool:
    if not url:
        return False
    u = url.strip()
    s = (store_slug or "").lower().strip()
    
    # JIB direct product page
    if "/web/product/readProduct/" in u:
        return True
        
    # iHaveCPU direct product page (not search results)
    if "ihavecpu.com/product/" in u and "/product/search" not in u:
        return True
        
    # BaNANA IT direct product page (not search /th/p?q=)
    if "bnn.in.th/th/p/" in u and "?q=" not in u and "shop-by-brand" not in u and not u.endswith("/th/p/"):
        return True
        
    # Advice direct product page (not /product/search)
    if "advice.co.th/product/" in u and "/product/search" not in u and "/product/compare" not in u:
        return True
        
    return False

def generate_store_product_url(
    store_slug: str, 
    product_name: str, 
    brand: str = "", 
    model_no: Optional[str] = "", 
    existing_url: Optional[str] = None,
    product_slug: Optional[str] = None
) -> str:
    slug = (store_slug or "").lower().strip()
    raw_model = (model_no or "").strip()
    
    # If existing URL is already a direct single product page, ALWAYS preserve it
    if existing_url and is_direct_product_url(existing_url, slug):
        return existing_url
        
    clean_kw = clean_search_keyword(product_name, brand, raw_model, product_slug=product_slug or "")
    if slug == "jib":
        if raw_model.isdigit() and len(raw_model) >= 5:
            return f"https://www.jib.co.th/web/product/readProduct/{raw_model}"
        encoded_q = urllib.parse.quote_plus(clean_kw)
        return f"https://www.jib.co.th/web/product/product_search/0?str_search={encoded_q}"
    elif slug == "ihavecpu":
        # iHaveCPU path routing uses %20 for spaces (literal '+' fails to match)
        encoded_path = urllib.parse.quote(clean_kw)
        return f"https://ihavecpu.com/product/search/{encoded_path}"
    elif slug == "banana":
        encoded_q = urllib.parse.quote_plus(clean_kw)
        return f"https://www.bnn.in.th/th/p?q={encoded_q}"
    elif slug == "advice":
        encoded_q = urllib.parse.quote_plus(clean_kw)
        return f"https://www.advice.co.th/product/search?keyword={encoded_q}"
    else:
        encoded_q = urllib.parse.quote_plus(f"{slug} {clean_kw}")
        return f"https://www.google.com/search?q={encoded_q}"

