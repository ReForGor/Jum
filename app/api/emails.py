from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models.email_log import EmailLog
from app.services.email_service import email_service
from app.config import settings

router = APIRouter(prefix="/api/emails", tags=["Email Notifications"])

class SendTestEmailRequest(BaseModel):
    email: EmailStr

@router.post("/test")
async def send_test_email(data: SendTestEmailRequest):
    """
    Sends a test email to verify SMTP configuration and email template styling.
    """
    test_html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: sans-serif; background-color: #0b0f19; color: #f3f4f6; padding: 20px;">
    <div style="max-width: 500px; margin: 0 auto; background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 24px; text-align: center;">
        <h2 style="color: #38bdf8; margin-top: 0;">⚡ TechPrice Thailand</h2>
        <div style="background-color: #10b981; color: white; padding: 8px 16px; border-radius: 20px; display: inline-block; font-weight: bold; margin: 10px 0;">
            ✅ ทดสอบระบบส่งอีเมลสำเร็จ!
        </div>
        <p style="color: #d1d5db; font-size: 14px; margin: 15px 0;">
            ยินดีด้วยครับ! ระบบแจ้งเตือนทางอีเมลของ <strong>TechPrice</strong> เชื่อมต่อและทำงานได้สมบูรณ์แบบ
        </p>
        <div style="background-color: #0f172a; border-radius: 8px; padding: 12px; font-size: 12px; color: #9ca3af; text-align: left; margin: 15px 0;">
            <div>• <strong>ผู้รับ:</strong> {data.email}</div>
            <div>• <strong>SMTP Server:</strong> {settings.SMTP_HOST or 'Dev Mode (Simulation)'}</div>
            <div>• <strong>จาก:</strong> {settings.SMTP_FROM_NAME} &lt;{settings.SMTP_FROM_EMAIL}&gt;</div>
        </div>
        <p style="font-size: 12px; color: #6b7280; margin-bottom: 0;">
            เมื่อราคาสินค้าที่ท่านตั้งเตือนลดลง ระบบจะส่งข้อมูลพร้อมลิงก์ร้านค้ามายังอีเมลนี้ทันทีครับ
        </p>
    </div>
</body>
</html>
"""
    result = await email_service.send_email(
        to_email=data.email,
        subject="🧪 [TechPrice] ทดสอบระบบแจ้งเตือนทางอีเมลสำเร็จ!",
        html_content=test_html,
        text_content=f"TechPrice: ทดสอบระบบแจ้งเตือนทางอีเมลสำหรับ {data.email} สำเร็จเรียบร้อยแล้ว!"
    )
    return {
        "success": result["status"] in ("sent", "simulated"),
        "details": result,
        "smtp_configured": bool(settings.SMTP_HOST and settings.SMTP_USER),
        "smtp_host": settings.SMTP_HOST or "None (Running in dev simulation mode)"
    }

@router.get("/outbox")
async def get_email_outbox(
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns the recent email notification logs and previews.
    """
    res = await db.execute(
        select(EmailLog).order_by(desc(EmailLog.created_at)).limit(limit)
    )
    logs = res.scalars().all()
    return [
        {
            "id": l.id,
            "recipient": l.recipient,
            "subject": l.subject,
            "status": l.status,
            "error_message": l.error_message,
            "product_id": l.product_id,
            "created_at": l.created_at.isoformat() if l.created_at else None,
            "html_preview": l.html_content[:300] + "..." if len(l.html_content) > 300 else l.html_content
        }
        for l in logs
    ]

