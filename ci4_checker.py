import os
import sublime
import sublime_plugin
import re

class Ci4FileCheckerCommand(sublime_plugin.EventListener):
    def on_post_save_async(self, view):
        """
        監聽檔案保存事件，並在檔案保存後執行檢查。
        檢查是否是 PHP 檔案，是否是 CodeIgniter 4 專案，
        並執行命名規則與 use 語句檢查。
        """
        # 檢查檔案名稱和類型
        file_name = view.file_name()
        if not file_name or not file_name.endswith(".php"):
            self.show_success_message(view, "檢查完成，這不是 PHP 檔案")
            return

        # 確認是否是 CodeIgniter 4 專案
        project_root = self.get_project_root(file_name)
        if not project_root:
            self.show_success_message(view, "檢查完成，無法找到 `.env` 文件，此專案可能不是 CodeIgniter 4 專案")
            return

        # 檢查是否符合 CodeIgniter 4 資料夾結構
        is_ci4 = self.is_codeigniter4_project(project_root)
        if not is_ci4:
            self.show_success_message(view, "檢查完成，此專案不是 CodeIgniter 4 專案")
            return

        # 執行檢查邏輯
        self.show_success_message(view, "檢測到 CodeIgniter 4 PHP 檔案，開始執行檢查")
        view.erase_status("ci4_check")
        errors = []
        errors.extend(self.check_file_naming(view))
        errors.extend(self.check_use_statements(view))

        # 根據檢查結果顯示提示
        if not errors:
            self.show_success_message(view, "CodeIgniter 4 PHP 檔案檢查完成，未發現任何問題！")
        else:
            self.show_error_message("\n\n".join(errors))

    def check_file_naming(self, view):
        """
        檢查檔案名稱是否符合 CodeIgniter 4 命名規則（PascalCase）。
        """
        errors = []
        file_name = view.file_name()
        base_name = os.path.basename(file_name)

        # 匹配 PascalCase 命名規則
        if not re.match(r"^[A-Z][a-zA-Z0-9]*\.php$", base_name):
            errors.append(
                f"檔案命名錯誤: {base_name}\n\n請使用 PascalCase 並以 .php 結尾。\n\n例如：MyClass.php"
            )
        return errors

    def check_use_statements(self, view):
        """
        檢查檔案中的 use 語句是否包含所有使用到的類別。
        """
        errors = []
        # 獲取檔案內容
        content = view.substr(sublime.Region(0, view.size()))

        # 提取所有 use 語句
        use_statements = re.findall(r"^use\s+([^;]+);", content, re.MULTILINE)

        # 建立類別別名字典（從 use 語句提取類別名）
        use_map = {u.split("\\")[-1]: u for u in use_statements}

        # 移除 PHP 註解和引號內容
        content = self.remove_php_comments(content)

        # 提取程式碼中實際使用的類別
        used_classes = self.extract_used_classes(content)

        # 找出使用到但未通過 use 引入的類別
        missing_classes = used_classes - set(use_map.keys())
        for cls in missing_classes:
            errors.append(f"`{cls}` 類別未通過 `use` 引入，請檢查檔案內容。")

        return errors

    def extract_used_classes(self, content):
        """
        從程式碼中提取使用到的類別名稱，包括靜態調用、物件創建、型別提示等。
        """
        # 使用正則表達式匹配類別使用場景
        pattern = r"""
            (\\?[A-Z][a-zA-Z0-9_\\]+)::|           # 靜態方法調用，支持完整命名空間
            ([A-Z][a-zA-Z0-9_]+)::|               # 靜態方法調用
            new\s+([A-Z][a-zA-Z0-9_]+)|           # 物件使用 new 方法創建
            @(?:var|param|return)\s+([A-Z][a-zA-Z0-9_]*)|  # PHPDoc 註解
            ([A-Z][a-zA-Z0-9_]*)::class|          # 動態調用與反射
            catch\s*\(\s*([A-Z][a-zA-Z0-9_]*)\s*\$ # 異常捕獲
        """
        matches = re.findall(pattern, content, re.VERBOSE)

        # 展平結果並過濾掉 None 值
        all_classes = {cls for match in matches for cls in match if cls}

        # 過濾掉完整命名空間（\開頭）的類別
        used_classes = {cls for cls in all_classes if not cls.startswith("\\")}
        return used_classes

    def remove_php_comments(self, content):
        """
        移除 PHP 程式碼中的註解（單行與多行）以及引號中的內容。
        """
        # 正則表達式匹配註解和引號內容
        pattern = r"""
            /\*[\s\S]*?\*/ |           # 多行註解
            //.*?$ |                   # 單行註解
            #.*?$ |                    # 另一種單行註解
            "(?:\\.|[^"\\])*" |        # 雙引號中的內容
            '(?:\\.|[^'\\])*'          # 單引號中的內容
        """
        return re.sub(pattern, "", content, flags=re.MULTILINE | re.VERBOSE)

    def get_project_root(self, file_path):
        """
        獲取專案根目錄，通過檢測是否存在 `.env` 文件確定。
        """
        current_dir = os.path.dirname(file_path)
    
        while current_dir:
            env_path = os.path.join(current_dir, ".env")
            if os.path.exists(env_path):
                 return current_dir
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                break  # 已達根目錄
            current_dir = parent_dir

        return None

    def is_codeigniter4_project(self, directory):
        """
        檢查目錄是否符合 CodeIgniter 4 專案的基本結構。
        必須包含以下目錄和檔案：
        - `app/`
        - `system/`
        - `public/` 或 `writable/`
        """
        required_paths = ["app","writable"]
        optional_paths = ["public","vendor"]

        for path in required_paths:
            if not os.path.isdir(os.path.join(directory, path)):
                return False

        for path in optional_paths:
            if os.path.isdir(os.path.join(directory, path)):
                return True  # 找到至少一個可選目錄即確認為 CI4 專案

        return False

    def show_error_message(self, message):
        """
        顯示錯誤訊息對話框，提醒使用者檢查問題。
        """
        sublime.message_dialog(f"------ CodeIgniter 4 Checker ------\n\n{message}\n")

    def show_success_message(self, view, message):
        """
        顯示成功訊息於 Sublime Text 的狀態列。
        """
        view.set_status("ci4_check", f"------ CodeIgniter 4 Checker ------ {message}------\n")
        sublime.set_timeout(lambda: view.erase_status("ci4_check"), 5000)
        # sublime.message_dialog(f"------ CodeIgniter 4 Checker ------\n\n{message}\n")
