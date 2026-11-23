"""教务管理系统（GUI 版）

以原控制台版为基础，做成类似购物车示例的桌面界面：
上方录入姓名和三科成绩，中间一排功能按钮，下方大页面展示结果。
"""

import tkinter as tk
import unicodedata
from tkinter import messagebox, ttk

ST_SUBJECTS = ("语文", "数学", "英语")

BG_COLOR = "#f0f0f0"
TITLE_FONT = ("SimSun", 30, "bold")
LABEL_FONT = ("Microsoft YaHei UI", 12)
ENTRY_FONT = ("Microsoft YaHei UI", 12)
BUTTON_FONT = ("Microsoft YaHei UI", 11, "bold")
DISPLAY_FONT = ("Consolas", 13)


def format_score(score):
    """把 88.0 显示为 88，把 88.5 保留为 88.5。"""
    return f"{score:g}"


def display_width(text):
    """计算字符串在等宽字体下占用的显示宽度，中文按 2 列计算。"""
    width = 0
    for char in str(text):
        width += 2 if unicodedata.east_asian_width(char) in ("W", "F") else 1
    return width


def pad_text(text, width):
    """按显示宽度在右侧补空格，保证表格列对齐。"""
    text = str(text)
    return text + " " * max(0, width - display_width(text))


class TeachingSystemApp:
    def __init__(self, root):
        self.root = root
        self.amsy = {}

        self.root.title("教务管理系统")
        self.root.configure(bg=BG_COLOR)
        self._set_window_size()

        self.status_var = tk.StringVar(
            value="就绪：添加需填写姓名和三科成绩；修改时留空的成绩保持不变。"
        )
        self._build_ui()
        self._render_list()
        self.name_entry.focus_set()

    # ---------- 界面 ----------
    def _set_window_size(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = min(1180, screen_width - 60)
        height = min(860, screen_height - 100)
        x = max(0, (screen_width - width) // 2)
        y = max(0, (screen_height - height) // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(920, 620)

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(4, weight=1)

        title = tk.Label(
            self.root,
            text="教务管理系统",
            font=TITLE_FONT,
            bg=BG_COLOR,
            fg="#111111",
        )
        title.grid(row=0, column=0, pady=(22, 10))

        input_frame = tk.Frame(self.root, bg=BG_COLOR)
        input_frame.grid(row=1, column=0, sticky="ew", padx=40, pady=(6, 12))
        input_frame.columnconfigure(1, weight=2)
        for column in (3, 5, 7):
            input_frame.columnconfigure(column, weight=1)

        self.name_entry = self._make_entry(input_frame, "姓名：", 0)
        self.ch_entry = self._make_entry(input_frame, "语文：", 2)
        self.ma_entry = self._make_entry(input_frame, "数学：", 4)
        self.en_entry = self._make_entry(input_frame, "英语：", 6)

        button_frame = tk.Frame(self.root, bg=BG_COLOR)
        button_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 10))
        buttons = (
            ("＋ 添加", "#d9ead3", "#c5e0b4", self.add_student),
            ("✎ 修改", "#fff2cc", "#ffe699", self.modify_student),
            ("✕ 删除", "#f4cccc", "#ea9999", self.delete_student),
            ("🔍 查询", "#cfe2f3", "#9fc5e8", self.query_student),
            ("☰ 列出", "#d9d2e9", "#b4a7d6", self.show_list),
            ("📊 统计", "#fce5cd", "#f9cb9c", self.show_stats),
            ("⟳ 刷新", "#cfe2f3", "#9fc5e8", self.refresh_view),
            ("⎋ 退出", "#e6e6e6", "#d9d9d9", self.exit_app),
        )
        for column, (text, bg, active_bg, command) in enumerate(buttons):
            button_frame.columnconfigure(column, weight=1)
            tk.Button(
                button_frame,
                text=text,
                command=command,
                font=BUTTON_FONT,
                bg=bg,
                activebackground=active_bg,
                relief="raised",
                bd=2,
                padx=6,
                pady=6,
                cursor="hand2",
            ).grid(row=0, column=column, sticky="ew", padx=4, pady=2)

        status = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Microsoft YaHei UI", 10),
            bg=BG_COLOR,
            fg="#666666",
            anchor="w",
        )
        status.grid(row=3, column=0, sticky="ew", padx=44, pady=(0, 4))

        display_frame = tk.Frame(self.root, bg=BG_COLOR)
        display_frame.grid(row=4, column=0, sticky="nsew", padx=40, pady=(0, 24))
        display_frame.rowconfigure(0, weight=1)
        display_frame.columnconfigure(0, weight=1)

        self.display = tk.Text(
            display_frame,
            font=DISPLAY_FONT,
            bg="white",
            fg="#111111",
            relief="sunken",
            bd=1,
            padx=12,
            pady=10,
            wrap="none",
            state="disabled",
            insertbackground="#111111",
        )
        self.display.grid(row=0, column=0, sticky="nsew")

        y_scroll = ttk.Scrollbar(display_frame, orient="vertical", command=self.display.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll = ttk.Scrollbar(display_frame, orient="horizontal", command=self.display.xview)
        x_scroll.grid(row=1, column=0, sticky="ew")
        self.display.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

    def _make_entry(self, parent, label_text, column):
        label = tk.Label(
            parent,
            text=label_text,
            font=LABEL_FONT,
            bg=BG_COLOR,
            fg="#111111",
        )
        label.grid(row=0, column=column, sticky="e", padx=(0 if column == 0 else 12, 4))
        entry = tk.Entry(
            parent,
            font=ENTRY_FONT,
            relief="solid",
            bd=1,
            highlightthickness=0,
            insertbackground="#111111",
        )
        entry.grid(row=0, column=column + 1, sticky="ew", ipady=4)
        return entry

    # ---------- 输入校验 ----------
    def _read_name(self):
        students_name = self.name_entry.get().strip()
        if not students_name:
            raise ValueError("请输入学生姓名！")
        return students_name

    def _read_score(self, entry, subject):
        text = entry.get().strip()
        if not text:
            raise ValueError(f"请输入{subject}成绩！")
        try:
            score = float(text)
        except ValueError:
            raise ValueError(f"{subject}成绩必须是数字！") from None
        if not 0 <= score <= 100:
            raise ValueError(f"{subject}成绩必须在 0~100 之间！")
        return score

    def _read_optional_score(self, entry, subject):
        if not entry.get().strip():
            return None
        return self._read_score(entry, subject)

    def _clear_inputs(self):
        for entry in (self.name_entry, self.ch_entry, self.ma_entry, self.en_entry):
            entry.delete(0, "end")
        self.name_entry.focus_set()

    def _show_error(self, message):
        self.status_var.set("操作失败")
        messagebox.showerror("操作提示", message)

    # ---------- 页面渲染 ----------
    def _set_display(self, content):
        self.display.configure(state="normal")
        self.display.delete("1.0", "end")
        self.display.insert("1.0", content)
        self.display.configure(state="disabled")
        self.display.see("1.0")

    def _row(self, values, widths):
        return "".join(
            pad_text(value, width) for value, width in zip(values, widths)
        ).rstrip()

    def _student_table(self, students):
        name_width = max([18] + [display_width(name) + 4 for name in students])
        widths = (name_width, 10, 10, 10)
        lines = [
            self._row(("姓名", "语文", "数学", "英语"), widths),
            "-" * sum(widths),
        ]
        for students_name, info in students.items():
            lines.append(
                self._row(
                    (
                        students_name,
                        format_score(info["语文"]),
                        format_score(info["数学"]),
                        format_score(info["英语"]),
                    ),
                    widths,
                )
            )
        return "\n".join(lines)

    def _render_list(self):
        if not self.amsy:
            self._set_display("（暂无学生信息）")
            return
        content = f"全部学生（共 {len(self.amsy)} 人）\n\n" + self._student_table(self.amsy)
        self._set_display(content)

    # ---------- 按钮功能 ----------
    def add_student(self):
        try:
            students_name = self._read_name()
            st_sc_ch = self._read_score(self.ch_entry, "语文")
            st_sc_ma = self._read_score(self.ma_entry, "数学")
            st_sc_en = self._read_score(self.en_entry, "英语")
        except ValueError as error:
            self._show_error(str(error))
            return

        if students_name in self.amsy:
            self._show_error(f"学生“{students_name}”已存在，请勿重复添加！")
            return

        self.amsy[students_name] = {
            "语文": st_sc_ch,
            "数学": st_sc_ma,
            "英语": st_sc_en,
        }
        self._clear_inputs()
        self._render_list()
        self.status_var.set(f"添加成功：{students_name}（共 {len(self.amsy)} 人）")

    def modify_student(self):
        try:
            students_name = self._read_name()
        except ValueError as error:
            self._show_error(str(error))
            return

        if students_name not in self.amsy:
            self._show_error(f"学生“{students_name}”不存在，请先添加！")
            return

        try:
            updates = {}
            for subject, entry in zip(
                ST_SUBJECTS, (self.ch_entry, self.ma_entry, self.en_entry)
            ):
                score = self._read_optional_score(entry, subject)
                if score is not None:
                    updates[subject] = score
            if not updates:
                raise ValueError("请至少输入一科要修改的成绩！")
        except ValueError as error:
            self._show_error(str(error))
            return

        self.amsy[students_name].update(updates)
        self._clear_inputs()
        self._render_list()
        self.status_var.set(f"修改成功：{students_name}（共 {len(self.amsy)} 人）")

    def delete_student(self):
        try:
            students_name = self._read_name()
        except ValueError as error:
            self._show_error(str(error))
            return

        if students_name not in self.amsy:
            self._show_error(f"学生“{students_name}”不存在！")
            return

        del self.amsy[students_name]
        self._clear_inputs()
        self._render_list()
        self.status_var.set(f"删除成功：{students_name}（共 {len(self.amsy)} 人）")

    def query_student(self):
        try:
            students_name = self._read_name()
        except ValueError as error:
            self._show_error(str(error))
            return

        if students_name not in self.amsy:
            self._set_display(f"未找到学生：{students_name}")
            self.status_var.set("查询失败：学生不存在")
            messagebox.showerror("查询失败", f"学生“{students_name}”不存在！")
            return

        content = (
            f"查询结果：{students_name}\n\n"
            + self._student_table({students_name: self.amsy[students_name]})
        )
        self._set_display(content)
        self.status_var.set(f"查询成功：{students_name}")

    def show_list(self):
        self._render_list()
        self.status_var.set(f"已列出全部学生（共 {len(self.amsy)} 人）")

    def show_stats(self):
        if not self.amsy:
            self._set_display("（暂无学生数据，无法统计）")
            self.status_var.set("统计失败：暂无学生数据")
            return

        rows = []
        for subject in ST_SUBJECTS:
            scores = {name: info[subject] for name, info in self.amsy.items()}
            values = list(scores.values())
            max_score = max(values)
            min_score = min(values)
            max_names = [name for name, score in scores.items() if score == max_score]
            min_names = [name for name, score in scores.items() if score == min_score]
            average = sum(values) / len(values)
            rows.append(
                (
                    subject,
                    format_score(max_score),
                    "、".join(max_names),
                    format_score(min_score),
                    "、".join(min_names),
                    f"{average:.1f}",
                )
            )

        headers = ("科目", "最高分", "最高分学生", "最低分", "最低分学生", "平均分")
        widths = (
            10,
            10,
            max(24, max(display_width(row[2]) for row in rows) + 4),
            10,
            max(24, max(display_width(row[4]) for row in rows) + 4),
            10,
        )
        lines = [self._row(headers, widths), "-" * sum(widths)]
        for row in rows:
            lines.append(self._row(row, widths))

        content = f"班级成绩统计（共 {len(self.amsy)} 人）\n\n" + "\n".join(lines)
        self._set_display(content)
        self.status_var.set(f"统计完成（共 {len(self.amsy)} 人）")

    def refresh_view(self):
        self._render_list()
        self.status_var.set(f"已刷新（共 {len(self.amsy)} 人）")

    def exit_app(self):
        self.root.destroy()


def main():
    root = tk.Tk()
    TeachingSystemApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
