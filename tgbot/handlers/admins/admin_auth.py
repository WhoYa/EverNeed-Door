# tgbot/handlers/admins/admin_auth.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from infrastructure.database.repositories.requests import RequestsRepo
from infrastructure.database.repositories.users import UsersRepo
from infrastructure.database.repositories.logs import LogsRepo
from tgbot.config import Config
from tgbot.keyboards.admin_main_menu import admin_back_button
from tgbot.filters.admin import AdminFilter

# Состояния для авторизации и управления администраторами
class AdminAuth(StatesGroup):
    waiting_for_password = State()  # Ожидание пароля для авторизации
    adding_admin = State()  # Добавление нового администратора
    waiting_for_admin_id = State()  # Ожидание ID нового администратора
    waiting_for_admin_role = State()  # Ожидание роли нового администратора
    removing_admin = State()  # Удаление администратора
    waiting_for_admin_id_to_remove = State()  # Ожидание ID удаляемого администратора
    confirm_remove_admin = State()  # Подтверждение удаления администратора

admin_auth_router = Router()

# Клавиатура меню управления администраторами
def admin_management_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="➕ Добавить администратора", callback_data="add_admin"),
        InlineKeyboardButton(text="➖ Удалить администратора", callback_data="remove_admin"),
        InlineKeyboardButton(text="👥 Список администраторов", callback_data="list_admins"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main")
    )
    builder.adjust(1)
    return builder.as_markup()

# Клавиатура выбора роли для администратора
def admin_role_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="👨‍💼 Администратор", callback_data="role_admin"),
        InlineKeyboardButton(text="👨‍💻 Менеджер", callback_data="role_manager"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="manage_admins")
    )
    builder.adjust(1)
    return builder.as_markup()

# Обработчик команды /admin для доступа к панели администратора
@admin_auth_router.message(Command("admin"))
async def admin_command(message: Message, state: FSMContext, config: Config):
    """
    Обрабатывает команду /admin - точка входа в админ-панель.
    Проверяет, является ли пользователь администратором, или запрашивает пароль.
    """
    user_id = message.from_user.id
    
    # Проверяем, есть ли пользователь в списке администраторов из конфига
    if user_id in config.tg_bot.admin_ids:
        await message.answer(
            "Вы уже являетесь администратором.\n"
            "Переход в панель администратора...",
        )
        # Переход в панель администратора
        await admin_panel(message)
    else:
        # Запрашиваем пароль для авторизации
        await state.set_state(AdminAuth.waiting_for_password)
        await message.answer(
            "Введите пароль администратора:",
        )

# Обработчик ввода пароля администратора
@admin_auth_router.message(AdminAuth.waiting_for_password)
async def process_admin_password(message: Message, state: FSMContext, config: Config, request: RequestsRepo):
    """
    Проверяет пароль администратора и предоставляет доступ, если пароль верный.
    """
    password = message.text.strip()
    
    # Проверка пароля (в реальном проекте используйте безопасное хранение и проверку)
    if password == config.tg_bot.admin_password:
        user_id = message.from_user.id
        
        # Добавляем пользователя как администратора в базу данных
        users_repo = request.users
        user = await users_repo.get_user_by_id(user_id)
        
        if user:
            # Обновляем роль пользователя
            await users_repo.update_field(user_id, "role", "admin")
        
        # Логируем действие
        logs_repo = request.logs
        await logs_repo.create_log(
            user_id=user_id,
            action="admin_authorized",
            details="Предоставлен доступ к панели администратора"
        )
        
        await state.clear()
        await message.answer(
            "Пароль принят! Вы получили доступ к панели администратора."
        )
        
        # Переход в панель администратора
        await admin_panel(message)
    else:
        await message.answer(
            "Неверный пароль. Попробуйте еще раз или отмените операцию командой /cancel"
        )

# Отображение панели администратора
async def admin_panel(message: Message):
    """
    Показывает панель администратора с доступными действиями.
    """
    from tgbot.keyboards.admin_main_menu import main_menu_keyboard
    
    await message.answer(
        "Панель администратора\n\n"
        "Выберите действие из меню ниже:",
        reply_markup=main_menu_keyboard()
    )

# Обработчик кнопки "Управление администраторами"
@admin_auth_router.callback_query(F.data == "manage_admins")
async def manage_admins_callback(callback: CallbackQuery):
    """
    Показывает меню управления администраторами.
    """
    await callback.message.edit_text(
        text="👨‍💼 <b>Управление администраторами</b>\n\n"
             "Выберите действие:",
        reply_markup=admin_management_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

# Обработчик кнопки "Добавить администратора"
@admin_auth_router.callback_query(F.data == "add_admin")
async def add_admin_callback(callback: CallbackQuery, state: FSMContext):
    """
    Начинает процесс добавления нового администратора.
    """
    await state.set_state(AdminAuth.waiting_for_admin_id)
    
    await callback.message.edit_text(
        text="👨‍💼 <b>Добавление нового администратора</b>\n\n"
             "Введите Telegram ID пользователя, которого хотите сделать администратором:",
        reply_markup=admin_back_button("manage_admins"),
        parse_mode="HTML"
    )
    await callback.answer()

# Обработчик ввода ID нового администратора
@admin_auth_router.message(AdminAuth.waiting_for_admin_id)
async def process_admin_id(message: Message, state: FSMContext):
    """
    Обрабатывает ввод ID пользователя для добавления в администраторы.
    """
    try:
        admin_id = int(message.text.strip())
        
        # Сохраняем ID в состоянии
        await state.update_data(new_admin_id=admin_id)
        
        # Запрашиваем роль администратора
        await state.set_state(AdminAuth.waiting_for_admin_role)
        
        await message.answer(
            text="Выберите роль для нового администратора:",
            reply_markup=admin_role_keyboard()
        )
    except ValueError:
        await message.answer(
            text="Пожалуйста, введите корректный ID пользователя (только цифры).",
            reply_markup=admin_back_button("manage_admins")
        )

# Обработчик выбора роли администратора
@admin_auth_router.callback_query(AdminAuth.waiting_for_admin_role, F.data.startswith("role_"))
async def process_admin_role(callback: CallbackQuery, state: FSMContext, request: RequestsRepo):
    """
    Обрабатывает выбор роли для нового администратора.
    """
    # Получаем ID нового администратора из состояния
    user_data = await state.get_data()
    new_admin_id = user_data.get("new_admin_id")
    
    # Определяем выбранную роль
    role = callback.data.split("_")[1]  # "role_admin" -> "admin"
    
    # Получаем репозиторий пользователей
    users_repo = request.users
    
    # Проверяем, существует ли пользователь
    user = await users_repo.get_user_by_id(new_admin_id)
    
    if user:
        # Обновляем роль пользователя
        await users_repo.update_field(new_admin_id, "role", role)
        
        success_text = (
            f"✅ <b>Администратор успешно добавлен!</b>\n\n"
            f"ID: {new_admin_id}\n"
            f"Роль: {role.capitalize()}"
        )
    else:
        # Создаем нового пользователя с ролью администратора
        # В реальном случае это может не работать, так как может потребоваться 
        # больше данных для создания пользователя
        try:
            await users_repo.create({
                "user_id": new_admin_id,
                "role": role,
                "active": True
            })
            success_text = (
                f"✅ <b>Администратор успешно добавлен!</b>\n\n"
                f"ID: {new_admin_id}\n"
                f"Роль: {role.capitalize()}"
            )
        except Exception as e:
            success_text = (
                f"⚠️ <b>Ошибка при добавлении администратора</b>\n\n"
                f"Пользователь с ID {new_admin_id} не найден в базе данных.\n"
                f"Пользователь должен сначала запустить бота."
            )
    
    # Логируем действие
    logs_repo = request.logs
    await logs_repo.create_log(
        user_id=callback.from_user.id,
        action="add_admin",
        details=f"Добавлен администратор с ID {new_admin_id} и ролью {role}"
    )
    
    # Сбрасываем состояние и отправляем ответ
    await state.clear()
    
    await callback.message.edit_text(
        text=success_text,
        reply_markup=admin_back_button("manage_admins"),
        parse_mode="HTML"
    )
    await callback.answer()

# Обработчик кнопки "Удалить администратора"
@admin_auth_router.callback_query(F.data == "remove_admin")
async def remove_admin_callback(callback: CallbackQuery, state: FSMContext):
    """
    Начинает процесс удаления администратора.
    """
    await state.set_state(AdminAuth.waiting_for_admin_id_to_remove)
    
    await callback.message.edit_text(
        text="👨‍💼 <b>Удаление администратора</b>\n\n"
             "Введите Telegram ID администратора, которого хотите удалить:",
        reply_markup=admin_back_button("manage_admins"),
        parse_mode="HTML"
    )
    await callback.answer()

# Обработчик ввода ID администратора для удаления
@admin_auth_router.message(AdminAuth.waiting_for_admin_id_to_remove)
async def process_admin_id_to_remove(message: Message, state: FSMContext, request: RequestsRepo):
    """
    Обрабатывает ввод ID администратора для удаления.
    """
    try:
        admin_id = int(message.text.strip())
        
        # Получаем репозиторий пользователей
        users_repo = request.users
        
        # Проверяем, существует ли пользователь и является ли он администратором
        user = await users_repo.get_user_by_id(admin_id)
        
        if not user:
            await message.answer(
                text=f"Пользователь с ID {admin_id} не найден.",
                reply_markup=admin_back_button("manage_admins")
            )
            return
        
        if user.role not in ["admin", "manager"]:
            await message.answer(
                text=f"Пользователь с ID {admin_id} не является администратором или менеджером.",
                reply_markup=admin_back_button("manage_admins")
            )
            return
        
        # Сохраняем ID в состоянии
        await state.update_data(admin_id_to_remove=admin_id)
        
        # Запрашиваем подтверждение удаления
        await state.set_state(AdminAuth.confirm_remove_admin)
        
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton
        
        # Клавиатура для подтверждения
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_remove_{admin_id}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="manage_admins")
        )
        builder.adjust(1)
        
        await message.answer(
            text=f"⚠️ <b>Подтверждение удаления</b>\n\n"
                 f"Вы действительно хотите удалить администратора с ID {admin_id}?",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer(
            text="Пожалуйста, введите корректный ID пользователя (только цифры).",
            reply_markup=admin_back_button("manage_admins")
        )

# Обработчик подтверждения удаления администратора
@admin_auth_router.callback_query(AdminAuth.confirm_remove_admin, F.data.startswith("confirm_remove_"))
async def confirm_remove_admin(callback: CallbackQuery, state: FSMContext, request: RequestsRepo):
    """
    Обрабатывает подтверждение удаления администратора.
    """
    # Получаем ID администратора из callback
    admin_id = int(callback.data.split("_")[-1])
    
    # Получаем репозиторий пользователей
    users_repo = request.users
    
    # Обновляем роль пользователя на "user"
    await users_repo.update_field(admin_id, "role", "user")
    
    # Логируем действие
    logs_repo = request.logs
    await logs_repo.create_log(
        user_id=callback.from_user.id,
        action="remove_admin",
        details=f"Удален администратор с ID {admin_id}"
    )
    
    # Сбрасываем состояние и отправляем ответ
    await state.clear()
    
    await callback.message.edit_text(
        text=f"✅ <b>Администратор успешно удален!</b>\n\n"
             f"ID: {admin_id}\n",
        reply_markup=admin_back_button("manage_admins"),
        parse_mode="HTML"
    )
    await callback.answer()

# Обработчик кнопки "Список администраторов"
@admin_auth_router.callback_query(F.data == "list_admins")
async def list_admins_callback(callback: CallbackQuery, request: RequestsRepo):
    """
    Показывает список всех администраторов.
    """
    # Получаем репозиторий пользователей
    users_repo = request.users
    
    # Получаем всех пользователей с ролью "admin" или "manager"
    from sqlalchemy import select
    from infrastructure.database.models.users import User
    
    stmt = select(User).where(User.role.in_(["admin", "manager"])).order_by(User.user_id)
    result = await users_repo.session.execute(stmt)
    admins = list(result.scalars().all())
    
    if admins:
        text = "👨‍💼 <b>Список администраторов</b>\n\n"
        
        for admin in admins:
            text += f"ID: {admin.user_id}\n"
            text += f"Имя: {admin.first_name or 'Не указано'} {admin.last_name or ''}\n"
            text += f"Роль: {admin.role.capitalize()}\n"
            text += f"Активен: {'Да' if admin.active else 'Нет'}\n\n"
    else:
        text = "👨‍💼 <b>Список администраторов</b>\n\n"
        text += "В системе нет администраторов."
    
    await callback.message.edit_text(
        text=text,
        reply_markup=admin_back_button("manage_admins"),
        parse_mode="HTML"
    )
    await callback.answer()