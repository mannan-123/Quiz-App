import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox, QLabel, QPushButton, QVBoxLayout, QFontDialog, QColorDialog, QWidget, QLineEdit
from PyQt5.QtGui import QColor
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
import pyodbc

# Use the connection string
# Database connection parameters (adjust these based on your MS Access setup)
conn_str = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=D:\\BS CS\\Freelancing\\Mannan\\Quiz Pyqt\\QuizDatabase.accdb;'
conn_str_Questions = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=D:\\BS CS\\Freelancing\\Mannan\\Quiz Pyqt\\Questions.accdb;'

class SignUpWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the SignUp UI File
        loadUi('SignuppageUI.ui', self)

        # Button Connections to functions
        self.btnSignup.pressed.connect(self.signup)
        self.btnHaveAccount.pressed.connect(self.haveAccount)

    def haveAccount(self):
        self.close()
        login_window.show()

    def signup(self):
        # Get user input from UI
        forename = self.txtForename.text()
        surname = self.txtSurname.text()
        username = self.txtUsername.text()
        email = self.txtEmail.text()
        password = self.txtPassword.text()
        pass_hint = self.txtPasswordHint.text()
        is_teacher = self.rbIsTeacher.isChecked()

        # Validate input (add your specific validation rules)
        if not all([forename, surname, username, email, password, pass_hint]):
            QMessageBox.warning(self, "Validation Error", "All fields must be filled.")
            return

        try:
            # Connect to the database
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            # Check if the username is already taken
            cursor.execute("SELECT COUNT(*) FROM Login WHERE Username=?", (username,))
            if cursor.fetchone()[0] > 0:
                QMessageBox.warning(self, "Username Taken", "Username is already in use. Please choose another.")
                return

            # Insert the new user into the database
            cursor.execute("""
                INSERT INTO Login (Username, Password, passhint, email, forename, surname, teacher)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (username, password, pass_hint, email, forename, surname, is_teacher))

            # Commit the transaction
            conn.commit()

            # Inform the user about successful signup
            QMessageBox.information(self, "Signup Successful", "Account created successfully.")

            self.close()
            if is_teacher:
                teacher_window.show()
            else:
                quiz_window.show()

        except pyodbc.Error as e:
            # Handle database errors
            print(f"Database Error: {e}")
            QMessageBox.critical(self, "Database Error", "An error occurred while accessing the database.")

        finally:
            try:
                # Close the database connection
                if conn:
                    conn.close()
            except NameError:
                pass  # Ignore the NameError if conn was not defined

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the UI file
        loadUi('LoginUI.ui', self)

        # Connections
        self.btnLogin.clicked.connect(self.login)
        self.btnForgotPass.clicked.connect(self.forgotPassword)
        self.btnCreateAccount.clicked.connect(self.createAccount)
    
    def createAccount(self):
        self.close()
        signup_window.show()

    def login(self):
        # Get user input from UI
        username = self.txtUsername.text()
        password = self.txtPassword.text()

        # Validate input (add your specific validation rules)
        if not all([username, password]):
            QMessageBox.warning(self, "Validation Error", "All fields must be filled.")
            return

        try:
            # Connect to the database
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            # Check if the username exists
            cursor.execute("SELECT COUNT(*) FROM Login WHERE Username=?", (username,))
            if cursor.fetchone()[0] == 0:
                QMessageBox.warning(self, "Invalid Username", "Username does not exist.")
                return

            # Check if the password is correct
            cursor.execute("SELECT COUNT(*) FROM Login WHERE Username=? AND Password=?", (username, password))
            if cursor.fetchone()[0] == 0:
                QMessageBox.warning(self, "Invalid Password", "Password is incorrect.")
                return

            # Inform the user about successful login
            QMessageBox.information(self, "Login Successful", "You have successfully logged in.")

            self.close()
            
            # Check if the user is a teacher
            cursor.execute("SELECT teacher FROM Login WHERE Username=?", (username,))
            is_teacher = cursor.fetchone()[0]
            if is_teacher:
                teacher_window.show()
            else:
                quiz_window.show()

        except pyodbc.Error as e:
            # Handle database errors
            print(f"Database Error: {e}")
            QMessageBox.critical(self, "Database Error", "An error occurred while accessing the database.")
        
        finally:
            try:
                # Close the database connection
                if conn:
                    conn.close()
            except NameError:
                pass  # Ignore the NameError if conn was not defined

    def forgotPassword(self):
        
        # Get user input from UI
        username = self.txtUsername.text()

        # Validate input (add your specific validation rules)
        if not username:
            QMessageBox.warning(self, "Validation Error", "Username must be filled.")
            return

        try:
            # Connect to the database
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            # Check if the username exists
            cursor.execute("SELECT COUNT(*) FROM Login WHERE Username=?", (username,))
            if cursor.fetchone()[0] == 0:
                QMessageBox.warning(self, "Invalid Username", "Username does not exist.")
                return

            # Get the password hint
            cursor.execute("SELECT passhint FROM Login WHERE Username=?", (username,))
            pass_hint = cursor.fetchone()[0]

            # Inform the user about the password hint
            QMessageBox.information(self, "Password Hint", f"Your password hint is: {pass_hint}")

        except pyodbc.Error as e:
            # Handle database errors
            print(f"Database Error: {e}")
            QMessageBox.critical(self, "Database Error", "An error occurred while accessing the database.")

        finally:
            try:
                # Close the database connection
                if conn:
                    conn.close()
            except NameError:
                pass  # Ignore the NameError if conn was not defined

class QuizWindow(QDialog):
    def __init__(self):
        super().__init__()

        # Load the UI file
        loadUi('QuizProject.ui', self)
        self.stackedWidget.setCurrentIndex(0)

        # Selected Subject
        self.subject = None
        self.selectedFont = None

        # Scroll Area
        self.scroll_layout = QVBoxLayout()
        self.scrollAreaQuiz.setWidgetResizable(True)
        self.scrollAreaQuiz.setLayout(self.scroll_layout)

        # Connections

        # pageHome Buttons
        self.btnLogout.clicked.connect(self.logout)
        self.btnSetting.clicked.connect(self.change_to_setting)
        self.btnTakeQuiz.clicked.connect(self.change_to_quiz_subjects)

        # pageSetting Buttons
        self.btnBack.clicked.connect(self.change_to_home)
        self.btnChgFont.clicked.connect(self.change_font)
        self.btnChgBgColor.clicked.connect(self.change_background_color)

        # pageQuizSubjects Buttons
        self.btnBack_2.clicked.connect(self.change_to_home)
        # Subject Buttons
        self.btnBiology.clicked.connect(lambda: self.change_to_quiz('Biology'))
        self.btnComputing.clicked.connect(lambda: self.change_to_quiz('Computing'))
        self.btnCustom.clicked.connect(lambda: self.change_to_quiz('Custom'))
        self.btnGeography.clicked.connect(lambda: self.change_to_quiz('Geography'))

        # pageQuiz Buttons
        self.btnBack_3.clicked.connect(self.change_to_quiz_subjects)
        self.btnCheckAnswers.clicked.connect(self.check_answers)

    # Functions

    # Change Stacked Widget
    def change_to_home(self):
        self.stackedWidget.setCurrentIndex(0)    

    def change_to_setting(self):
        self.stackedWidget.setCurrentIndex(1)

    def change_to_quiz_subjects(self):
        self.stackedWidget.setCurrentIndex(2)

    def change_to_quiz(self, sub):
        self.subject = sub
        self.lblQuizTitle.setText("Quiz " +sub)
        self.load_quiz(sub)
        self.stackedWidget.setCurrentIndex(3)

    def load_quiz(self, subject):
        
        try:
            # Connect to the database
            conn = pyodbc.connect(conn_str_Questions)
            cursor = conn.cursor()

            # Get the questions and answers
            cursor.execute(f"SELECT * FROM {subject}")
            questions = cursor.fetchall()

            # Clear the existing layout and delete the widgets
            for i in reversed(range(self.scroll_layout.count())):
                self.scroll_layout.itemAt(i).widget().setParent(None)

            # Display the questions and answers in the scroll area
            for question_id, question_text, answer_text in questions:
                question_label = QLabel(question_text)
                answer_line_edit = QLineEdit()
                
                if self.selectedFont:
                    question_label.setFont(self.selectedFont)
                    answer_line_edit.setFont(self.selectedFont)

                # Add question label and answer line edit to the layout
                self.scroll_layout.addWidget(question_label)
                self.scroll_layout.addWidget(answer_line_edit)


        except pyodbc.Error as e:
            # Handle database errors
            print(f"Database Error: {e}")

        finally:
            try:
                # Close the database connection
                if conn:
                    conn.close()
            except NameError:
                pass  # Ignore the NameError if conn was not defined

    def check_answers(self):
        incorrect_questions = []
        try:
            # Connect to the database
            conn = pyodbc.connect(conn_str_Questions)
            cursor = conn.cursor()

            # Get the correct answers from the database
            cursor.execute(f"SELECT Answers FROM {self.subject}")
            correct_answers = [row.Answers for row in cursor.fetchall()]

            # Iterate through the widgets in the scroll layout
            for i in range(0, self.scroll_layout.count(), 2):  # Every second widget is an answer_line_edit
                question_label = self.scroll_layout.itemAt(i).widget()
                answer_line_edit = self.scroll_layout.itemAt(i + 1).widget()

                # Retrieve the entered answer
                user_answer = answer_line_edit.text().strip()

                # Get the corresponding correct answer
                correct_answer = correct_answers[i // 2] if i // 2 < len(correct_answers) else ""

                # Compare the user's answer with the correct answer
                if user_answer.lower() == correct_answer.lower():  # Use lower() for case-insensitive comparison
                    question_label.setStyleSheet("color: green;")
                else:
                    question_label.setStyleSheet("color: red;")
                    incorrect_questions.append(question_label.text())

            # Display summary message at the end
            if incorrect_questions:
                incorrect_msg = "\n".join(incorrect_questions)
                QMessageBox.warning(self, "Incorrect Answers", f"Your answers for the following questions are incorrect:\n\n{incorrect_msg}")
            else:
                QMessageBox.information(self, "All Correct", "Congratulations! All your answers are correct.")

        except pyodbc.Error as e:
            # Handle database errors
            print(f"Database Error: {e}")

        finally:
            try:
                # Close the database connection
                if conn:
                    conn.close()
            except NameError:
                pass  # Ignore the NameError if conn was not defined


    # Logout
    def logout(self):
        self.close()
        login_window.show()

    # Change Font
    def change_font(self):

        font, ok = QFontDialog.getFont(self.font(), self)
        if ok:
            self.selectedFont = font
            #self.set_font_for_all_widgets(self, font)

    def set_font_for_all_widgets(self, widget, font):
        # Recursively set the font for all child widgets
        if widget is not None:
            widget.setFont(font)
            for child_widget in widget.findChildren(QWidget):
                self.set_font_for_all_widgets(child_widget, font)

    # Change Background Color
    def change_background_color(self):
        color = QColorDialog.getColor(self.palette().color(self.backgroundRole()), self)
        if color.isValid():
            self.setStyleSheet(f"background-color: {color.name()};")

class TeacherWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the UI file
        loadUi('TeacherUI.ui', self)
        self.stackedWidget.setCurrentIndex(0)

        # Selected Subject
        self.subject = None

        # Connections

        # pageHome Buttons
        self.btnLogout.clicked.connect(self.logout)
        self.btnQuizSubjects.clicked.connect(self.change_to_quiz_subjects)

        # pageQuizSubjects Buttons
        self.btnBack.clicked.connect(self.change_to_home)
        # Subject Buttons
        self.btnBiology.clicked.connect(lambda: self.change_to_quiz('Biology'))
        self.btnComputing.clicked.connect(lambda: self.change_to_quiz('Computing'))
        self.btnCustom.clicked.connect(lambda: self.change_to_quiz('Custom'))
        self.btnGeography.clicked.connect(lambda: self.change_to_quiz('Geography'))

        # pageAddQuiz Buttons
        self.btnBack_2.clicked.connect(self.change_to_quiz_subjects)
        self.btnAddQuestion.clicked.connect(self.add_question)

    # Functions

    # Add Question
    def add_question(self):

        # Get user input from UI
        question = self.txtQuestion.text()
        answer = self.txtCorrectAnswer.text()

        # Validate input (add your specific validation rules)
        if not all([question, answer]):
            QMessageBox.warning(self, "Validation Error", "All fields must be filled.")
            return

        try:
            # Connect to the database
            conn = pyodbc.connect(conn_str_Questions)
            cursor = conn.cursor()

            # Check if the question is already in the database
            cursor.execute(f"SELECT COUNT(*) FROM {self.subject} WHERE Questions=?", (question,))
            if cursor.fetchone()[0] > 0:
                QMessageBox.warning(self, "Question Already Exists", "Question is already in the database. Please choose another.")
                return

            # Insert the new question into the database
            cursor.execute(f"""
                INSERT INTO {self.subject} (Questions, Answers)
                VALUES (?, ?)
            """, (question, answer))

            # Commit the transaction
            conn.commit()

            # Inform the user about successful signup
            QMessageBox.information(self, "Question Added", "Question added successfully.")

            # Clear the text fields
            self.txtQuestion.clear()
            self.txtCorrectAnswer.clear()

        except pyodbc.Error as e:
            # Handle database errors
            print(f"Database Error: {e}")
            QMessageBox.critical(self, "Database Error", "An error occurred while accessing the database.")

        finally:
            try:
                # Close the database connection
                if conn:
                    conn.close()
            except NameError:
                pass  # Ignore the NameError if conn was not defined

    # Logout
    def logout(self):
        self.close()
        login_window.show()

    # Change Stacked Widget
    def change_to_home(self):
        self.stackedWidget.setCurrentIndex(0)    

    def change_to_quiz_subjects(self):
        self.stackedWidget.setCurrentIndex(1)

    def change_to_quiz(self, sub):
        self.subject = sub
        self.stackedWidget.setCurrentIndex(2)


# Main Application
if __name__ == "__main__":
    app = QApplication(sys.argv)

    signup_window = SignUpWindow()
    login_window = LoginWindow()
    quiz_window = QuizWindow()
    teacher_window = TeacherWindow()

    login_window.show()
    sys.exit(app.exec_())
