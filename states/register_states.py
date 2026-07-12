from aiogram.fsm.state import State, StatesGroup

class RegisterStates(StatesGroup):
    waiting_for_role = State()         
    waiting_for_invite = State()        

class TutorStates(StatesGroup):
    waiting_for_student_name = State()