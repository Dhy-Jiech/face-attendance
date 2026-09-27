import tkinter as tk
from tkinter import messagebox


class RegistrationWindow:

    def __init__(self, parent, app):

        self.parent = parent
        self.app = app

        self.window = tk.Toplevel(parent)

        self.window.title(
            "Đăng ký sinh viên"
        )

        self.window.geometry(
            "500x350"
        )

        self.window.resizable(
            False,
            False
        )

        self.create_interface()

    def create_interface(self):

        title = tk.Label(
            self.window,
            text="ĐĂNG KÝ SINH VIÊN",
            font=("Arial", 22, "bold")
        )

        title.pack(
            pady=(30, 30)
        )

        # MSSV

        mssv_frame = tk.Frame(
            self.window
        )

        mssv_frame.pack(
            pady=10
        )

        tk.Label(
            mssv_frame,
            text="MSSV:",
            font=("Arial", 13),
            width=10,
            anchor="w"
        ).pack(
            side="left"
        )

        self.mssv_entry = tk.Entry(
            mssv_frame,
            font=("Arial", 13),
            width=30
        )

        self.mssv_entry.pack(
            side="left"
        )

        # Họ tên

        name_frame = tk.Frame(
            self.window
        )

        name_frame.pack(
            pady=10
        )

        tk.Label(
            name_frame,
            text="Họ tên:",
            font=("Arial", 13),
            width=10,
            anchor="w"
        ).pack(
            side="left"
        )

        self.name_entry = tk.Entry(
            name_frame,
            font=("Arial", 13),
            width=30
        )

        self.name_entry.pack(
            side="left"
        )

        # Nút đăng ký

        register_button = tk.Button(
            self.window,
            text="ĐĂNG KÝ KHUÔN MẶT",
            font=("Arial", 13, "bold"),
            width=25,
            height=2,
            command=self.register
        )

        register_button.pack(
            pady=(25, 10)
        )

        # Nút hủy

        cancel_button = tk.Button(
            self.window,
            text="HỦY",
            font=("Arial", 12),
            width=15,
            command=self.cancel
        )

        cancel_button.pack()

    def register(self):

        student_code = (
            self.mssv_entry
            .get()
            .strip()
        )

        student_name = (
            self.name_entry
            .get()
            .strip()
        )

        if not student_code:

            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập MSSV."
            )

            return

        if not student_name:

            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập họ tên."
            )

            return

        result = self.app.register_student(
            student_code,
            student_name
        )

        if result["success"]:

            messagebox.showinfo(
                "Thành công",
                result["message"]
            )

            self.window.destroy()

        else:

            messagebox.showerror(
                "Đăng ký thất bại",
                result["message"]
            )

    def cancel(self):

        self.window.destroy()