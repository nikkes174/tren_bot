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
            "value": "1.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/nikkestelegrambot"  # Измените на ваш URL
        },
        "capture": True,
        "description": "Оплата тренировки",
        # Добавляем корректный receipt
        "receipt": {
            "customer": {
                "email": "user@example.com"  # Должен быть корректный email покупателя
            },
            "items": [
                {
                    "description": "Тренировочная программа",
                    "quantity": "1.00",
                    "amount": {
                        "value": "1.00",
                        "currency": "RUB"
                    },
                    "vat_code": "1",  # Код НДС (1 – без НДС, 2 – 10%, 3 – 20% и т. д.)
                    "payment_mode": "full_prepayment",  # Полная предоплата
                    "payment_subject": "service"  # Тип платежа (услуга)
                }
            ]
        }
    })

    return payment.id, payment.confirmation.confirmation_url

def check_payment_status(payment_id):
    try:
        payment = Payment.find_one(payment_id)  # ✅ Используем правильный метод
        return payment.status  # Возможные статусы: "pending", "succeeded", "canceled"
    except Exception as e:
        print(f"Ошибка при проверке платежа: {e}")


async def check_payment_loop(payment_id, user_id, bot):
    """Фоновая проверка оплаты (ждет до 5 минут)"""
    for _ in range(10):  # Проверяем платеж 10 раз (по 30 сек = 5 минут)
        await asyncio.sleep(30)  # ⏳ Ждем 30 секунд перед проверкой
        status = check_payment_status(payment_id)

        if status == "succeeded":
            add_payment(user_id)  # ✅ Сохраняем подписку в БД

            await bot.send_message(
                user_id,
                "✅ Оплата прошла успешно! Вам открыт доступ к тренировочным программам.",
                reply_markup=training_period()  # ✅ Отправляем меню с программами
            )
            return  # 🚀 Выходим из функции после успешной оплаты

        elif status == "canceled":
            await bot.send_message(
                user_id,
                "❌ Оплата отменена. Попробуйте снова."
            )
            return  # Выходим из функции, если платеж отменен

    # Если после 5 минут платеж не найден
    await bot.send_message(
        user_id,
        "⌛ Оплата не найдена или еще обрабатывается. Проверьте позже."
    )
