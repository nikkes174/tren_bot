from aiogram.utils.keyboard import InlineKeyboardBuilder


def first_start_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="️‍️‍️‍️‍️‍️‍️‍🏋️‍♂🥩️Персональный план тренировок и питания 2000 Руб🥩🏋️‍♂️",
        callback_data="training_programs"
    )
    builder.button(
        text="📊Онлайн ведение📊"
             "5000 Руб/месяц",
        url="https://t.me/abvgdeikin"
    )
    builder.button(
        text="🦾Разовая консультация🦾"
             "500 Руб",
        url="https://t.me/abvgdeikin"
    )
    builder.button(
        text="ℹ️Информация по разделамℹ️"
             ,
        callback_data="the_info"
    )

    builder.adjust(1, 1)
    return builder.as_markup()


def training_period():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Тренировочный план📈",
        callback_data="one_mouth"
    )
    builder.button(
        text="Расчет КБЖУ🥕",
        callback_data="calculation_kal"
    )
    builder.button(
        text="Назад 🔙️",
        callback_data="back_to_menu"
    )
    builder.adjust(1, 1)
    return builder.as_markup()


def choice_gender():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="️‍️‍️‍️‍️‍️‍️‍Мужской 🥷🏻",
        callback_data="the_man"
    )
    builder.button(
        text="Женский 🧚🏻",
        callback_data="the_woman"
    )
    builder.button(
        text="Назад 🔙️",
        callback_data="back_to_menu"
    )
    builder.adjust(1, 1)
    return builder.as_markup()


def to_back():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Назад 🔙️",
        callback_data="back_to_menu"
    )
    builder.adjust(1, 1)
    return builder.as_markup()


def online():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Назад 🔙️",
        callback_data="back_to_menu"
    )
    builder.adjust(1, 1)
    return builder.as_markup()


def activity_level():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🛋️ Минимальная",
        callback_data="low_activity"
    )
    builder.button(
        text="🚶 Средняя",
        callback_data="moderate_activity"
    )
    builder.button(
        text="🏃 Высокая",
        callback_data="high_activity"
    )
    builder.adjust(1)  # Размещаем кнопки в одном столбце
    return builder.as_markup()


def choice_goal():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🏋️‍♂️ Набор массы",
        callback_data="mass_gain"
    )
    builder.button(
        text="⚖️ Похудение",
        callback_data="weight_loss"
    )
    builder.button(
        text="🤸 Поддержание формы",
        callback_data="support"
    )
    builder.adjust(1)
    return builder.as_markup()


def gender_for_trening():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="️‍️‍️‍️‍️‍️‍️‍Мужской 🥷🏻",
        callback_data="the_man_tranning"
    )
    builder.button(
        text="Женский 🧚🏻",
        callback_data="the_woman_trenning"
    )
    builder.button(
        text="Назад 🔙️",
        callback_data="back_to_menu"
    )
    builder.adjust(1, 1)
    return builder.as_markup()


def level_trening_wooman():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="️‍️‍️‍️‍️‍️‍️‍Продвинутый💪",
        callback_data="hard_level_w"
    )
    builder.button(
        text="Новичок👶",
        callback_data="easy_level_w"
    )
    builder.button(
        text="Назад 🔙️",
        callback_data="back_to_menu"
    )
    builder.adjust(1, 1)
    return builder.as_markup()


def level_trening_mans():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="️‍️‍️‍️‍️‍️‍️‍Продвинутый💪",
        callback_data="hard_level_m"
    )
    builder.button(
        text="Новичок👶",
        callback_data="easy_level_m"
    )
    builder.button(
        text="Назад 🔙️",
        callback_data="back_to_menu"
    )
    builder.adjust(1, 1)
    return builder.as_markup()


def payment_start(payment_url=None):
    """Создает inline-клавиатуру с кнопкой оплаты"""
    builder = InlineKeyboardBuilder()

    if payment_url:
        builder.button(
            text="💳 Перейти к оплате",
            url=payment_url  # Если передана ссылка, делаем кнопку-ссылку
        )
    else:
        builder.button(
            text="💳 Оплатить",
            callback_data="start_payment"
        )

    builder.adjust(1, 1)
    return builder.as_markup()