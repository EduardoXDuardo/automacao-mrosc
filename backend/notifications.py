import os
import requests
from backend.config import logger

class Notifier:
    @staticmethod
    def send_telegram_message(message: str) -> bool:
        """
        Envia uma mensagem via Telegram se o bot token e chat ID estiverem configurados.
        """
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not token or not chat_id:
            logger.info("Credenciais do Telegram não configuradas no .env. Notificação ignorada.")
            return False
            
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Notificação enviada com sucesso no Telegram.")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar notificação no Telegram: {e}")
            return False
