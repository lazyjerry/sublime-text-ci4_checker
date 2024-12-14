import os
import sublime
import sublime_plugin
import re

class Ci4FileCheckerCommand(sublime_plugin.EventListener):
    def on_post_save_async(self, view):
        # 檢查是否是 PHP 檔案
        file_name = view.file_name()
        if not file_name.endswith(".php"):
            return

        # 確認是否為 CodeIgniter 4 專案
        project_root = self.get_project_root(file_name)
        if not project_root:
            return

        # 執行檢查
        self.check_file_naming(view)
        self.check_use_statements(view, project_root)
        show_error_message(f"檢查完畢沒問題")

    def check_file_naming(self, view):
        file_name = view.file_name()
        base_name = os.path.basename(file_name)
        
        # CodeIgniter 4 檔案命名規則（例如駝峰式或 PascalCase）
        if not re.match(r"^[A-Z][a-zA-Z0-9]*\.php$", base_name):
            self.show_error_message(
                f"檔案命名錯誤: {base_name}\n\n請使用 PascalCase 並以 .php 結尾。\n\n例如：MyClass.php"
            )

    def check_use_statements(self, view, project_root):
        content = view.substr(sublime.Region(0, view.size()))
        use_statements = re.findall(r"^use\s+([^;]+);", content, re.MULTILINE)

        # 模擬檢查用到的 `use` 是否存在於專案的相關路徑
        errors = []
        for statement in use_statements:
            class_path = statement.replace("\\", os.sep) + ".php"
            if not os.path.exists(os.path.join(project_root, class_path)):
                errors.append(f"`use {statement}` 的路徑無法解析到實際檔案。")

        if errors:
            self.show_error_message(
                "以下 `use` 語句存在問題：\n\n" + "\n".join(errors) +
                "\n\n請檢查相對應的檔案是否存在並正確命名。"
            )

    def get_project_root(self, file_path):
        # 偵測專案根目錄（有 .env 檔案）
        current_dir = os.path.dirname(file_path)
        while current_dir:
            if os.path.exists(os.path.join(current_dir, ".env")):
                return current_dir
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                break
            current_dir = parent_dir
        return None

    def show_error_message(self, message):
        """顯示警告對話框，提醒使用者修正錯誤。"""
        sublime.message_dialog(f"CodeIgniter 4 檢查錯誤\n\n{message}")
