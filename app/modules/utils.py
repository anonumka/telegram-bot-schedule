from app.modules.question_handler import Question

def get_question_info(question: Question) -> str:
    res_text = f"Вопрос: {question.question}\nПравильный ответ: {question.answer}\n"
    for full_name, _, answer in question.answers:
        res_text += f"{full_name}: {answer}\n"
    return res_text
