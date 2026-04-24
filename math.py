import tkinter as tk
from tkinter import ttk, messagebox
import random

class MentalArithmeticApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ментальная арифметика")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        # Приятный фон
        self.root.configure(bg="#2c3e50")

        self.current_question = 0
        self.score = 0
        self.questions = []          # список кортежей (a, b, op, correct)
        self.user_answers = []
        self.level = None
        self.sprint_active = False
        self.sprint_time_left = 60
        self.sprint_timer_id = None
        self.hide_timer_id = None
        self.expected_correct = None  # для проверки ответа в обычном режиме

        self.create_widgets()

    def create_widgets(self):
        # Заголовок
        title = tk.Label(self.root, text="Ментальная арифметика",
                         font=("Arial", 24, "bold"), bg="#2c3e50", fg="white")
        title.pack(pady=20)

        # Фрейм для выбора уровня
        self.level_frame = tk.Frame(self.root, bg="#2c3e50")
        self.level_frame.pack(pady=20)

        tk.Label(self.level_frame, text="Выберите уровень сложности:",
                 font=("Arial", 14), bg="#2c3e50", fg="white").pack()

        self.level_var = tk.StringVar(value="easy")
        levels = [
            ("Лёгкий (1–10, только +)", "easy"),
            ("Сложный (10–99, +, -, *, /)", "hard"),
            ("Спринт (60 сек, примеры исчезают)", "sprint")
        ]

        for text, value in levels:
            rb = tk.Radiobutton(self.level_frame, text=text, variable=self.level_var, value=value,
                                font=("Arial", 12), bg="#2c3e50", fg="white", selectcolor="#2c3e50",
                                activebackground="#2c3e50")
            rb.pack(anchor="w", padx=20)

        # Кнопка старта
        self.start_btn = ttk.Button(self.root, text="Начать тест", command=self.start_test)
        self.start_btn.pack(pady=20)

        # Место для отображения вопроса
        self.question_label = tk.Label(self.root, text="", font=("Arial", 32, "bold"),
                                       bg="#2c3e50", fg="#f1c40f")
        self.question_label.pack(pady=30)

        # Поле ввода ответа
        self.answer_entry = tk.Entry(self.root, font=("Arial", 20), justify="center", width=10)
        self.answer_entry.pack(pady=10)

        # Кнопка "Ответить"
        self.submit_btn = ttk.Button(self.root, text="Ответить", command=self.check_answer)
        self.submit_btn.pack(pady=10)

        # Метка для прогресса
        self.progress_label = tk.Label(self.root, text="", font=("Arial", 12),
                                       bg="#2c3e50", fg="white")
        self.progress_label.pack(pady=10)

        # Изначально скрываем элементы теста
        self.question_label.pack_forget()
        self.answer_entry.pack_forget()
        self.submit_btn.pack_forget()
        self.progress_label.pack_forget()

    def start_test(self):
        """Начинает тест с выбранным уровнем"""
        self.level = self.level_var.get()
        self.sprint_active = (self.level == "sprint")
        if self.sprint_active:
            self.start_sprint()
        else:
            self.start_normal_test()

    def start_normal_test(self):
        """Обычный режим: 10 примеров, каждый исчезает через 1.5 секунды"""
        self.generate_questions()
        self.current_question = 0
        self.score = 0
        self.user_answers = []
        self.expected_correct = None

        # Показываем элементы теста
        self.question_label.pack()
        self.answer_entry.pack()
        self.submit_btn.pack()
        self.progress_label.pack()

        # Скрываем выбор уровня и кнопку старта
        self.level_frame.pack_forget()
        self.start_btn.pack_forget()

        self.show_question()

    def start_sprint(self):
        """Режим спринта: 60 секунд, примеры исчезают, бесконечное количество"""
        self.sprint_time_left = 60
        self.score = 0
        self.current_question = 0
        self.user_answers = []
        self.expected_correct = None

        # Показываем элементы теста
        self.question_label.pack()
        self.answer_entry.pack()
        self.submit_btn.pack()
        self.progress_label.pack()

        # Скрываем выбор уровня и кнопку старта
        self.level_frame.pack_forget()
        self.start_btn.pack_forget()

        # Запускаем общий таймер
        self.update_sprint_timer()
        # Показываем первый пример
        self.show_sprint_question()

    def update_sprint_timer(self):
        """Обновление таймера спринта"""
        if self.sprint_time_left > 0:
            self.progress_label.config(text=f"⏱️ Осталось: {self.sprint_time_left} сек | ✅ Решено: {self.score}")
            self.sprint_time_left -= 1
            self.sprint_timer_id = self.root.after(1000, self.update_sprint_timer)
        else:
            # Время вышло
            if self.sprint_timer_id:
                self.root.after_cancel(self.sprint_timer_id)
            self.end_sprint()

    def generate_question(self):
        """Генерирует один вопрос в зависимости от уровня (без спринта)"""
        if self.level == "easy":
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            op = "+"
            correct = a + b
        else:  # hard
            a = random.randint(10, 99)
            b = random.randint(10, 99)
            op = random.choice(["+", "-", "*", "/"])
            if op == "+":
                correct = a + b
            elif op == "-":
                if a < b:
                    a, b = b, a
                correct = a - b
            elif op == "*":
                correct = a * b
            else:  # деление
                # Генерируем b от 2 до 20, a = b * k, чтобы a было в [10, 99]
                b = random.randint(2, 20)
                max_k = 99 // b
                if max_k < 2:
                    # если b большое, подбираем другое
                    b = random.randint(2, 10)
                    max_k = 99 // b
                k = random.randint(2, max_k)
                a = b * k
                correct = a // b
        return a, b, op, correct

    def generate_questions(self):
        """Генерирует 10 вопросов для обычного режима"""
        self.questions = []
        for _ in range(10):
            self.questions.append(self.generate_question())

    def show_question(self):
        """Отображает текущий вопрос в обычном режиме"""
        if self.current_question < len(self.questions):
            a, b, op, correct = self.questions[self.current_question]
            self.expected_correct = correct
            self.question_label.config(text=f"{a} {op} {b} = ?")
            self.progress_label.config(text=f"Вопрос {self.current_question + 1} из 10")
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.focus()

            # Запускаем таймер на скрытие
            if self.hide_timer_id:
                self.root.after_cancel(self.hide_timer_id)
            self.hide_timer_id = self.root.after(1500, self.hide_question)
        else:
            self.end_normal_test()

    def hide_question(self):
        """Скрывает вопрос в обычном режиме"""
        self.question_label.config(text="?")
        self.hide_timer_id = None

    def show_sprint_question(self):
        """Показывает пример в спринте, затем скрывает через 1.5 секунды"""
        if not self.sprint_active:
            return

        # Генерируем пример для спринта (лёгкий: 1–20, + или –)
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        op = random.choice(["+", "-"])
        if op == "+":
            correct = a + b
        else:
            if a < b:
                a, b = b, a
            correct = a - b

        self.current_question += 1
        self.expected_correct = correct
        self.question_label.config(text=f"{a} {op} {b} = ?")
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.focus()

        # Запускаем таймер на скрытие
        if self.hide_timer_id:
            self.root.after_cancel(self.hide_timer_id)
        self.hide_timer_id = self.root.after(1500, self.hide_sprint_question)

    def hide_sprint_question(self):
        """Скрывает пример в спринте"""
        self.question_label.config(text="?")
        self.hide_timer_id = None

    def check_answer(self):
        """Проверяет ответ (для обычного и спринта)"""
        try:
            user_answer = int(self.answer_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введите целое число!")
            return

        if self.expected_correct is None:
            messagebox.showwarning("Внимание", "Пример уже скрыт, но вы можете ввести ответ по памяти.")
            # Всё равно проверяем, но предупреждаем

        if self.sprint_active:
            # Спринт: запоминаем ответ и переходим к следующему
            self.user_answers.append((self.expected_correct, user_answer))
            if user_answer == self.expected_correct:
                self.score += 1
            self.show_sprint_question()
        else:
            # Обычный режим
            self.user_answers.append((self.expected_correct, user_answer))
            if user_answer == self.expected_correct:
                self.score += 1
            self.current_question += 1
            self.show_question()

    def end_normal_test(self):
        """Завершает обычный тест"""
        self.cleanup_test()
        percent = (self.score / 10) * 100
        grade = self.get_grade(percent)
        result_text = f"Вы ответили правильно на {self.score} из 10 вопросов.\nОценка: {grade}"
        messagebox.showinfo("Результат", result_text)

        # Детали
        if self.user_answers:
            details = "Детали:\n"
            for i, (correct, user_ans) in enumerate(self.user_answers):
                status = "✓" if user_ans == correct else "✗"
                # Получаем оригинальный пример из self.questions, если есть
                if i < len(self.questions):
                    a, b, op, _ = self.questions[i]
                    details += f"{i+1}. {a} {op} {b} = {correct} (Ваш ответ: {user_ans}) {status}\n"
                else:
                    details += f"{i+1}. Ответ должен быть {correct} (Ваш ответ: {user_ans}) {status}\n"
            messagebox.showinfo("Разбор ошибок", details)

    def end_sprint(self):
        """Завершает спринт"""
        self.sprint_active = False
        if self.sprint_timer_id:
            self.root.after_cancel(self.sprint_timer_id)
        if self.hide_timer_id:
            self.root.after_cancel(self.hide_timer_id)

        self.cleanup_test()

        total = self.current_question
        if total == 0:
            messagebox.showinfo("Результат", "Вы не решили ни одного примера.")
            return

        percent = (self.score / total) * 100
        grade = self.get_grade(percent)
        result_text = f"За 60 секунд вы решили {total} примеров.\nПравильно: {self.score} из {total} ({percent:.0f}%).\nОценка: {grade}"
        messagebox.showinfo("Результат спринта", result_text)

        # Детали
        if self.user_answers:
            details = "Детали:\n"
            for i, (correct, user_ans) in enumerate(self.user_answers):
                status = "✓" if user_ans == correct else "✗"
                details += f"{i+1}. Ответ: {correct} (Ваш ответ: {user_ans}) {status}\n"
            messagebox.showinfo("Разбор ошибок", details)

    def cleanup_test(self):
        """Скрывает элементы теста и возвращает главное меню"""
        self.question_label.pack_forget()
        self.answer_entry.pack_forget()
        self.submit_btn.pack_forget()
        self.progress_label.pack_forget()
        self.level_frame.pack()
        self.start_btn.pack()
        self.expected_correct = None

    def get_grade(self, percent):
        """Возвращает оценку на основе процента правильных ответов"""
        if percent >= 90:
            return "Отлично!"
        elif percent >= 70:
            return "Хорошо!"
        elif percent >= 50:
            return "Удовлетворительно."
        else:
            return "Плохо. Нужно больше тренироваться."

if __name__ == "__main__":
    root = tk.Tk()
    app = MentalArithmeticApp(root)
    root.mainloop()