import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from tests.evaluate_recognition import RecognitionEvaluator


class EvaluationWindow:

    def __init__(self, parent, app):

        self.parent = parent
        self.app = app

        self.window = tk.Toplevel(parent)

        self.window.title(
            "Đánh giá hệ thống nhận diện"
        )

        self.window.geometry(
            "680x600"
        )

        self.window.resizable(
            True,
            True
        )

        self.is_evaluating = False

        self.create_interface()

    def create_interface(self):

        # Title
        title_label = tk.Label(
            self.window,
            text="ĐÁNH GIÁ HỆ THỐNG NHẬN DIỆN",
            font=("Arial", 18, "bold")
        )

        title_label.pack(
            pady=(20, 15)
        )

        # Control frame for Threshold
        control_frame = tk.Frame(self.window)

        control_frame.pack(
            pady=5,
            fill=tk.X,
            padx=20
        )

        threshold_label = tk.Label(
            control_frame,
            text="Ngưỡng Threshold:",
            font=("Arial", 11)
        )

        threshold_label.pack(
            side=tk.LEFT,
            padx=(0, 10)
        )

        self.threshold_var = tk.StringVar(value="0.65")

        self.threshold_entry = tk.Entry(
            control_frame,
            textvariable=self.threshold_var,
            font=("Arial", 11),
            width=8
        )

        self.threshold_entry.pack(
            side=tk.LEFT,
            padx=(0, 20)
        )

        self.start_button = tk.Button(
            control_frame,
            text="ĐÁNH GIÁ MÔ HÌNH AI (TẬP TEST)",
            font=("Arial", 10, "bold"),
            bg="#2196F3",
            fg="white",
            padx=10,
            pady=4,
            command=self.start_evaluation
        )

        self.start_button.pack(
            side=tk.LEFT,
            padx=(0, 10)
        )

        self.realtime_report_button = tk.Button(
            control_frame,
            text="BÁO CÁO HIỆU NĂNG REAL-TIME",
            font=("Arial", 10, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=10,
            pady=4,
            command=self.show_realtime_report
        )

        self.realtime_report_button.pack(
            side=tk.LEFT
        )

        # Status label
        self.status_label = tk.Label(
            self.window,
            text="Đánh giá mô hình AI trên tập ảnh test HOẶC xem báo cáo chỉ số Real-time khi bật camera điểm danh",
            font=("Arial", 10, "italic"),
            fg="#555555"
        )

        self.status_label.pack(
            pady=(10, 5)
        )

        # Progress bar
        self.progressbar = ttk.Progressbar(
            self.window,
            mode="indeterminate"
        )

        self.progressbar.pack(
            fill=tk.X,
            padx=20,
            pady=5
        )

        # Results Summary Frame
        self.summary_frame = tk.LabelFrame(
            self.window,
            text=" Kết quả tổng quan ",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=10
        )

        self.summary_frame.pack(
            fill=tk.X,
            padx=20,
            pady=10
        )

        # Grid labels for metrics
        self.lbl_total = tk.Label(self.summary_frame, text="Tổng số ảnh test: --", font=("Arial", 10))
        self.lbl_total.grid(row=0, column=0, sticky="w", padx=10, pady=2)

        self.lbl_correct = tk.Label(self.summary_frame, text="Nhận diện đúng: --", font=("Arial", 10, "bold"), fg="green")
        self.lbl_correct.grid(row=0, column=1, sticky="w", padx=10, pady=2)

        self.lbl_wrong = tk.Label(self.summary_frame, text="Nhận diện sai: --", font=("Arial", 10, "bold"), fg="red")
        self.lbl_wrong.grid(row=0, column=2, sticky="w", padx=10, pady=2)

        self.lbl_accuracy = tk.Label(self.summary_frame, text="Accuracy: --", font=("Arial", 10, "bold"))
        self.lbl_accuracy.grid(row=1, column=0, sticky="w", padx=10, pady=2)

        self.lbl_precision = tk.Label(self.summary_frame, text="Precision: --", font=("Arial", 10))
        self.lbl_precision.grid(row=1, column=1, sticky="w", padx=10, pady=2)

        self.lbl_recall = tk.Label(self.summary_frame, text="Recall: --", font=("Arial", 10))
        self.lbl_recall.grid(row=1, column=2, sticky="w", padx=10, pady=2)

        self.lbl_f1 = tk.Label(self.summary_frame, text="F1-Score: --", font=("Arial", 10))
        self.lbl_f1.grid(row=2, column=0, sticky="w", padx=10, pady=2)

        # Detailed Log / Confusion Matrix Text Area
        log_label = tk.Label(
            self.window,
            text="Chi tiết Ma trận nhầm lẫn (Confusion Matrix) & Báo cáo:",
            font=("Arial", 10, "bold")
        )

        log_label.pack(
            anchor="w",
            padx=20,
            pady=(5, 2)
        )

        self.text_area = scrolledtext.ScrolledText(
            self.window,
            font=("Consolas", 10),
            wrap=tk.WORD,
            height=12
        )

        self.text_area.pack(
            fill=tk.BOTH,
            expand=True,
            padx=20,
            pady=(0, 15)
        )

    def start_evaluation(self):

        if self.is_evaluating:
            return

        try:
            threshold_val = float(self.threshold_var.get().strip())
        except ValueError:
            messagebox.showerror(
                "Lỗi nhập liệu",
                "Vui lòng nhập giá trị threshold là một số thực hợp lệ (ví dụ: 0.65)."
            )
            return

        self.is_evaluating = True

        self.start_button.config(state=tk.DISABLED)

        self.status_label.config(
            text=f"Đang thực hiện đánh giá với threshold = {threshold_val}...",
            fg="#0055FF"
        )

        self.progressbar.start(10)

        # Clear previous text
        self.text_area.delete("1.0", tk.END)

        # Run in separate thread
        thread = threading.Thread(
            target=self._run_eval_thread,
            args=(threshold_val,),
            daemon=True
        )

        thread.start()

    def _run_eval_thread(self, threshold_val):

        evaluator = None

        try:

            evaluator = RecognitionEvaluator(threshold=threshold_val)

            results = evaluator.evaluate()

            # Schedule UI update on main thread
            self.window.after(
                0,
                self._update_ui_results,
                results
            )

        except Exception as e:

            self.window.after(
                0,
                self._handle_eval_error,
                str(e)
            )

        finally:

            if evaluator is not None:
                try:
                    evaluator.close()
                except Exception:
                    pass

    def _update_ui_results(self, results):

        self.progressbar.stop()

        self.is_evaluating = False

        self.start_button.config(state=tk.NORMAL)

        self.status_label.config(
            text="Đánh giá hoàn tất!",
            fg="green"
        )

        # Update labels
        self.lbl_total.config(text=f"Tổng số ảnh test: {results['total']}")
        self.lbl_correct.config(text=f"Nhận diện đúng: {results['correct']}")
        self.lbl_wrong.config(text=f"Nhận diện sai: {results['wrong']}")

        self.lbl_accuracy.config(text=f"Accuracy: {results['accuracy']:.2f}%")
        self.lbl_precision.config(text=f"Precision: {results['precision']:.2f}%")
        self.lbl_recall.config(text=f"Recall: {results['recall']:.2f}%")
        self.lbl_f1.config(text=f"F1-Score: {results['f1']:.2f}%")

        # Display matrix & report in text area
        self.text_area.insert(tk.END, "========================================\n")
        self.text_area.insert(tk.END, "       BÁO CÁO ĐÁNH GIÁ CHI TIẾT\n")
        self.text_area.insert(tk.END, "========================================\n\n")
        self.text_area.insert(tk.END, f"• Tổng số ảnh test : {results['total']}\n")
        self.text_area.insert(tk.END, f"• Nhận diện đúng   : {results['correct']}\n")
        self.text_area.insert(tk.END, f"• Nhận diện sai    : {results['wrong']}\n\n")
        self.text_area.insert(tk.END, f"• Accuracy         : {results['accuracy']:.2f}%\n")
        self.text_area.insert(tk.END, f"• Precision        : {results['precision']:.2f}%\n")
        self.text_area.insert(tk.END, f"• Recall           : {results['recall']:.2f}%\n")
        self.text_area.insert(tk.END, f"• F1-score         : {results['f1']:.2f}%\n\n")
        self.text_area.insert(tk.END, "Labels:\n")
        self.text_area.insert(tk.END, f"{results['labels']}\n\n")
        self.text_area.insert(tk.END, "Confusion Matrix:\n")
        self.text_area.insert(tk.END, f"{results['confusion_matrix']}\n")

    def show_realtime_report(self):

        if not hasattr(self.app, "metrics_tracker") or self.app.metrics_tracker is None:
            from app.attendance.realtime_metrics import RealtimeMetricsTracker
            self.app.metrics_tracker = RealtimeMetricsTracker()

        metrics_tracker = self.app.metrics_tracker
        m = metrics_tracker.get_summary_metrics()

        self.status_label.config(
            text="Hiển thị chỉ số Hiệu năng Real-time & Nghiệp vụ Điểm danh",
            fg="#0055FF"
        )

        # Update summary labels
        self.lbl_total.config(text=f"Lượt điểm danh: {m['total_attempts']}")
        self.lbl_correct.config(text=f"Thành công: {m['successful_attendances']}")
        self.lbl_wrong.config(text=f"Thất bại: {m['failed_attendances']}")

        self.lbl_accuracy.config(text=f"FPS: {m['fps']}")
        self.lbl_precision.config(text=f"Latency: {m['avg_latency_ms']} ms")
        self.lbl_recall.config(text=f"Time/SV: {m['avg_time_per_student']}s")
        self.lbl_f1.config(text=f"DB Reliability: {m['transaction_reliability']}%")

        # Update Text area with formatted report
        self.text_area.delete("1.0", tk.END)
        report_text = metrics_tracker.generate_report_text()
        self.text_area.insert(tk.END, report_text)

    def _handle_eval_error(self, error_msg):

        self.progressbar.stop()

        self.is_evaluating = False

        self.start_button.config(state=tk.NORMAL)

        self.status_label.config(
            text="Lỗi khi thực hiện đánh giá!",
            fg="red"
        )

        messagebox.showerror(
            "Lỗi đánh giá",
            f"Đã xảy ra lỗi trong quá trình đánh giá:\n{error_msg}"
        )

