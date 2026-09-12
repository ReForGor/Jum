import asyncio
import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Dict, Any

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.email_log import EmailLog

logger = logging.getLogger("techprice.email")

def _send_smtp_sync(to_email: str, subject: str, html_body: str, text_body: str) -> None:
    """Synchronous SMTP worker executed in a thread pool."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    msg["To"] = to_email

    # Plain text version for fallback
    part1 = MIMEText(text_body, "plain", "utf-8")
    # HTML version
    part2 = MIMEText(html_body, "html", "utf-8")
    msg.attach(part1)
    msg.attach(part2)

    server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15)
    try:
        if settings.SMTP_TLS:
            server.starttls()
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
    finally:
        server.quit()

class EmailService:
    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        product_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Dispatches an email via SMTP or records it in dev simulation mode.
        Automatically logs to the email_logs database table.
        """
        if not to_email or "@" not in to_email:
            logger.warning(f"[EmailService] Invalid recipient email: {to_email}")
            return {"status": "error", "error": "Invalid email address"}

        plain_text = text_content or f"{subject}\n\nVisit: {settings.SMTP_FROM_EMAIL}"
        status = "sent"
        error_msg = None

        # Check if real SMTP credentials are provided
        has_smtp = bool(settings.SMTP_HOST and (settings.SMTP_USER or settings.SMTP_PORT == 25))

        if has_smtp:
            try:
                logger.info(f"📧 [EmailService] Sending live SMTP email to {to_email} via {settings.SMTP_HOST}:{settings.SMTP_PORT}...")
                await asyncio.to_thread(_send_smtp_sync, to_email, subject, html_content, plain_text)
                status = "sent"
                logger.info(f"✅ [EmailService] Live email delivered to {to_email}!")
            except Exception as ex:
                logger.error(f"❌ [EmailService] SMTP delivery failed to {to_email}: {ex}")
                status = "failed"
                error_msg = str(ex)
        else:
            # Dev simulation mode
            status = "simulated"
            logger.info(f"📬 [EmailService (Simulation)] Email queued for {to_email} | Subject: '{subject}'")

        # Save record in database
        try:
            async with AsyncSessionLocal() as db:
                log_entry = EmailLog(
                    recipient=to_email,
                    subject=subject,
                    html_content=html_content,
                    status=status,
                    error_message=error_msg,
                    product_id=product_id,
                    created_at=datetime.utcnow()
                )
                db.add(log_entry)
                await db.commit()
        except Exception as db_err:
            logger.error(f"[EmailService] Could not save email log: {db_err}")

        return {
            "status": status,
            "recipient": to_email,
            "subject": subject,
            "error": error_msg,
            "mode": "live_smtp" if (has_smtp and status == "sent") else ("smtp_failed" if has_smtp else "dev_simulation")
        }

    @staticmethod
    async def send_price_drop_alert(
        to_email: str,
        product_name: str,
        new_price: float,
        target_price: float,
        store_name: str,
        product_url: str,
        product_image: Optional[str] = None,
        product_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Sends a high-converting, beautiful price drop alert email in Thai.
        """
        savings = max(0.0, target_price - new_price)
        subject = f"🔥 [TechPrice] ราคาลดแล้ว! {product_name[:35]}... เหลือเพียง ฿{new_price:,.2f} ที่ {store_name}"

        img_html = f'<img src="{product_image}" alt="{product_name}" style="max-height: 180px; max-width: 100%; border-radius: 8px; margin: 0 auto; display: block; object-fit: contain;">' if product_image else ''

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{subject}</title>
<style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0b0f19; color: #f3f4f6; margin: 0; padding: 0; }}
    .container {{ max-width: 600px; margin: 20px auto; background-color: #111827; border: 1px solid #1f2937; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
    .header {{ background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); padding: 24px; text-align: center; border-bottom: 1px solid #374151; }}
    .header h1 {{ margin: 0; font-size: 20px; color: #38bdf8; letter-spacing: 0.5px; }}
    .badge-deal {{ display: inline-block; background-color: #dc2626; color: #fff; font-size: 11px; font-weight: bold; padding: 4px 10px; border-radius: 20px; margin-top: 8px; text-transform: uppercase; letter-spacing: 1px; }}
    .content {{ padding: 28px 24px; }}
    .product-card {{ background-color: #1f2937; border: 1px solid #374151; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 24px; }}
    .product-title {{ font-size: 16px; font-weight: bold; color: #ffffff; margin-top: 14px; line-height: 1.4; }}
    .price-box {{ display: flex; justify-content: space-around; background-color: #0f172a; border-radius: 10px; padding: 16px; margin: 20px 0; }}
    .price-col {{ text-align: center; }}
    .price-label {{ font-size: 11px; color: #9ca3af; text-transform: uppercase; margin-bottom: 4px; }}
    .price-old {{ font-size: 15px; color: #ef4444; text-decoration: line-through; }}
    .price-new {{ font-size: 24px; font-weight: 800; color: #10b981; }}
    .store-badge {{ display: inline-block; background-color: #0284c7; color: #ffffff; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: bold; margin-bottom: 20px; }}
    .btn-buy {{ display: block; width: 85%; margin: 15px auto 0; background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%); color: #ffffff !important; text-decoration: none; text-align: center; padding: 14px 20px; border-radius: 10px; font-size: 15px; font-weight: bold; box-shadow: 0 4px 14px rgba(6, 182, 212, 0.4); }}
    .footer {{ background-color: #0f172a; padding: 20px; text-align: center; font-size: 11px; color: #6b7280; border-top: 1px solid #1f2937; }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>⚡ TechPrice Thailand</h1>
        <div class="badge-deal">🔥 แจ้งเตือนราคาลดพิเศษ (Price Drop Alert)</div>
    </div>
    <div class="content">
        <p style="font-size: 14px; color: #d1d5db; margin-top: 0;">
            สวัสดีครับ! สินค้าที่คุณกำลังติดตามราคาลดลงมาถึงราคาเป้าหมายที่คุณต้องการแล้ว:
        </p>

        <div class="product-card">
            {img_html}
            <div class="product-title">{product_name}</div>
            
            <div class="price-box">
                <div class="price-col">
                    <div class="price-label">ราคาเป้าหมายของคุณ</div>
                    <div class="price-old">฿{target_price:,.2f}</div>
                </div>
                <div class="price-col">
                    <div class="price-label">ราคาพิเศษปัจจุบัน</div>
                    <div class="price-new">฿{new_price:,.2f}</div>
                </div>
            </div>

            <div class="store-badge">
                📍 วางจำหน่ายที่: <strong>{store_name}</strong>
            </div>

            <a href="{product_url}" class="btn-buy" target="_blank">
                👉 ไปที่ร้าน {store_name} เพื่อสั่งซื้อราคานี้ทันที
            </a>
        </div>

        <p style="font-size: 12px; color: #9ca3af; text-align: center; margin-bottom: 0;">
            💡 <em>หมายเหตุ: ราคาสินค้าและโปรโมชั่นอาจมีการเปลี่ยนแปลงหรือสินค้าหมดสต็อก แนะนำให้ตรวจสอบและสั่งซื้อโดยเร็วครับ</em>
        </p>
    </div>
    <div class="footer">
        คุณได้รับอีเมลนี้เนื่องจากตั้งค่า Price Alert ไว้ที่ระบบเปรียบเทียบราคา TechPrice Thailand<br>
        ติดตามราคาฮาร์ดแวร์ไอที 4 ร้านค้าหลัก (JIB, Advice, iHaveCPU, BaNANA IT)
    </div>
</div>
</body>
</html>
"""
        plain_text = (
            f"⚡ TechPrice แจ้งเตือนราคาลดพิเศษ!\n\n"
            f"สินค้า: {product_name}\n"
            f"ราคาเป้าหมาย: ฿{target_price:,.2f}\n"
            f"ราคาใหม่พิเศษ: ฿{new_price:,.2f} (ประหยัดได้ ฿{savings:,.2f})\n"
            f"ร้านค้า: {store_name}\n\n"
            f"สั่งซื้อราคานี้ได้ที่: {product_url}\n"
        )

        return await EmailService.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_body,
            text_content=plain_text,
            product_id=product_id
        )

    @staticmethod
    async def send_alert_confirmation(
        to_email: str,
        product_name: str,
        target_price: float,
        current_lowest_price: float,
        product_image: Optional[str] = None,
        product_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Sends an email confirming that the user has successfully set up a price alert.
        """
        subject = f"✅ [TechPrice] ยืนยันการตั้งค่าแจ้งเตือนราคา: {product_name[:35]}..."
        img_html = f'<img src="{product_image}" alt="{product_name}" style="max-height: 140px; max-width: 100%; border-radius: 8px; margin: 0 auto; display: block; object-fit: contain;">' if product_image else ''

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #0b0f19; color: #f3f4f6; margin: 0; padding: 0; }}
    .container {{ max-width: 580px; margin: 20px auto; background-color: #111827; border: 1px solid #1f2937; border-radius: 16px; overflow: hidden; }}
    .header {{ background: #0f172a; padding: 20px; text-align: center; border-bottom: 1px solid #374151; }}
    .content {{ padding: 24px; }}
    .card {{ background-color: #1f2937; border-radius: 10px; padding: 18px; text-align: center; margin: 18px 0; }}
    .price-highlight {{ color: #06b6d4; font-size: 20px; font-weight: bold; }}
    .footer {{ background-color: #0f172a; padding: 16px; text-align: center; font-size: 11px; color: #6b7280; }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h2 style="color: #38bdf8; margin: 0;">⚡ TechPrice Thailand</h2>
        <p style="color: #10b981; font-size: 13px; font-weight: bold; margin: 6px 0 0 0;">✅ ยืนยันการเริ่มติดตามราคาเรียบร้อยแล้ว</p>
    </div>
    <div class="content">
        <p style="font-size: 14px; color: #d1d5db;">
            เราได้บันทึกการตั้งค่าแจ้งเตือนของคุณเรียบร้อยแล้ว ระบบจะตรวจเช็คราคาจาก <strong>JIB, Advice, iHaveCPU และ BaNANA IT</strong> ให้ทุกวันตลอด 24 ชั่วโมง
        </p>

        <div class="card">
            {img_html}
            <h4 style="color: #ffffff; margin: 10px 0 14px 0;">{product_name}</h4>
            <p style="font-size: 13px; color: #9ca3af; margin: 4px 0;">ราคาต่ำสุดในตลาดปัจจุบัน: <strong>฿{current_lowest_price:,.2f}</strong></p>
            <p style="font-size: 14px; color: #f3f4f6; margin: 8px 0;">เป้าหมายที่คุณต้องการ: <span class="price-highlight">฿{target_price:,.2f}</span></p>
        </div>

        <p style="font-size: 13px; color: #9ca3af; text-align: center;">
            🔔 ทันทีที่ราคาของสินค้านี้ลดลงมาถึงหรือต่ำกว่า <strong>฿{target_price:,.2f}</strong> เราจะส่งอีเมลแจ้งเตือนให้คุณทราบทันทีครับ!
        </p>
    </div>
    <div class="footer">
        TechPrice Thailand - ระบบติดตามและเปรียบเทียบราคาฮาร์ดแวร์ไอที
    </div>
</div>
</body>
</html>
"""
        plain_text = (
            f"✅ [TechPrice] ยืนยันการตั้งค่าแจ้งเตือนราคา\n\n"
            f"สินค้า: {product_name}\n"
            f"ราคาต่ำสุดปัจจุบัน: ฿{current_lowest_price:,.2f}\n"
            f"ราคาเป้าหมายของคุณ: ฿{target_price:,.2f}\n\n"
            f"ระบบจะตรวจสอบราคาทุกวันจาก JIB, Advice, iHaveCPU, BaNANA IT และส่งอีเมลแจ้งเตือนทันทีเมื่อราคาถึงเป้าหมายครับ!"
        )

        return await EmailService.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_body,
            text_content=plain_text,
            product_id=product_id
        )

email_service = EmailService()

