import asyncio

from aiogram import Router, F, Dispatcher
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, types
from aiogram.types import CallbackQuery
from yookassa import Configuration, Payment


import os
import random

from tgbot.database import check_date_tranning, add_date_tranning
from tgbot.database import check_payment
from .admin import is_admin
from .payment import create_payment, check_payment_loop
from tgbot.keyboards.inline import choice_gender, activity_level, to_back, first_start_keyboard, \
    training_period, choice_goal, gender_for_trening, level_trening_wooman, level_trening_mans, payment_start





TOKEN = "6535006519:AAEn_TXF3aGQ8oTlm629D4MLL3fybRAnGnQ"
YOOKASSA_SHOP_ID = "1032008"
YOOKASSA_SECRET = "live_CEqPQ1lwbzMqCs-61XbxCeYvrqczpNzmMVQU5o3hXO8"
Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET
user_router = Router()
dp = Dispatcher()
allowed_extensions = {".docx"}
user_payments = {}
user_access = {}
USER_ACCESS_FILE = "user_access.json"
storage = MemoryStorage()


class UserData(StatesGroup):
    gender = State()
    age = State()
    weight = State()
    height = State()
    activity = State()
    goal = State()
    waiting_for_email = State()

@user_router.message(CommandStart())
async def user_start(message : Message):
    try:
        await message.delete()
    except Exception as e:
        print(f"⚠️ Ошибка удаления сообщения: {e}")
    await message.answer(
        f"""🏋️‍♂️Привет! Рад, что ты здесь!🏋️‍♂️

    Значит твоя цель — превратить твои мечты о теле, здоровье и энергии в реальные достижения. 
    Мой бот построит не просто план, а целый стиль жизни, который будет работать на тебя.
    Все подробности во вкладке ℹ️Информация по разделамℹ️

    P.S. и еще больше полезного контента в каналах 👇🏻
    IG : @smngrsmv_fit
    TG : https://t.me/smngrsmv
    """,
        reply_markup=first_start_keyboard()
    )




@user_router.callback_query(F.data == "training_programs")
async def training_programs_handler(callback_query: CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id

    # 🗑️ Пытаемся удалить предыдущее сообщение (если есть)
    try:
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    except Exception as e:
        print(f"⚠️ Ошибка удаления сообщения: {e}")

    # ✅ Если админ или у пользователя есть подписка — даем доступ
    if is_admin(user_id) or check_payment(user_id):
        await bot.send_message(
            user_id,
            "✅ У вас уже есть доступ! Вот ваша тренировочная программа:",
            reply_markup=training_period()
        )
        return  # Выходим из обработчика

    # 💳 Если нет подписки — предлагаем оплату
    amount = 1  # Фиксированная сумма (1 рубль)
    payment_id, payment_url = create_payment(amount)

    await bot.send_message(
        user_id,
        f"❗ У вас нет активной подписки.",
        reply_markup=payment_start(payment_url)
    )

    # 🔄 Запускаем проверку платежа в фоне
    asyncio.create_task(check_payment_loop(payment_id, user_id, bot))


@user_router.callback_query(F.data == "back_to_menu")
async def take_menu(call: CallbackQuery):
    try:
        await call.message.edit_text(
            text="Какой раздел вас интересует?",
            reply_markup=first_start_keyboard()
        )
    except Exception as e:
        print(f"⚠️ Ошибка редактирования сообщения: {e}")

@user_router.callback_query(F.data == "calculation_kal")
async def ask_gender(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text="Укажите ваш пол 🥷🏻/🧚🏻",
        reply_markup=choice_gender()
    )


# Выбор пола
@user_router.callback_query(F.data.in_(["the_man", "the_woman"]))
async def ask_age(call: CallbackQuery, state: FSMContext):
    gender = "Мужской" if call.data == "the_man" else "Женский"
    print(f"Пользователь выбрал пол: {gender}")

    await state.update_data(gender=gender)
    await state.set_state(UserData.age)

    # ✅ Удаляем предыдущее сообщение (если возможно)
    try:
        await call.message.delete()
    except Exception as e:
        print(f"⚠️ Ошибка удаления сообщения: {e}")

    # ✅ Отправляем новое сообщение с запросом возраста
    new_message = await call.message.answer("Введите ваш возраст (лет):")

    # ✅ Получаем старый ID сообщения (если есть) и удаляем
    data = await state.get_data()
    last_message_id = data.get("last_message_id")

    if last_message_id:
        try:
            await call.message.bot.delete_message(chat_id=call.message.chat.id, message_id=last_message_id)
        except Exception as e:
            print(f"⚠️ Ошибка удаления предыдущего сообщения: {e}")

    # ✅ Сохраняем новый ID сообщения в состоянии
    await state.update_data(last_message_id=new_message.message_id)


# Ввод возраста
@user_router.message(UserData.age)
async def ask_weight(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 10 or age > 100:
            raise ValueError("Возраст вне допустимого диапазона.")
        await state.update_data(age=age)
        await state.set_state(UserData.weight)
        try:
            await message.delete()
        except Exception as e:
            print(f"⚠️ Ошибка удаления сообщения: {e}")
        await message.answer("Введите ваш вес (в кг):")
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректный возраст числом (10-100 лет).")


@user_router.message(UserData.weight)
async def ask_height(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        if weight < 30 or weight > 300:
            raise ValueError("Вес вне допустимого диапазона.")

        # ✅ Обновляем данные состояния
        await state.update_data(weight=weight)
        await state.set_state(UserData.height)

        # ✅ Отправляем новое сообщение с запросом роста
        new_message = await message.answer("Введите ваш рост (в см):")

        # ✅ Получаем сохраненные данные состояния
        data = await state.get_data()
        last_message_id = data.get("last_message_id")

        # ✅ Удаляем предыдущее сообщение с этим же вопросом
        if last_message_id:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=last_message_id)
            except Exception as e:
                print(f"⚠️ Ошибка удаления предыдущего сообщения: {e}")

        # ✅ Сохраняем ID нового сообщения, чтобы удалить его при следующем вводе
        await state.update_data(last_message_id=new_message.message_id)

    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректный вес числом (30-300 кг).")



# Ввод роста
@user_router.message(UserData.height)
async def ask_goal(message: Message, state: FSMContext):
    try:
        height = float(message.text)
        if height < 100 or height > 250:
            raise ValueError("Рост вне допустимого диапазона.")

        await state.update_data(height=height)
        await state.set_state(UserData.goal)

        # ✅ Отправляем новое сообщение с выбором цели
        new_message = await message.answer(
            "Какая ваша цель? 🎯",
            reply_markup=choice_goal()
        )

        # ✅ Получаем сохраненный ID последнего сообщения (если оно есть)
        data = await state.get_data()
        last_message_id = data.get("last_message_id")

        # ✅ Удаляем предыдущее сообщение с этим же вопросом
        if last_message_id:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=last_message_id)
            except Exception as e:
                print(f"⚠️ Ошибка удаления предыдущего сообщения: {e}")

        # ✅ Сохраняем новый ID сообщения, чтобы удалить его при новом вводе
        await state.update_data(last_message_id=new_message.message_id)

    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректный рост числом (100-250 см).")


@user_router.callback_query(UserData.goal)
async def ask_activity(call: CallbackQuery, state: FSMContext):
    goal = call.data
    await state.update_data(goal=goal)
    await state.set_state(UserData.activity)
    try:
        await call.message.delete()
    except Exception as e:
        print(f"⚠️ Ошибка удаления сообщения: {e}")
    await call.message.answer(
        "Выберите ваш уровень физической активности:",
        reply_markup=activity_level()
    )


@user_router.callback_query(UserData.activity)
async def calculate_bju(call: CallbackQuery, state: FSMContext):
    activity_levels = {
        "low_activity": 1.2,
        "moderate_activity": 1.375,
        "high_activity": 1.55
    }
    activity = activity_levels.get(call.data)
    if not activity:
        await call.message.answer("❌ Выберите корректный уровень активности.")
        return
    await state.update_data(activity=activity)
    data = await state.get_data()
    gender = data["gender"]
    age = data["age"]
    weight = data["weight"]
    height = data["height"]
    goal = data["goal"]
    if gender == "Мужской":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    elif gender == "Женский":
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        await call.message.answer("❌ Ошибка: пол не указан.")
        return
    total_calories = bmr * activity
    if goal == "mass_gain":
        total_calories += 500
    elif goal == "weight_loss":
        total_calories -= 500
    proteins = round(total_calories * 0.3 / 4, 1)
    fats = round(total_calories * 0.3 / 9, 1)
    carbs = round(total_calories * 0.4 / 4, 1)
    try:
        await call.message.delete()
    except Exception as e:
        print(f"⚠️ Ошибка удаления сообщения: {e}")
    await call.message.answer(
        f"📊 *Ваши расчеты:*\n"
        f"🎯 Цель: {'Набор массы' if goal == 'mass_gain' else 'Похудение' if goal == 'weight_loss' else 'Поддержание формы'}\n"
        f"🔥 *Калории*: {round(total_calories)} ккал\n"
        f"🍗 *Белки*: {proteins} г\n"
        f"🥑 *Жиры*: {fats} г\n"
        f"🍞 *Углеводы*: {carbs} г\n",
        reply_markup=to_back(),
        parse_mode="Markdown"
    )
    await state.clear()


@user_router.callback_query(F.data == "the_info")
async def take_menu(call: CallbackQuery):
    # ✅ Удаляем предыдущее сообщение
    try:
        await call.message.delete()
    except Exception as e:
        print(f"⚠️ Ошибка удаления сообщения: {e}")  # Игнорируем ошибки

    # ✅ Отправляем новое сообщение с информацией
    await call.message.answer(
        f"✅ *ОНЛАЙН ВЕДЕНИЕ:*\n"
        f"📌 *Составление тренировочного плана*\n"
        f"📌 *Рекомендации по питанию (КБЖУ)*\n"
        f"📌 *Консультация по спортивным добавкам*\n"
        f"📌 *Постановка техники выполнения упражнений*\n"
        f"📌 *Консультации* (переписка, аудио/видео звонки)\n\n"
        f"✅ *Персональный план тренировок и питания:*\n"
        f"📌 *Индивидуальный подсчет КБЖУ под ваши цели*\n"
        f"📌 *Тренировочный сплит под ваш уровень подготовки*\n\n"
        f"⚠️ *Срок пользования*: 1 месяц с момента оплаты.\n"      
        f"❗️❗️ *Тренировочный сплит выдается 1 раз в месяц*❗️❗\n"
        f"⚠️ *Далее раздел блокируется*\n"
        f"📌 *При повторной покупке вы получаете новый план.*",
        reply_markup=to_back(),
        parse_mode="Markdown"
    )


@user_router.callback_query(F.data == "one_mouth")
async def take_men(call: CallbackQuery):
    user_id = call.from_user.id


    if not check_date_tranning(user_id):
        await call.message.answer("❌ Вы уже использовали этот раздел в этом месяце. Попробуйте позже.")
        return


    add_date_tranning(user_id)

    # ✅ Отправляем меню
    await call.message.edit_text(
        text="Укажите ваш пол",
        reply_markup=gender_for_trening()
    )


@user_router.callback_query(F.data == "the_man_tranning")
async def take_menu(call: CallbackQuery):
    await call.message.edit_text(text="""Какой у вас уровень тренированности?"""
                                 , reply_markup=level_trening_mans())


@user_router.callback_query(F.data == "the_woman_trenning")
async def take_menu(call: CallbackQuery):
    await call.message.edit_text(text="""Какой у вас уровень тренированности?"""
                                 , reply_markup=level_trening_wooman())





@user_router.callback_query(F.data == "hard_level_m")
async def get_program(callback_query: CallbackQuery, bot: Bot):
    # Жесткий путь к папке (для теста)
    PLANS_DIRECTORY = "/root/bot/Files/man/senior"

    # Отладка
    print(f"🔍 Проверка пути: {PLANS_DIRECTORY}")
    print(f"🔍 Существует ли папка? {os.path.exists(PLANS_DIRECTORY)}")

    try:
        if not os.path.exists(PLANS_DIRECTORY):
            print(f"❌ Ошибка: Папка {PLANS_DIRECTORY} не существует!")
            await bot.answer_callback_query(callback_query.id, text="Ошибка: Папка с файлами не найдена.")
            return

        files = [f for f in os.listdir(PLANS_DIRECTORY) if f.endswith('.txt')]
        if not files:
            await bot.answer_callback_query(callback_query.id, text="В папке нет доступных файлов.")
            return

        random_file = random.choice(files)
        file_path = os.path.join(PLANS_DIRECTORY, random_file)

        print(f"📂 Файл для отправки: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        await bot.send_message(callback_query.from_user.id, file_content)
        await bot.answer_callback_query(callback_query.id, text="Ваш тренировочный план!")

    except Exception as e:
        print(f"❌ Ошибка при отправке файла: {str(e)}")
        await bot.answer_callback_query(callback_query.id, text=f"Произошла ошибка: {str(e)}")



@user_router.callback_query(F.data == "easy_level_m")
async def get_program(callback_query: CallbackQuery, bot: Bot):
    # Жесткий путь к папке (для теста)
    PLANS_DIRECTORY = "/root/bot/Files/man/jun"

    # Отладка
    print(f"🔍 Проверка пути: {PLANS_DIRECTORY}")
    print(f"🔍 Существует ли папка? {os.path.exists(PLANS_DIRECTORY)}")

    try:
        if not os.path.exists(PLANS_DIRECTORY):
            print(f"❌ Ошибка: Папка {PLANS_DIRECTORY} не существует!")
            await bot.answer_callback_query(callback_query.id, text="Ошибка: Папка с файлами не найдена.")
            return

        files = [f for f in os.listdir(PLANS_DIRECTORY) if f.endswith('.txt')]
        if not files:
            await bot.answer_callback_query(callback_query.id, text="В папке нет доступных файлов.")
            return

        random_file = random.choice(files)
        file_path = os.path.join(PLANS_DIRECTORY, random_file)

        print(f"📂 Файл для отправки: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        await bot.send_message(callback_query.from_user.id, file_content)
        await bot.answer_callback_query(callback_query.id, text="Ваш тренировочный план!")

    except Exception as e:
        print(f"❌ Ошибка при отправке файла: {str(e)}")
        await bot.answer_callback_query(callback_query.id, text=f"Произошла ошибка: {str(e)}")

@user_router.callback_query(F.data == "hard_level_w")
async def get_program(callback_query: CallbackQuery, bot: Bot):
    # Жесткий путь к папке (для теста)
    PLANS_DIRECTORY = "/root/bot/Files/wooman/senior"

    # Отладка
    print(f"🔍 Проверка пути: {PLANS_DIRECTORY}")
    print(f"🔍 Существует ли папка? {os.path.exists(PLANS_DIRECTORY)}")

    try:
        if not os.path.exists(PLANS_DIRECTORY):
            print(f"❌ Ошибка: Папка {PLANS_DIRECTORY} не существует!")
            await bot.answer_callback_query(callback_query.id, text="Ошибка: Папка с файлами не найдена.")
            return

        files = [f for f in os.listdir(PLANS_DIRECTORY) if f.endswith('.txt')]
        if not files:
            await bot.answer_callback_query(callback_query.id, text="В папке нет доступных файлов.")
            return

        random_file = random.choice(files)
        file_path = os.path.join(PLANS_DIRECTORY, random_file)

        print(f"📂 Файл для отправки: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        await bot.send_message(callback_query.from_user.id, file_content)
        await bot.answer_callback_query(callback_query.id, text="Ваш тренировочный план!")

    except Exception as e:
        print(f"❌ Ошибка при отправке файла: {str(e)}")
        await bot.answer_callback_query(callback_query.id, text=f"Произошла ошибка: {str(e)}")


@user_router.callback_query(F.data == "easy_level_w")
async def get_program(callback_query: CallbackQuery, bot: Bot):
    # Жесткий путь к папке (для теста)
    PLANS_DIRECTORY = "/root/bot/Files/wooman/jun"
    # Отладка
    print(f"🔍 Проверка пути: {PLANS_DIRECTORY}")
    print(f"🔍 Существует ли папка? {os.path.exists(PLANS_DIRECTORY)}")
    try:
        if not os.path.exists(PLANS_DIRECTORY):
            print(f"❌ Ошибка: Папка {PLANS_DIRECTORY} не существует!")
            await bot.answer_callback_query(callback_query.id, text="Ошибка: Папка с файлами не найдена.")
            return
        files = [f for f in os.listdir(PLANS_DIRECTORY) if f.endswith('.txt')]
        if not files:
            await bot.answer_callback_query(callback_query.id, text="В папке нет доступных файлов.")
            return
        random_file = random.choice(files)
        file_path = os.path.join(PLANS_DIRECTORY, random_file)
        print(f"📂 Файл для отправки: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
        await bot.send_message(callback_query.from_user.id, file_content)
        await bot.answer_callback_query(callback_query.id, text="Ваш тренировочный план!")
    except Exception as e:
        print(f"❌ Ошибка при отправке файла: {str(e)}")
        await bot.answer_callback_query(callback_query.id, text=f"Произошла ошибка: {str(e)}")











