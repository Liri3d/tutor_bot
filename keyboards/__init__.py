# keyboards/__init__.py
from .auth_kb import (
    start_menu_keyboard,
    role_keyboard,
    back_to_main_keyboard
)
from .tutor_kb import (
    tutor_menu_keyboard,
    build_students_keyboard,
    student_detail_menu,
    gender_keyboard
)


from .setting_kb import settings_menu, confirm_change_role_menu
from .stud_kb import student_menu_keyboard

__all__ = [
    'start_menu_keyboard',
    'tutor_menu_keyboard',
    'student_menu_keyboard',
    'role_keyboard',
    'back_to_main_keyboard',
    'build_students_keyboard',
    'student_detail_menu',
    'gender_keyboard',
    'settings_menu',
    'confirm_change_role_menu',
]