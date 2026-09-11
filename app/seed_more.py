import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from app.config import settings
from app.models.product import Product
from app.models.store import Store
from app.models.price_listing import PriceListing
from app.models.price_history import PriceHistory
from app.utils.store_urls import generate_store_product_url

MORE_PRODUCTS = [
    # --- Additional GPUs ---
    {
        "name": "NVIDIA GeForce RTX 4090 24GB GDDR6X",
        "slug": "nvidia-geforce-rtx-4090-24gb",
        "category": "Graphics Cards (GPU)",
        "brand": "NVIDIA",
        "model_no": "RTX-4090-24G",
        "image_url": "https://images.unsplash.com/photo-1591488320449-011701bb6704?auto=format&fit=crop&w=600&q=80",
        "description": "Ultra-enthusiast Ada Lovelace GPU with 24GB GDDR6X, 16384 CUDA cores, 384-bit bus, and DLSS 3.5 support.",
        "msrp": 67900.0,
        "specs": {
            "vram": "24GB GDDR6X",
            "bus_width": "384-bit",
            "cuda_cores": "16,384",
            "boost_clock": "2.52 GHz",
            "tdp": "450W",
            "interface": "PCIe 4.0 x16",
            "warranty": "3 Years Official Thailand"
        }
    },
    {
        "name": "NVIDIA GeForce RTX 4080 Super 16GB GDDR6X",
        "slug": "nvidia-geforce-rtx-4080-super-16gb",
        "category": "Graphics Cards (GPU)",
        "brand": "NVIDIA",
        "model_no": "RTX-4080S-16G",
        "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=1200&q=85",
        "description": "High-end 4K gaming powerhouse with 10,240 CUDA cores, 16GB GDDR6X, and supercharged ray tracing cores.",
        "msrp": 38900.0,
        "specs": {
            "vram": "16GB GDDR6X",
            "bus_width": "256-bit",
            "cuda_cores": "10,240",
            "boost_clock": "2.55 GHz",
            "tdp": "320W",
            "interface": "PCIe 4.0 x16",
            "warranty": "3 Years Official Thailand"
        }
    },
    {
        "name": "NVIDIA GeForce RTX 4070 Super 12GB GDDR6X",
        "slug": "nvidia-geforce-rtx-4070-super-12gb",
        "category": "Graphics Cards (GPU)",
        "brand": "NVIDIA",
        "model_no": "RTX-4070S-12G",
        "image_url": "https://images.unsplash.com/photo-1591488320449-011701bb6704?auto=format&fit=crop&w=1200&q=85",
        "description": "Sweet-spot 1440p high refresh GPU with 7168 CUDA cores, 12GB GDDR6X, and DLSS 3 frame generation.",
        "msrp": 23900.0,
        "specs": {
            "vram": "12GB GDDR6X",
            "bus_width": "192-bit",
            "cuda_cores": "7,168",
            "boost_clock": "2.48 GHz",
            "tdp": "220W",
            "interface": "PCIe 4.0 x16",
            "warranty": "3 Years Official Thailand"
        }
    },
    {
        "name": "NVIDIA GeForce RTX 4060 Ti 16GB GDDR6",
        "slug": "nvidia-geforce-rtx-4060-ti-16gb",
        "category": "Graphics Cards (GPU)",
        "brand": "NVIDIA",
        "model_no": "RTX-4060TI-16G",
        "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=1200&q=85",
        "description": "High VRAM 1080p/1440p gaming and AI generation GPU with 16GB GDDR6 and low 165W power consumption.",
        "msrp": 17900.0,
        "specs": {
            "vram": "16GB GDDR6",
            "bus_width": "128-bit",
            "cuda_cores": "4,352",
            "boost_clock": "2.54 GHz",
            "tdp": "165W",
            "interface": "PCIe 4.0 x8",
            "warranty": "3 Years Official Thailand"
        }
    },
    {
        "name": "AMD Radeon RX 7800 XT 16GB GDDR6",
        "slug": "amd-radeon-rx-7800-xt-16gb",
        "category": "Graphics Cards (GPU)",
        "brand": "AMD",
        "model_no": "RX-7800XT-16G",
        "image_url": "https://images.unsplash.com/photo-1591488320449-011701bb6704?auto=format&fit=crop&w=1200&q=85",
        "description": "RDNA 3 gaming champion with 16GB VRAM, 256-bit bus width, 64MB Infinity Cache, and AMD HYPR-RX.",
        "msrp": 19500.0,
        "specs": {
            "vram": "16GB GDDR6",
            "bus_width": "256-bit",
            "compute_units": "60",
            "boost_clock": "2.43 GHz",
            "tdp": "263W",
            "interface": "PCIe 4.0 x16",
            "warranty": "3 Years Official Thailand"
        }
    },
    {
        "name": "AMD Radeon RX 7700 XT 12GB GDDR6",
        "slug": "amd-radeon-rx-7700-xt-12gb",
        "category": "Graphics Cards (GPU)",
        "brand": "AMD",
        "model_no": "RX-7700XT-12G",
        "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=1200&q=85",
        "description": "1440p gaming graphics card with 12GB GDDR6, 54 Compute Units, and DisplayPort 2.1 support.",
        "msrp": 15900.0,
        "specs": {
            "vram": "12GB GDDR6",
            "bus_width": "192-bit",
            "compute_units": "54",
            "boost_clock": "2.54 GHz",
            "tdp": "245W",
            "interface": "PCIe 4.0 x16",
            "warranty": "3 Years Official Thailand"
        }
    },

    # --- Additional CPUs ---
    {
        "name": "AMD Ryzen 7 7800X3D 8-Core Gaming Processor",
        "slug": "amd-ryzen-7-7800x3d",
        "category": "Processors (CPU)",
        "brand": "AMD",
        "model_no": "100-100000910WOF",
        "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?auto=format&fit=crop&w=1200&q=85",
        "description": "Legendary gaming CPU with 96MB of 3D V-Cache, 8 cores, 16 threads, and incredible power efficiency.",
        "msrp": 14900.0,
        "specs": {
            "cores_threads": "8 Cores / 16 Threads",
            "base_clock": "4.2 GHz",
            "boost_clock": "5.0 GHz",
            "cache": "104MB (96MB L3 3D V-Cache)",
            "socket": "AM5",
            "tdp": "120W",
            "warranty": "3 Years (Synnex / Ingram)"
        }
    },
    {
        "name": "AMD Ryzen 5 9600X 6-Core 12-Thread Processor",
        "slug": "amd-ryzen-5-9600x",
        "category": "Processors (CPU)",
        "brand": "AMD",
        "model_no": "100-100001405WOF",
        "image_url": "https://images.unsplash.com/photo-1555680202-c86f0e12f086?auto=format&fit=crop&w=1200&q=85",
        "description": "Zen 5 desktop CPU offering high single-core gaming performance, 5.4GHz boost, and low 65W TDP.",
        "msrp": 10900.0,
        "specs": {
            "cores_threads": "6 Cores / 12 Threads",
            "base_clock": "3.9 GHz",
            "boost_clock": "5.4 GHz",
            "cache": "38MB Total (32MB L3)",
            "socket": "AM5",
            "tdp": "65W",
            "warranty": "3 Years (Synnex / Ingram)"
        }
    },
    {
        "name": "Intel Core i9-14900K 24-Core 32-Thread Processor",
        "slug": "intel-core-i9-14900k",
        "category": "Processors (CPU)",
        "brand": "Intel",
        "model_no": "BX8071514900K",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=85",
        "description": "Raptor Lake Refresh flagship capable of up to 6.0 GHz Intel Thermal Velocity Boost, 8P+16E cores.",
        "msrp": 21900.0,
        "specs": {
            "cores_threads": "24 Cores (8P + 16E) / 32 Threads",
            "base_clock": "3.2 GHz",
            "boost_clock": "6.0 GHz",
            "cache": "36MB Intel Smart Cache",
            "socket": "LGA 1700",
            "tdp": "125W Base / 253W Turbo",
            "warranty": "3 Years (Synnex / WPG)"
        }
    },
    {
        "name": "Intel Core i7-14700K 20-Core 28-Thread Processor",
        "slug": "intel-core-i7-14700k",
        "category": "Processors (CPU)",
        "brand": "Intel",
        "model_no": "BX8071514700K",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=85",
        "description": "20 cores (8P + 12E), 5.6 GHz max turbo frequency, perfect for demanding gamers and streamers.",
        "msrp": 15900.0,
        "specs": {
            "cores_threads": "20 Cores (8P + 12E) / 28 Threads",
            "base_clock": "3.4 GHz",
            "boost_clock": "5.6 GHz",
            "cache": "33MB Intel Smart Cache",
            "socket": "LGA 1700",
            "tdp": "125W Base / 253W Turbo",
            "warranty": "3 Years (Synnex / WPG)"
        }
    },
    {
        "name": "Intel Core i5-14600K 14-Core 20-Thread Processor",
        "slug": "intel-core-i5-14600k",
        "category": "Processors (CPU)",
        "brand": "Intel",
        "model_no": "BX8071514600K",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=85",
        "description": "The best value mid-range processor with 14 cores (6P + 8E), 5.3 GHz boost, and DDR5/DDR4 support.",
        "msrp": 11500.0,
        "specs": {
            "cores_threads": "14 Cores (6P + 8E) / 20 Threads",
            "base_clock": "3.5 GHz",
            "boost_clock": "5.3 GHz",
            "cache": "24MB Intel Smart Cache",
            "socket": "LGA 1700",
            "tdp": "125W Base / 181W Turbo",
            "warranty": "3 Years (Synnex / WPG)"
        }
    },

    # --- Additional Motherboards ---
    {
        "name": "ASUS ROG MAXIMUS Z890 HERO WiFi 7 Motherboard",
        "slug": "asus-rog-maximus-z890-hero",
        "category": "Motherboards",
        "brand": "ASUS",
        "model_no": "ROG-Z890-HERO",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=85",
        "description": "Flagship Intel LGA 1851 motherboard with 22+1+2+2 power stages, DDR5 NitroPath, Thunderbolt 4, and WiFi 7.",
        "msrp": 26900.0,
        "specs": {
            "socket": "LGA 1851 (Intel Core Ultra Series 2)",
            "chipset": "Intel Z890",
            "memory": "4x DDR5 DIMM (up to 9200+ MT/s OC, 192GB)",
            "expansion": "1x PCIe 5.0 x16, 1x PCIe 4.0 x16",
            "networking": "Intel 2.5G LAN, Realtek 5G LAN, WiFi 7",
            "storage": "3x PCIe 5.0 M.2 + 3x PCIe 4.0 M.2",
            "warranty": "3+1 Years ASUS Thailand"
        }
    },
    {
        "name": "MSI MAG B650 TOMAHAWK WIFI AM5 Motherboard",
        "slug": "msi-mag-b650-tomahawk-wifi",
        "category": "Motherboards",
        "brand": "MSI",
        "model_no": "MAG-B650-TOMAHAWK-WIFI",
        "image_url": "https://images.unsplash.com/photo-1555680202-c86f0e12f086?auto=format&fit=crop&w=1200&q=85",
        "description": "Extremely popular AMD AM5 gaming motherboard with robust 14+2+1 Duet Rail VRM and dual PCIe 4.0 M.2.",
        "msrp": 7990.0,
        "specs": {
            "socket": "AM5 (AMD Ryzen 7000 / 8000 / 9000)",
            "chipset": "AMD B650",
            "memory": "4x DDR5 DIMM (up to 7600+ MHz OC)",
            "storage": "3x M.2 PCIe 4.0 x4",
            "networking": "Realtek 2.5G LAN + Wi-Fi 6E",
            "form_factor": "ATX",
            "warranty": "3 Years MSI Thailand"
        }
    },
    {
        "name": "GIGABYTE X870 AORUS ELITE WIFI7 AM5 Motherboard",
        "slug": "gigabyte-x870-aorus-elite-wifi7",
        "category": "Motherboards",
        "brand": "GIGABYTE",
        "model_no": "X870-AORUS-ELITE-WIFI7",
        "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=1200&q=85",
        "description": "Next-gen AMD AM5 motherboard featuring native USB4 40Gbps, PCIe 5.0 GPU & M.2, and Wi-Fi 7 with EZ-Latch.",
        "msrp": 11900.0,
        "specs": {
            "socket": "AM5 (AMD Ryzen 9000 Ready)",
            "chipset": "AMD X870",
            "memory": "4x DDR5 DIMM (up to 8000 MT/s EXPO)",
            "usb": "Dual USB4 40Gbps Type-C",
            "storage": "3x PCIe 5.0 M.2 + 1x PCIe 4.0 M.2",
            "networking": "Realtek 2.5G LAN + Wi-Fi 7",
            "warranty": "3 Years Synnex Thailand"
        }
    },

    # --- Additional Laptops ---
    {
        "name": "Lenovo Legion Pro 7i 16\" (i9-14900HX, RTX 4080, 32GB RAM)",
        "slug": "lenovo-legion-pro-7i-rtx4080",
        "category": "Laptops & Notebooks",
        "brand": "Lenovo",
        "model_no": "16IRX9H",
        "image_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=1200&q=85",
        "description": "Elite gaming laptop with 16\" WQXGA 240Hz 500 nits display, 175W TGP RTX 4080, and Coldfront Vapor Chamber.",
        "msrp": 89900.0,
        "specs": {
            "display": "16\" 2560x1600 IPS 240Hz (100% DCI-P3, G-SYNC)",
            "processor": "Intel Core i9-14900HX (24 Cores / 32 Threads)",
            "graphics": "NVIDIA GeForce RTX 4080 12GB (175W TGP)",
            "ram": "32GB DDR5-5600MHz",
            "storage": "1TB PCIe 4.0 NVMe SSD",
            "weight": "2.62 kg",
            "warranty": "3 Years Legion Ultimate Support (Onsite)"
        }
    },
    {
        "name": "Acer Predator Helios 16 (i7-14700HX, RTX 4070, 16GB RAM)",
        "slug": "acer-predator-helios-16-rtx4070",
        "category": "Laptops & Notebooks",
        "brand": "Acer",
        "model_no": "PH16-72-747X",
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=1200&q=85",
        "description": "High refresh 16\" WQXGA 240Hz screen, 5th Gen AeroBlade 3D fans, and full-power RTX 4070 140W GPU.",
        "msrp": 59900.0,
        "specs": {
            "display": "16\" WQXGA (2560x1600) 240Hz IPS",
            "processor": "Intel Core i7-14700HX (20 Cores)",
            "graphics": "NVIDIA GeForce RTX 4070 8GB GDDR6 (140W)",
            "ram": "16GB DDR5 5600MHz (expandable to 64GB)",
            "storage": "1TB PCIe Gen4 NVMe SSD",
            "warranty": "3 Years Onsite Service Acer Thailand"
        }
    },
    {
        "name": "Apple MacBook Air 15\" M3 (16GB RAM, 512GB SSD)",
        "slug": "apple-macbook-air-15-m3",
        "category": "Laptops & Notebooks",
        "brand": "Apple",
        "model_no": "MXD13TH/A",
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=85",
        "description": "Ultra-thin 11.5mm aluminum chassis, 15.3\" Liquid Retina display, silent fanless M3 chip, and 18-hour battery.",
        "msrp": 54900.0,
        "specs": {
            "display": "15.3\" Liquid Retina (2880x1864, 500 nits, True Tone)",
            "processor": "Apple M3 (8-Core CPU, 10-Core GPU)",
            "ram": "16GB Unified Memory",
            "storage": "512GB High-speed SSD",
            "weight": "1.51 kg",
            "warranty": "1 Year AppleCare (Extendable)"
        }
    },

    # --- Additional Storage (SSD) ---
    {
        "name": "Western Digital WD_BLACK SN850X 2TB NVMe M.2 SSD",
        "slug": "wd-black-sn850x-2tb-nvme",
        "category": "Storage (SSD & HDD)",
        "brand": "Western Digital",
        "model_no": "WDS200T2X0E",
        "image_url": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?auto=format&fit=crop&w=1200&q=85",
        "description": "Blistering PCIe Gen4 speeds up to 7,300 MB/s read, Game Mode 2.0, optimized for PC and PS5 storage.",
        "msrp": 6290.0,
        "specs": {
            "capacity": "2TB",
            "interface": "PCIe Gen4 x4, NVMe 1.4",
            "seq_read": "7,300 MB/s",
            "seq_write": "6,600 MB/s",
            "endurance": "1,200 TBW",
            "form_factor": "M.2 2280",
            "warranty": "5 Years Synnex Thailand"
        }
    },
    {
        "name": "Kingston KC3000 2TB PCIe 4.0 NVMe M.2 SSD",
        "slug": "kingston-kc3000-2tb-nvme",
        "category": "Storage (SSD & HDD)",
        "brand": "Kingston",
        "model_no": "SKC3000D/2048G",
        "image_url": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?auto=format&fit=crop&w=1200&q=85",
        "description": "Phison E18 controller, graphene aluminum heat spreader, 7000MB/s speeds, and premium 1600 TBW endurance.",
        "msrp": 5490.0,
        "specs": {
            "capacity": "2TB",
            "interface": "PCIe 4.0 x4 NVMe",
            "seq_read": "7,000 MB/s",
            "seq_write": "7,000 MB/s",
            "endurance": "1,600 TBW",
            "form_factor": "M.2 2280",
            "warranty": "5 Years Synnex Thailand"
        }
    },

    # --- Additional RAM ---
    {
        "name": "G.SKILL Trident Z5 RGB DDR5 32GB (2x16GB) 6400MHz CL32",
        "slug": "gskill-trident-z5-rgb-ddr5-32gb-6400",
        "category": "Memory (RAM)",
        "brand": "G.SKILL",
        "model_no": "F5-6400J3239G16GX2-TZ5RK",
        "image_url": "https://images.unsplash.com/photo-1562976540-1502c2145186?auto=format&fit=crop&w=1200&q=85",
        "description": "Hyper-speed DDR5 memory module with sleek brushed-aluminum heatspreader and smooth RGB light bar.",
        "msrp": 4890.0,
        "specs": {
            "capacity": "32GB (2 x 16GB)",
            "speed": "DDR5-6400 MHz",
            "timing": "CL32-39-39-102",
            "voltage": "1.40V",
            "profile": "Intel XMP 3.0",
            "warranty": "Lifetime Warranty (Synnex)"
        }
    },
    {
        "name": "Kingston FURY Beast RGB DDR5 32GB (2x16GB) 6000MHz CL30",
        "slug": "kingston-fury-beast-rgb-ddr5-32gb-6000",
        "category": "Memory (RAM)",
        "brand": "Kingston",
        "model_no": "KF560C30BBEAK2-32",
        "image_url": "https://images.unsplash.com/photo-1562976540-1502c2145186?auto=format&fit=crop&w=1200&q=85",
        "description": "AMD EXPO certified DDR5 memory kit with tight CL30 timings for maximum Ryzen 7000/9000 gaming FPS.",
        "msrp": 4290.0,
        "specs": {
            "capacity": "32GB (2 x 16GB)",
            "speed": "DDR5-6000 MHz",
            "timing": "CL30-36-36",
            "profile": "AMD EXPO & Intel XMP 3.0",
            "warranty": "Lifetime Warranty (Synnex / Ingram)"
        }
    },

    # --- Additional Monitors ---
    {
        "name": "ASUS ROG Swift OLED PG32UCDM 32\" 4K 240Hz Gaming Monitor",
        "slug": "asus-rog-swift-oled-pg32ucdm",
        "category": "Monitors & Displays",
        "brand": "ASUS",
        "model_no": "PG32UCDM",
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=1200&q=85",
        "description": "Third-generation 4K QD-OLED panel, 240Hz refresh, 0.03ms response, graphene film heatsink, and USB-C 90W PD.",
        "msrp": 46900.0,
        "specs": {
            "panel": "31.5\" QD-OLED (3840x2160)",
            "refresh_rate": "240Hz",
            "response_time": "0.03ms (GTG)",
            "brightness": "1000 nits (Peak HDR)",
            "ports": "2x HDMI 2.1, 1x DP 1.4 DSC, 1x USB-C 90W",
            "warranty": "3 Years Burn-in Warranty ASUS"
        }
    },
    {
        "name": "Samsung Odyssey OLED G9 49\" Curved 240Hz 0.03ms",
        "slug": "samsung-odyssey-oled-g9-49",
        "category": "Monitors & Displays",
        "brand": "Samsung",
        "model_no": "LS49CG954SEXXT",
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=1200&q=85",
        "description": "Colossal 49\" 32:9 super ultrawide Dual QHD OLED panel with 1800R curvature, Neo Quantum Processor Pro.",
        "msrp": 49900.0,
        "specs": {
            "panel": "49\" OLED 32:9 Super Ultra-wide (5120x1440)",
            "curvature": "1800R",
            "refresh_rate": "240Hz",
            "response_time": "0.03ms",
            "speakers": "5W x 2 Built-in Stereo",
            "warranty": "3 Years Onsite Samsung Thailand"
        }
    },

    # --- Additional PC Cases & Cooling ---
    {
        "name": "NZXT Kraken Elite 360 RGB AIO Liquid CPU Cooler",
        "slug": "nzxt-kraken-elite-360-rgb",
        "category": "PC Cases & Cooling",
        "brand": "NZXT",
        "model_no": "RL-KR36E-B1",
        "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=1200&q=85",
        "description": "High-performance liquid cooling with 2.36\" wide-angle 640x640 LCD display for custom GIFs and system telemetry.",
        "msrp": 10500.0,
        "specs": {
            "radiator_size": "360mm (394 x 121 x 27mm)",
            "display": "2.36\" TFT-LCD (640 x 640, 60Hz, 690 cd/m²)",
            "fans": "3x F120 RGB Core Fans (500 - 1800 RPM)",
            "pump_speed": "800 - 2800 ± 300 RPM",
            "socket_support": "Intel LGA 1851/1700, AMD AM5/AM4",
            "warranty": "6 Years Official Warranty"
        }
    },
    {
        "name": "Lian Li O11 Dynamic EVO RGB PC Gaming Case",
        "slug": "lian-li-o11-dynamic-evo-rgb",
        "category": "PC Cases & Cooling",
        "brand": "Lian Li",
        "model_no": "O11DERGBX",
        "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=1200&q=85",
        "description": "Iconic dual-chamber showcase chassis with removable front pillar for panoramic glass view and ARGB diffuser strips.",
        "msrp": 5590.0,
        "specs": {
            "case_type": "Dual-Chamber Mid-Tower ATX",
            "materials": "4mm Tempered Glass, Aluminum, Steel",
            "radiator_support": "Up to 3x 360mm or 420mm Radiators",
            "gpu_clearance": "455mm (Vertical GPU Ready)",
            "motherboard_support": "E-ATX (under 280mm), ATX, Micro-ATX",
            "warranty": "1 Year Official Warranty"
        }
    },

    # --- Additional Gaming Peripherals ---
    {
        "name": "Logitech G PRO X SUPERLIGHT 2 Wireless Gaming Mouse",
        "slug": "logitech-g-pro-x-superlight-2",
        "category": "Gaming Peripherals",
        "brand": "Logitech",
        "model_no": "910-006631",
        "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=1200&q=85",
        "description": "Pro esports icon weighing only 60g with HERO 2 sensor (32,000 DPI), LIGHTFORCE hybrid switches, and 4K polling.",
        "msrp": 5490.0,
        "specs": {
            "weight": "60 grams",
            "sensor": "HERO 2 (100 – 32,000 DPI, >500 IPS)",
            "switches": "LIGHTFORCE Hybrid Optical-Mechanical",
            "polling_rate": "Up to 4000Hz (0.25ms)",
            "battery_life": "Up to 95 Hours continuous motion",
            "connectivity": "LIGHTSPEED Wireless / USB-C",
            "warranty": "2 Years Synnex Thailand"
        }
    },
    {
        "name": "Razer Viper V3 Pro Ultra-Lightweight Wireless Mouse",
        "slug": "razer-viper-v3-pro-wireless",
        "category": "Gaming Peripherals",
        "brand": "Razer",
        "model_no": "RZ01-05120100-R3A1",
        "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=1200&q=85",
        "description": "54g ultra-lightweight esports mouse with Focus Pro 35K Gen-2 Optical Sensor and true 8000Hz wireless polling.",
        "msrp": 5690.0,
        "specs": {
            "weight": "54 grams",
            "sensor": "Focus Pro 35K Gen-2 Optical (35,000 DPI)",
            "polling_rate": "True 8000Hz HyperPolling Wireless Included",
            "switches": "Optical Mouse Switches Gen-3 (90M clicks)",
            "battery_life": "Up to 95 hours at 1000Hz / 17h at 8000Hz",
            "warranty": "2 Years Synnex / Ascenti Thailand"
        }
    },
    {
        "name": "Wooting 60HE+ Rapid Trigger Analog Keyboard",
        "slug": "wooting-60he-plus-analog-keyboard",
        "category": "Gaming Peripherals",
        "brand": "Wooting",
        "model_no": "WK3-US1-G01-B01",
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=1200&q=85",
        "description": "Hall Effect magnetic switches with 0.1mm - 4.0mm adjustable actuation, Rapid Trigger, and 0.1ms latency.",
        "msrp": 6990.0,
        "specs": {
            "layout": "60% ANSI Compact",
            "switches": "Lekker L60 Hall Effect Linear Magnetic",
            "actuation_point": "0.1mm to 4.0mm (0.1mm increments)",
            "rapid_trigger": "True Rapid Trigger with Dynamic Keystroke",
            "polling_rate": "1000Hz (Tachyon Mode < 1ms)",
            "warranty": "2 Years Official Thailand"
        }
    }
]

async def seed_more_items():
    engine = create_async_engine(settings.DATABASE_URL)
    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with session_maker() as db:
        # Fetch active Thai stores
        store_res = await db.execute(select(Store))
        stores = {s.slug: s for s in store_res.scalars().all()}
        print(f"Loaded {len(stores)} store entities: {list(stores.keys())}")

        now = datetime.utcnow()
        added_count = 0

        store_offsets = {
            "jib": random.uniform(-0.04, 0.02),
            "ihavecpu": random.uniform(-0.08, -0.01),
            "banana": random.uniform(-0.03, 0.03),
            "advice": random.uniform(-0.06, 0.01)
        }

        for pdata in MORE_PRODUCTS:
            # Check if product exists by slug
            check = await db.execute(select(Product).where(Product.slug == pdata["slug"]))
            existing = check.scalar_one_or_none()
            if existing:
                if existing.slug == "logitech-g-pro-x-superlight-2" and "ihavecpu" in stores:
                    listing_res = await db.execute(
                        select(PriceListing).where(
                            PriceListing.product_id == existing.id,
                            PriceListing.store_id == stores["ihavecpu"].id
                        )
                    )
                    listing = listing_res.scalar_one_or_none()
                    if listing:
                        listing.price = 3990.0
                        listing.original_price = round(existing.msrp * 1.06 / 10) * 10
                        listing.last_checked = datetime.utcnow()
                print(f"Skipping existing: {pdata['name']}")
                continue

            prod = Product(**pdata)
            db.add(prod)
            await db.flush()
            added_count += 1
            print(f"Added product #{prod.id}: {prod.name}")

            msrp = prod.msrp
            for slug, st_obj in stores.items():
                offset = store_offsets.get(slug, 0.0)
                if prod.slug == "logitech-g-pro-x-superlight-2" and slug == "ihavecpu":
                    current_p = 3990.0
                else:
                    current_p = round((msrp * (1.0 + offset)) / 10) * 10
                orig_p = round((msrp * 1.06) / 10) * 10 if current_p < msrp else None

                p_url = generate_store_product_url(
                    store_slug=slug,
                    product_name=prod.name,
                    brand=prod.brand,
                    model_no=prod.model_no,
                    product_slug=prod.slug
                )

                listing = PriceListing(
                    product_id=prod.id,
                    store_id=st_obj.id,
                    price=float(current_p),
                    original_price=float(orig_p) if orig_p else None,
                    currency="THB",
                    product_url=p_url,
                    stock_status="in_stock" if random.random() > 0.1 else "low_stock",
                    shipping_cost=0.0,
                    seller_name=st_obj.name,
                    rating=round(random.uniform(4.7, 4.9), 1),
                    review_count=random.randint(150, 3500),
                    last_checked=now
                )
                db.add(listing)

                # Generate historical price trend
                for day_ago in range(30, 0, -3):
                    hist_time = now - timedelta(days=day_ago, hours=random.randint(1, 12))
                    hist_price = round((msrp * (1.0 + offset + random.uniform(-0.03, 0.03))) / 10) * 10
                    db.add(PriceHistory(
                        product_id=prod.id,
                        store_id=st_obj.id,
                        price=float(hist_price),
                        currency="THB",
                        timestamp=hist_time
                    ))

                # Current price point
                db.add(PriceHistory(
                    product_id=prod.id,
                    store_id=st_obj.id,
                    price=float(current_p),
                    currency="THB",
                    timestamp=now
                ))

        await db.commit()
        print(f"Successfully seeded {added_count} new products with complete 4-store listings into Neon DB!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_more_items())
