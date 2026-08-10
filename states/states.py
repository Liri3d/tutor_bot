from aiogram.fsm.state import State, StatesGroup

class RegisterStates(StatesGroup):
    waiting_for_role = State()         
    waiting_for_invite = State()        

class TutorStates(StatesGroup):
    waiting_for_student_name = State()
    waiting_for_student_gender = State()
    waiting_for_student_age = State()
    waiting_for_student_subject = State()