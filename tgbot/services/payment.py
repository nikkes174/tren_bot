import os
import asyncio
import logging
from typing import Optional, Tuple

from dotenv import load_dotenv
from yookassa import Configuration, Payment

from tgbot.keyboards.inline import training_period
from tgbot.database import add_payment

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

load_dotenv()


class PaymentService:
    """Сервис для работы с YooKassa API."""

    def __init__(self):
        self.shop_id = os.getenv("YOOKASSA_SHOP_ID")
        self.secret_key = os.getenv("YOOKASSA_SECRET_KEY")
        self.return_url = os.getenv("YOOKASSA_RETURN_URL", "https://t.me/yourbot")

        Configuration.account_id = self.shop_id
        Configuration.secret_key = self.secret_key

    def create_payment(self, amount: float, description: str, email: str = "user@example.com") -> Tuple[str, str]:
        """
        Создаёт платёж в YooKassa.
        :param amount: сумма платежа
        :param description: описание
        :param email: email клиента
        :return: (payment_id, confirmation_url)
        """
        try:
            payment = Payment.create({
                "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
                "confirmation": {"type": "redirect", "return_url": self.return_url},
                "capture": True,
                "description": description,
                "receipt": {
                    "customer": {"email": email},
                    "items": [{
                        "description": description,
                        "quantity": 1,
                        "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
                        "vat_code": 1,
                        "payment_mode": "full_prepayment",
                        "payment_subject": "service",
                    }],
                }
            })
            logging.info("💳 Создан платёж: %s (%s ₽)", payment.id, amount)
            return payment.id, payment.confirmation.confirmation_url
        except Exception as e:
            logging.error("❌ Ошибка при создании платежа: %s", e)
            raise

    def check_payment_status(self, payment_id: str) -> Optional[str]:
        """Проверяет статус платежа."""
        try:
            payment = Payment.find_one(payment_id)
            return payment.status
        except Exception as e:
            logging.error("❌ Ошибка при проверке платежа %s: %s", payment_id, e)
            return None

    async def check_payment_loop(self, payment_id: str, user_id: int, bot, timeout: int = 300) -> None:
        """
        Асинхронный цикл проверки оплаты (до 5 минут).
        :param payment_id: ID платежа
        :param user_id: Telegram ID пользователя
        :param bot: экземпляр бота
        :param timeout: сколько секунд проверять (по умолчанию 300)
        """
        logging.info("⏳ Запущена проверка платежа: %s", payment_id)

        for _ in range(timeout // 30):  # каждые 30 сек, пока не выйдет время
            await asyncio.sleep(30)
            status = self.check_payment_status(payment_id)

            if status == "succeeded":
                add_payment(user_id)
                await bot.send_message(
                    user_id,
                    "✅ Оплата прошла успешно! Вам открыт доступ к тренировочным программам.",
                    reply_markup=training_period()
                )
                logging.info("✅ Платёж %s прошёл успешно (user_id=%s)", payment_id, user_id)
                return

            elif status == "canceled":
                await bot.send_message(user_id, "❌ Оплата отменена. Попробуйте снова.")
                logging.warning("❌ Платёж %s отменён (user_id=%s)", payment_id, user_id)
                return

        await bot.send_message(user_id, "⌛ Оплата не найдена или ещё обрабатывается. Проверьте позже.")
        logging.warning("⌛ Платёж %s не подтвердился за %s секунд", payment_id, timeout)
