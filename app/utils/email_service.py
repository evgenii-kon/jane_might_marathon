import resend
from app.config import settings

resend.api_key = settings.RESEND_API_KEY


async def send_verification_email(to: str, token: str) -> None:
    link = f"{settings.APP_URL}/auth/verify-email?token={token}"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="margin:0;padding:0;background:#f5f5f5;font-family:Arial,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5;padding:40px 0;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                        
                        <!-- Шапка -->
                        <tr>
                            <td style="background:#1a1a2e;padding:32px;text-align:center;">
                                <img src="https://school-might-marathon.ru/static/images/orange_logo.png" 
                                     alt="Jane Marathon" height="50" style="display:block;margin:0 auto;">
                            </td>
                        </tr>
                        
                        <!-- Контент -->
                        <tr>
                            <td style="padding:40px 48px;">
                                <h1 style="margin:0 0 16px;color:#1a1a2e;font-size:24px;">Подтвердите email</h1>
                                <p style="margin:0 0 24px;color:#666;font-size:16px;line-height:1.6;">
                                    Спасибо за регистрацию в Jane Marathon! Нажмите кнопку ниже чтобы подтвердить ваш адрес и начать обучение.
                                </p>
                                <table cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td style="border-radius:8px;background:#ff6b35;">
                                            <a href="{link}" 
                                               style="display:inline-block;padding:14px 32px;color:#ffffff;text-decoration:none;font-size:16px;font-weight:bold;">
                                                Подтвердить email →
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                <p style="margin:24px 0 0;color:#999;font-size:14px;">
                                    Ссылка действует 24 часа. Если вы не регистрировались — проигнорируйте письмо.
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Подвал -->
                        <tr>
                            <td style="background:#f9f9f9;padding:24px 48px;border-top:1px solid #eee;">
                                <p style="margin:0;color:#999;font-size:12px;text-align:center;">
                                    © 2023 Jane Marathon · <a href="https://school-might-marathon.ru" style="color:#ff6b35;">school-might-marathon.ru</a>
                                </p>
                            </td>
                        </tr>
                        
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    resend.Emails.send({
        "from": settings.EMAIL_FROM,
        "to": to,
        "subject": "Подтвердите email — Jane Marathon",
        "html": html,
    })


async def send_reset_password_email(to: str, token: str) -> None:
    link = f"{settings.APP_URL}/auth/reset-password?token={token}"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="margin:0;padding:0;background:#f5f5f5;font-family:Arial,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5;padding:40px 0;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                        
                        <!-- Шапка -->
                        <tr>
                            <td style="background:#1a1a2e;padding:32px;text-align:center;">
                                <img src="https://school-might-marathon.ru/static/images/orange_logo.png" 
                                     alt="Jane Marathon" height="50" style="display:block;margin:0 auto;">
                            </td>
                        </tr>
                        
                        <!-- Контент -->
                        <tr>
                            <td style="padding:40px 48px;">
                                <h1 style="margin:0 0 16px;color:#1a1a2e;font-size:24px;">Сброс пароля</h1>
                                <p style="margin:0 0 24px;color:#666;font-size:16px;line-height:1.6;">
                                    Мы получили запрос на сброс пароля для вашего аккаунта. Нажмите кнопку ниже чтобы задать новый пароль.
                                </p>
                                <table cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td style="border-radius:8px;background:#ff6b35;">
                                            <a href="{link}" 
                                               style="display:inline-block;padding:14px 32px;color:#ffffff;text-decoration:none;font-size:16px;font-weight:bold;">
                                                Сбросить пароль →
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                <p style="margin:24px 0 0;color:#999;font-size:14px;">
                                    Ссылка действует 15 минут. Если вы не запрашивали сброс — проигнорируйте письмо.
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Подвал -->
                        <tr>
                            <td style="background:#f9f9f9;padding:24px 48px;border-top:1px solid #eee;">
                                <p style="margin:0;color:#999;font-size:12px;text-align:center;">
                                    © 2023 Jane Marathon · <a href="https://school-might-marathon.ru" style="color:#ff6b35;">school-might-marathon.ru</a>
                                </p>
                            </td>
                        </tr>
                        
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    resend.Emails.send({
        "from": settings.EMAIL_FROM,
        "to": to,
        "subject": "Сброс пароля — Jane Marathon",
        "html": html,
    })