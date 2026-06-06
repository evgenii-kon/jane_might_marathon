import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings


async def send_email(to: str, subject: str, html: str) -> None:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.SMTP_FROM
    message["To"] = to
    message.attach(MIMEText(html, "html"))

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        use_tls=True,
    )


async def send_verification_email(to: str, token: str) -> None:
    link = f"{settings.APP_URL}/auth/verify-email?token={token}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
        <h2>Подтверждение email</h2>
        <p>Нажмите на кнопку чтобы подтвердить адрес:</p>
        <a href="{link}" style="background:#4CAF50;color:white;padding:12px 24px;
           text-decoration:none;border-radius:4px;display:inline-block;margin:16px 0;">
            Подтвердить email
        </a>
        <p style="color:#666;font-size:14px;">Ссылка действует 24 часа.</p>
        <p style="color:#666;font-size:14px;">Если вы не регистрировались — проигнорируйте письмо.</p>
    </div>
    """
    await send_email(to, "Подтверждение email — Jane Marathon", html)


async def send_reset_password_email(to: str, token: str) -> None:
    link = f"{settings.APP_URL}/auth/reset-password?token={token}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
        <h2>Сброс пароля</h2>
        <p>Нажмите на кнопку чтобы сбросить пароль:</p>
        <a href="{link}" style="background:#2196F3;color:white;padding:12px 24px;
           text-decoration:none;border-radius:4px;display:inline-block;margin:16px 0;">
            Сбросить пароль
        </a>
        <p style="color:#666;font-size:14px;">Ссылка действует 15 минут.</p>
        <p style="color:#666;font-size:14px;">Если вы не запрашивали сброс — проигнорируйте письмо.</p>
    </div>
    """
    await send_email(to, "Сброс пароля — Jane Marathon", html)