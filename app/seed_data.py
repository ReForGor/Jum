import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.store import Store
from app.models.product import Product
from app.models.price_listing import PriceListing
from app.models.price_history import PriceHistory
from app.models.user import User
from app.models.alert import PriceAlert
from app.models.notification import Notification
from app.auth import hash_password

# Top Thailand IT Hardware Retail Platforms
THAI_STORES_DATA = [
    {
        "name": "JIB Computer Group",
        "slug": "jib",
        "logo_url": "https://www.jib.co.th/web/images/logo/logo_jib.png",
        "base_url": "https://www.jib.co.th",
        "color": "#f59e0b",
        "scraper_type": "jib"
    },
    {
        "name": "iHaveCPU",
        "slug": "ihavecpu",
        "logo_url": "https://www.ihavecpu.com/images/logo.png",
        "base_url": "https://www.ihavecpu.com",
        "color": "#ef4444",
        "scraper_type": "ihavecpu"
    },
    {
        "name": "BaNANA IT",
        "slug": "banana",
        "logo_url": "https://media-cdn.bnn.in.th/289945/banana-logo.png",
        "base_url": "https://www.bnn.in.th",
        "color": "#22c55e",
        "scraper_type": "banana"
    },
    {
        "name": "Advice IT Infinite",
        "slug": "advice",
        "logo_url": "https://www.advice.co.th/assets/images/advice-logo.png",
        "base_url": "https://www.advice.co.th",
        "color": "#3b82f6",
        "scraper_type": "advice"
    }
]

PRODUCTS_DATA = [
    # --- GPUs ---
    {
        "name": "NVIDIA GeForce RTX 5090 32GB GDDR7",
        "slug": "nvidia-geforce-rtx-5090-32gb",
        "category": "Graphics Cards (GPU)",
        "brand": "NVIDIA",
        "model_no": "RTX-5090-FE",
        "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=600&q=80",
        "description": "Flagship Blackwell architecture GPU with 32GB GDDR7 VRAM, 512-bit bus, 21,760 CUDA cores, and DLSS 4 support.",
        "msrp": 79900.0,
        "specs": {
            "vram": "32GB GDDR7",
            "bus_width": "512-bit",
            "cuda_cores": "21,760",
            "boost_clock": "2.55 GHz",
            "tdp": "600W",
            "interface": "PCIe 5.0 x16",
            "outputs": "1x HDMI 2.1b, 3x DisplayPort 2.1b",
            "warranty": "3 Years Thailand Official"
        }
    },
    {
        "name": "NVIDIA GeForce RTX 5080 16GB GDDR7",
        "slug": "nvidia-geforce-rtx-5080-16gb",
        "category": "Graphics Cards (GPU)",
        "brand": "NVIDIA",
        "model_no": "RTX-5080-FE",
        "image_url": "https://images.unsplash.com/photo-1591488320449-011701bb6704?auto=format&fit=crop&w=600&q=80",
        "description": "High-end Blackwell GPU featuring 16GB ultra-fast 30Gbps GDDR7 memory, 10,752 CUDA cores, and extreme 4K ray tracing.",
        "msrp": 39900.0,
        "specs": {
            "vram": "16GB GDDR7",
            "bus_width": "256-bit",
            "cuda_cores": "10,752",
            "boost_clock": "2.68 GHz",
            "tdp": "400W",
            "interface": "PCIe 5.0 x16",
            "warranty": "3 Years Thailand Official"
        }
    },
    {
        "name": "AMD Radeon RX 7900 XTX 24GB",
        "slug": "amd-radeon-rx-7900-xtx-24gb",
        "category": "Graphics Cards (GPU)",
        "brand": "AMD",
        "model_no": "RX-7900-XTX",
        "image_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=600&q=80",
        "description": "RDNA 3 flagship GPU with 24GB GDDR6, 96 Compute Units, DisplayPort 2.1, and 2nd Gen Raytracing Accelerators.",
        "msrp": 34900.0,
        "specs": {
            "vram": "24GB GDDR6",
            "bus_width": "384-bit",
            "stream_processors": "6,144",
            "boost_clock": "2.50 GHz",
            "tdp": "355W",
            "warranty": "3 Years Thailand Official"
        }
    },
    {
        "name": "NVIDIA GeForce RTX 4070 Ti Super 16GB",
        "slug": "nvidia-geforce-rtx-4070-ti-super-16gb",
        "category": "Graphics Cards (GPU)",
        "brand": "NVIDIA",
        "model_no": "RTX-4070TIS-16G",
        "image_url": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?auto=format&fit=crop&w=600&q=80",
        "description": "Ada Lovelace architecture with upgraded 16GB GDDR6X and 256-bit bus, ideal for high frame-rate 1440p and 4K gaming.",
        "msrp": 29900.0,
        "specs": {
            "vram": "16GB GDDR6X",
            "bus_width": "256-bit",
            "cuda_cores": "8,448",
            "boost_clock": "2.61 GHz",
            "tdp": "285W",
            "warranty": "3 Years Thailand Official"
        }
    },

    # --- CPUs ---
    {
        "name": "AMD Ryzen 7 9800X3D 8-Core Gaming Processor",
        "slug": "amd-ryzen-7-9800x3d",
        "category": "Processors (CPU)",
        "brand": "AMD",
        "model_no": "100-100001084WOF",
        "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?auto=format&fit=crop&w=600&q=80",
        "description": "The world's fastest gaming processor built on Zen 5 with 2nd generation 3D V-Cache, 96MB L3 cache, and full overclocking support.",
        "msrp": 18900.0,
        "specs": {
            "cores_threads": "8 Cores / 16 Threads",
            "base_clock": "4.7 GHz",
            "boost_clock": "5.2 GHz",
            "cache": "104MB Total (96MB L3)",
            "socket": "AM5",
            "tdp": "120W",
            "warranty": "3 Years (Synnex / SVOA)"
        }
    },
    {
        "name": "AMD Ryzen 9 9950X 16-Core 32-Thread Processor",
        "slug": "amd-ryzen-9-9950x",
        "category": "Processors (CPU)",
        "brand": "AMD",
        "model_no": "100-100001277WOF",
        "image_url": "https://images.unsplash.com/photo-1555680202-c86f0e12f086?auto=format&fit=crop&w=600&q=80",
        "description": "Zen 5 flagship workstation/content creation CPU with 16 cores, 32 threads, 5.7GHz boost, and PCIe Gen 5 readiness.",
        "msrp": 24900.0,
        "specs": {
            "cores_threads": "16 Cores / 32 Threads",
            "base_clock": "4.3 GHz",
            "boost_clock": "5.7 GHz",
            "cache": "80MB Total (64MB L3)",
            "socket": "AM5",
            "tdp": "170W",
            "warranty": "3 Years (Synnex / Ingram)"
        }
    },
    {
        "name": "Intel Core Ultra 9 285K 24-Core Processor",
        "slug": "intel-core-ultra-9-285k",
        "category": "Processors (CPU)",
        "brand": "Intel",
        "model_no": "BX80768285K",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=600&q=80",
        "description": "Arrow Lake flagship desktop processor featuring 8 Performance Cores + 16 Efficient Cores, dedicated NPU for AI, and LGA 1851 socket.",
        "msrp": 23500.0,
        "specs": {
            "cores_threads": "24 Cores (8P + 16E) / 24 Threads",
            "base_clock": "3.7 GHz (P-core)",
            "boost_clock": "5.7 GHz",
            "cache": "36MB Intel Smart Cache + 40MB L2",
            "socket": "LGA 1851",
            "tdp": "125W Base / 250W Max Turbo",
            "warranty": "3 Years (WPG / Synnex)"
        }
    },

    # --- Laptops ---
    {
        "name": "Apple MacBook Pro 16\" M4 Max (36GB RAM, 1TB SSD)",
        "slug": "apple-macbook-pro-16-m4-max",
        "category": "Laptops & Notebooks",
        "brand": "Apple",
        "model_no": "MX2V3TH/A",
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80",
        "description": "Liquid Retina XDR display with nano-texture option, 14-core CPU / 32-core GPU M4 Max chip, 24-hour battery life, and Thunderbolt 5 ports.",
        "msrp": 129900.0,
        "specs": {
            "display": "16.2\" Liquid Retina XDR (3456x2234, 120Hz ProMotion, 1600 nits)",
            "processor": "Apple M4 Max (14-Core CPU, 32-Core GPU)",
            "memory": "36GB Unified Memory (410GB/s)",
            "storage": "1TB NVMe SSD",
            "battery": "100Wh (up to 24 hours)",
            "warranty": "1 Year AppleCare Thailand"
        }
    },
    {
        "name": "ASUS ROG Zephyrus G16 OLED Gaming Laptop",
        "slug": "asus-rog-zephyrus-g16-oled",
        "category": "Laptops & Notebooks",
        "brand": "ASUS",
        "model_no": "GU605MZ-QR043W",
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=600&q=80",
        "description": "Ultra-slim CNC aluminum gaming laptop with 16\" 2.5K 240Hz ROG Nebula OLED, Intel Core Ultra 9 185H, and RTX 4080.",
        "msrp": 89900.0,
        "specs": {
            "display": "16\" 2.5K (2560x1600) 240Hz 0.2ms OLED, 100% DCI-P3",
            "processor": "Intel Core Ultra 9 185H (16-core)",
            "gpu": "NVIDIA GeForce RTX 4080 12GB GDDR6",
            "memory": "32GB LPDDR5X-7467MHz",
            "storage": "2TB PCIe 4.0 NVMe SSD",
            "warranty": "3 Years On-site + 1 Year Perfect Warranty"
        }
    },

    # --- Storage & SSDs ---
    {
        "name": "Samsung 990 PRO 2TB PCIe 4.0 M.2 NVMe SSD",
        "slug": "samsung-990-pro-2tb-nvme-ssd",
        "category": "Storage (SSD & HDD)",
        "brand": "Samsung",
        "model_no": "MZ-V9P2T0B/TH",
        "image_url": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?auto=format&fit=crop&w=600&q=80",
        "description": "Sequential read speeds up to 7,450 MB/s and write speeds up to 6,900 MB/s. Built with Samsung V-NAND TLC and Nickel-coated controller.",
        "msrp": 6890.0,
        "specs": {
            "capacity": "2TB",
            "interface": "PCIe Gen 4.0 x4, NVMe 2.0",
            "seq_read": "Up to 7,450 MB/s",
            "seq_write": "Up to 6,900 MB/s",
            "warranty": "5 Years Thailand Official"
        }
    },
    {
        "name": "Crucial T705 2TB PCIe Gen5 NVMe M.2 SSD",
        "slug": "crucial-t705-2tb-gen5-ssd",
        "category": "Storage (SSD & HDD)",
        "brand": "Crucial",
        "model_no": "CT2000T705SSD3",
        "image_url": "https://images.unsplash.com/photo-1544652478-6653e09f18a2?auto=format&fit=crop&w=600&q=80",
        "description": "Blazing Gen5 performance with read speeds up to 14,500 MB/s and write speeds up to 12,700 MB/s, Micron 232-layer TLC NAND.",
        "msrp": 9990.0,
        "specs": {
            "capacity": "2TB",
            "interface": "PCIe Gen 5.0 x4, NVMe 2.0",
            "seq_read": "Up to 14,500 MB/s",
            "seq_write": "Up to 12,700 MB/s",
            "warranty": "5 Years Thailand Official"
        }
    },

    # --- Memory / RAM ---
    {
        "name": "Corsair Vengeance RGB DDR5 64GB (2x32GB) 6000MHz CL30",
        "slug": "corsair-vengeance-rgb-ddr5-64gb-6000mhz",
        "category": "Memory (RAM)",
        "brand": "Corsair",
        "model_no": "CMH64GX5M2B6000C30",
        "image_url": "https://images.unsplash.com/photo-1562976540-1502c2145186?auto=format&fit=crop&w=600&q=80",
        "description": "High performance DDR5 memory kit with dynamic ten-zone RGB lighting, Intel XMP 3.0 & AMD EXPO profile support, CL30 low latency.",
        "msrp": 7490.0,
        "specs": {
            "capacity": "64GB (2 x 32GB)",
            "speed": "DDR5-6000 MHz",
            "timing": "CL30 (30-36-36-76)",
            "warranty": "Lifetime Warranty (Ascenti)"
        }
    },

    # --- Monitors ---
    {
        "name": "LG UltraGear 32GS95UE 32\" 4K 240Hz / 1080p 480Hz Dual-Mode OLED",
        "slug": "lg-ultragear-32gs95ue-32-oled",
        "category": "Monitors & Displays",
        "brand": "LG",
        "model_no": "32GS95UE-B",
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=600&q=80",
        "description": "World's first VESA-certified Dual-Hz OLED monitor: 4K @ 240Hz for immersive AAA gaming or 1080p @ 480Hz for competitive esports at 0.03ms response.",
        "msrp": 45900.0,
        "specs": {
            "screen_size": "31.5\" WOLED Flat",
            "resolution_refresh": "4K (3840x2160) @ 240Hz / FHD @ 480Hz",
            "response_time": "0.03ms (GtG)",
            "warranty": "3 Years On-site (LG Thailand)"
        }
    },
    {
        "name": "Dell Alienware AW3423DWF 34\" Curved QD-OLED 165Hz",
        "slug": "dell-alienware-aw3423dwf-34-curved-qd-oled",
        "category": "Monitors & Displays",
        "brand": "Dell Alienware",
        "model_no": "AW3423DWF",
        "image_url": "https://images.unsplash.com/photo-1586210579191-33b45e38fa2c?auto=format&fit=crop&w=600&q=80",
        "description": "Quantum Dot OLED 1800R curved gaming monitor with infinite contrast, 99.3% DCI-P3 color gamut, and 0.1ms response time.",
        "msrp": 28900.0,
        "specs": {
            "screen_size": "34.18\" QD-OLED 1800R Curved",
            "resolution": "UWQHD (3440 x 1440) @ 165Hz",
            "response_time": "0.1ms (GtG)",
            "warranty": "3 Years Premium Panel Exchange (Dell Thailand)"
        }
    },

    # --- Power Supplies ---
    {
        "name": "Corsair RM1000x Shift 1000W 80 PLUS Gold Fully Modular ATX 3.0",
        "slug": "corsair-rm1000x-shift-1000w-gold",
        "category": "Power Supplies (PSU)",
        "brand": "Corsair",
        "model_no": "CP-9020253-NA",
        "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=600&q=80",
        "description": "Side-mounted modular interface for easier cable management, 100% Japanese 105°C capacitors, ATX 3.0 certified with PCIe 5.0 12VHPWR cable.",
        "msrp": 6590.0,
        "specs": {
            "wattage": "1000 Watts",
            "efficiency": "80 PLUS Gold",
            "standards": "ATX 3.0, PCIe 5.0 Ready",
            "warranty": "10 Years (Ascenti / Scanner)"
        }
    }
]

async def seed_initial_data(db: AsyncSession):
    # Clear & re-seed with Thai stores & realistic THB catalog
    store_res = await db.execute(select(Store))
    existing_stores = store_res.scalars().all()

    store_entities = {}
    if not existing_stores or len(existing_stores) < 4 or existing_stores[0].slug == "amazon":
        # Clear legacy stores and products to switch cleanly to Thai stores
        await db.execute(delete(PriceHistory))
        await db.execute(delete(PriceListing))
        await db.execute(delete(Notification))
        await db.execute(delete(PriceAlert))
        await db.execute(delete(Product))
        await db.execute(delete(Store))
        await db.flush()

        for sdata in THAI_STORES_DATA:
            st = Store(**sdata)
            db.add(st)
            await db.flush()
            store_entities[st.slug] = st
    else:
        for s in existing_stores:
            store_entities[s.slug] = s

    # Check / Create Demo User
    user_res = await db.execute(select(User).where(User.email == "gamer@demo.com"))
    demo_user = user_res.scalar_one_or_none()
    if not demo_user:
        demo_user = User(
            email="gamer@demo.com",
            username="SomchaiGamer",
            full_name="Somchai TechGamer",
            hashed_password=hash_password("password123"),
            is_admin=False
        )
        db.add(demo_user)
        await db.flush()

    # Check / Create Admin User
    admin_res = await db.execute(select(User).where(User.email == "admin@techprice.com"))
    admin_user = admin_res.scalar_one_or_none()
    if not admin_user:
        admin_user = User(
            email="admin@techprice.com",
            username="admin",
            full_name="System Administrator",
            hashed_password=hash_password("admin123"),
            is_admin=True
        )
        db.add(admin_user)
        await db.flush()

    from app.seed_more import MORE_PRODUCTS
    all_seed_products = PRODUCTS_DATA + MORE_PRODUCTS

    # Create Products & Thai Store Listings
    prod_res = await db.execute(select(Product))
    existing_prods_map = {p.slug: p for p in prod_res.scalars().all()}

    now = datetime.utcnow()
    created_prods = []

    for pdata in all_seed_products:
        if pdata["slug"] in existing_prods_map:
            continue
        prod = Product(**pdata)
        db.add(prod)
        await db.flush()
        created_prods.append(prod)
        existing_prods_map[prod.slug] = prod

        msrp = prod.msrp
        
        # Thai Store Pricing Offsets
        store_offsets = {
            "jib": random.uniform(-0.04, 0.02),
            "ihavecpu": random.uniform(-0.08, -0.01),  # iHaveCPU often lower on custom hardware
            "banana": random.uniform(-0.03, 0.03),
            "advice": random.uniform(-0.06, 0.01)     # Advice competitive prices
        }

        for slug, st_obj in store_entities.items():
            offset = store_offsets.get(slug, 0.0)
            current_p = round((msrp * (1.0 + offset)) / 10) * 10
            orig_p = round((msrp * 1.06) / 10) * 10 if current_p < msrp else None
            
            # Direct Thai store product search/buy link
            if slug == "jib":
                p_url = f"https://www.jib.co.th/web/product/search?keyword={prod.name.replace(' ', '+')}"
            elif slug == "ihavecpu":
                p_url = f"https://www.ihavecpu.com/search?q={prod.name.replace(' ', '+')}"
            elif slug == "banana":
                p_url = f"https://www.bnn.in.th/th/p?q={prod.name.replace(' ', '+')}"
            else:
                p_url = f"https://www.advice.co.th/product/search?keyword={prod.name.replace(' ', '+')}"

            listing = PriceListing(
                product_id=prod.id,
                store_id=st_obj.id,
                price=float(current_p),
                original_price=float(orig_p) if orig_p else None,
                currency="THB",
                product_url=p_url,
                stock_status="in_stock" if random.random() > 0.08 else "low_stock",
                shipping_cost=0.0,
                seller_name=st_obj.name,
                rating=round(random.uniform(4.7, 4.9), 1),
                review_count=random.randint(250, 4200),
                last_checked=now
            )
            db.add(listing)

            # Generate 15 historical points across 30 days
            for day_ago in range(30, 0, -2):
                hist_time = now - timedelta(days=day_ago, hours=random.randint(1, 12))
                hist_price = round((msrp * (1.0 + offset + random.uniform(-0.03, 0.03))) / 10) * 10
                history_entry = PriceHistory(
                    product_id=prod.id,
                    store_id=st_obj.id,
                    price=float(hist_price),
                    currency="THB",
                    timestamp=hist_time
                )
                db.add(history_entry)

            # Current price point
            db.add(PriceHistory(
                product_id=prod.id,
                store_id=st_obj.id,
                price=float(current_p),
                currency="THB",
                timestamp=now
            ))

        # Create demo alerts & notifications for demo user
        if created_prods:
            rtx5090 = created_prods[0]
            ryzen9800x3d = created_prods[4]

            # Alert 1: RTX 5090 target ฿76,000
            alert1 = PriceAlert(
                user_id=demo_user.id,
                product_id=rtx5090.id,
                email=demo_user.email,
                target_price=76000.0,
                currency="THB",
                is_active=True,
                current_lowest_price=74900.0,
                triggered_at=now - timedelta(hours=2)
            )
            db.add(alert1)
            await db.flush()

            # Notification 1
            db.add(Notification(
                user_id=demo_user.id,
                email=demo_user.email,
                product_id=rtx5090.id,
                alert_id=alert1.id,
                title=f"🔥 Price Drop Alert: {rtx5090.name}",
                message=f"Great news! {rtx5090.name} dropped to ฿74,900.00 on iHaveCPU (Below your target ฿76,000.00)!",
                old_price=79900.0,
                new_price=74900.0,
                store_name="iHaveCPU",
                product_url="https://www.ihavecpu.com",
                currency="THB",
                is_read=False,
                created_at=now - timedelta(hours=2)
            ))

            # Alert 2: Ryzen 7 9800X3D target ฿18,000
            alert2 = PriceAlert(
                user_id=demo_user.id,
                product_id=ryzen9800x3d.id,
                email=demo_user.email,
                target_price=18000.0,
                currency="THB",
                is_active=True,
                current_lowest_price=17890.0,
                triggered_at=now - timedelta(hours=5)
            )
            db.add(alert2)
            await db.flush()

            # Notification 2
            db.add(Notification(
                user_id=demo_user.id,
                email=demo_user.email,
                product_id=ryzen9800x3d.id,
                alert_id=alert2.id,
                title=f"🔥 Price Drop Alert: {ryzen9800x3d.name}",
                message=f"{ryzen9800x3d.name} is on flash sale for ฿17,890.00 on Advice IT (Below your target ฿18,000.00)!",
                old_price=18900.0,
                new_price=17890.0,
                store_name="Advice IT Infinite",
                product_url="https://www.advice.co.th",
                currency="THB",
                is_read=False,
                created_at=now - timedelta(hours=5)
            ))

        await db.commit()
