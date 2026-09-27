from networkx.generators import spectral_graph_forge
import tkinter as tk

from ui.registration_window import RegistrationWindow
from ui.attendance_window import AttendanceWindow
from ui.evaluation_window import EvaluationWindow

class MainWindow:

    def __init__(self, root, app):

        self.root = root
        self.app = app

        self.root.title(
            "Hệ thống điểm danh sinh viên"
        )

        self.root.geometry(
            "500x480"
        )

        self.root.resizable(
            False,
            False
        )

        self.create_interface()

    def create_interface(self):

        title = tk.Label(
            self.root,
            text="HỆ THỐNG ĐIỂM DANH",
            font=("Arial", 24, "bold")
        )

        title.pack(
            pady=(40, 30)
        )

        register_button = tk.Button(
            self.root,
            text="ĐĂNG KÝ SINH VIÊN",
            font=("Arial", 14),
            width=25,
            height=2,
            command=self.open_registration
        )

        register_button.pack(
            pady=8
        )

        attendance_button = tk.Button(
            self.root,
            text="ĐIỂM DANH",
            font=("Arial", 14),
            width=25,
            height=2,
            command=self.open_attendance
        )

        attendance_button.pack(
            pady=8
        )

        evaluation_button = tk.Button(
            self.root,
            text="ĐÁNH GIÁ HỆ THỐNG",
            font=("Arial", 14),
            width=25,
            height=2,
            command=self.open_evaluation
        )

        evaluation_button.pack(
            pady=8
        )

        exit_button = tk.Button(
            self.root,
            text="THOÁT",
            font=("Arial", 14),
            width=25,
            height=2,
            command=self.exit_application
        )

        exit_button.pack(
            pady=8
        )

    def open_registration(self):

        RegistrationWindow(
            self.root,
            self.app
        )

    def open_attendance(self):

        AttendanceWindow(
            self.root,
            self.app
        )

    def open_evaluation(self):

        EvaluationWindow(
            self.root,
            self.app
        )

    def exit_application(self):

        self.root.destroy()