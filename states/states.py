from aiogram.fsm.state import State, StatesGroup

class RegisterStates(StatesGroup):
    waiting_for_role = State()         
    waiting_for_invite = State()        

class TutorStates(StatesGroup):
    # Состояния для добавления ученика
    waiting_for_student_name = State()
    waiting_for_student_gender = State()
    waiting_for_student_age = State()
    waiting_for_student_subject = State()

    # Состояния для создания занятия
    waiting_lesson_student = State()
    # waiting_lesson_date = State()
    # waiting_lesson_time = State()
    waiting_lesson_duration = State()
    waiting_lesson_title = State()

class StudentStates(StatesGroup):
    waiting_for_invite = State()