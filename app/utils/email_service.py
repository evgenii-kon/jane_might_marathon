import resend
from app.config import settings

resend.api_key = settings.RESEND_API_KEY


async def send_verification_email(to: str, token: str) -> None:
    link = f"{settings.APP_URL}/auth/verify-email?token={token}"
    resend.Emails.send({
        "from": settings.SMTP_FROM,
        "to": to,
        "subject": "Подтверждение email — Jane Marathon",
        "html": f"""
        <h2>Подтверждение email</h2>
        <p>Нажмите на кнопку чтобы подтвердить адрес:</p>
        <a href="{link}" style="background:#4CAF50;color:white;padding:12px 24px;
           text-decoration:none;border-radius:4px;display:inline-block;">
            Подтвердить email
        </a>
        <p>Ссылка действует 24 часа.</p>
        """,
    })


async def send_reset_password_email(to: str, token: str) -> None:
    link = f"{settings.APP_URL}/auth/reset-password?token={token}"
    resend.Emails.send({
        "from": settings.SMTP_FROM,
        "to": to,
        "subject": "Сброс пароля — Jane Marathon",
        "html": f"""
        <h2>Сброс пароля</h2>
        <p>Нажмите на кнопку чтобы сбросить пароль:</p>
        <a href="{link}" style="background:#2196F3;color:white;padding:12px 24px;
           text-decoration:none;border-radius:4px;display:inline-block;">
            Сбросить пароль
        </a>
        <p>Ссылка действует 15 минут.</p>
        """,
    })