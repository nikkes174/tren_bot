import os
from yookassa import Configuration, Payment
from dotenv import load_dotenv
import asyncio

from tgbot.keyboards.inline import training_period
from tgbot.database import add_payment

load_dotenv()

TOKEN = os.getenv("TOKEN")
YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")
YOOKASSA_RETURN_URL = os.getenv("YOOKASSA_RETURN_URL")
Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY


def create_payment(amount):
    payment = Payment.create({
        "amount": {
            "value": 2000.00,
            "currency": "RUB"

        },
        "confirmation": {
            "type": "redirect",
            "return_url": ""
        },
        "capture": True,
        "description": "Оплата тренировки",
        "receipt": {
            "customer": {
                "email": "user@example.com"
            },
            "items": [
                {
                    "description": "Тренировочная программа",
                    "quantity": 1,
                    "amount": {
                        "value": 2000.00,
                        "currency": "RUB"
                    },
                    "vat_code": 1,
                    "payment_mode": "full_prepayment",
                    "payment_subject": "service"
                }
            ]
        }
    })

    return payment.id, payment.confirmation.confirmation_url

def check_payment_status(payment_id):
    try:
        payment = Payment.find_one(payment_id)
        return payment.status
    except Exception as e:
        print(f"Ошибка при проверке платежа: {e}")


async def check_payment_loop(payment_id, user_id, bot):
    """Фоновая проверка оплаты (ждет до 5 минут)"""
    for _ in range(10):
        await asyncio.sleep(30)
        status = check_payment_status(payment_id)
        if status == "succeeded":
            add_payment(user_id)

            await bot.send_message(
                user_id,
                "✅ Оплата прошла успешно! Вам открыт доступ к тренировочным программам.",
                reply_markup=training_period()
            )
            return
        elif status == "canceled":
            await bot.send_message(
                user_id,
                "❌ Оплата отменена. Попробуйте снова."
            )
            return
    await bot.send_message(
        user_id,
        "⌛ Оплата не найдена или еще обрабатывается. Проверьте позже."
    )
