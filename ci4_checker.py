import os
import sublime
import sublime_plugin
import re
import json

class Ci4FileCheckerCommand(sublime_plugin.EventListener):
    def on_post_save_async(self, view):
        # 檢查是否是 PHP 檔案
        file_name = view.file_name()
        if not file_name or not file_name.endswith(".php"):
            self.show_success_message(view, "檢查完成，這不是 PHP 檔案")
            return

        # 確認是否為 CodeIgniter 4 專案
        project_root = self.get_project_root(file_name)
        if not project_root:
            self.show_success_message(view, "檢查完成，無法找到 `.env` 文件，此專案可能不是 CodeIgniter 4 專案")
            return

        # 執行檢查
        self.show_success_message(view, "檢測到Codeigniter4 PHP 檔案，開始執行檢查")
        view.erase_status("ci4_check")
        errors = []
        errors.extend(self.check_file_naming(view))
        errors.extend(self.check_use_statements(view))

        # 如果沒有錯誤，顯示檢查無誤的提示
        if not errors:
            self.show_success_message(view, "Codeigniter4 PHP 檔案檢查完成，未發現任何問題！")
        else:
            self.show_error_message("\n\n".join(errors))

    def check_file_naming(self, view):
        errors = []
        file_name = view.file_name()
        base_name = os.path.basename(file_name)
        
        # CodeIgniter 4 檔案命名規則（例如駝峰式或 PascalCase）
        if not re.match(r"^[A-Z][a-zA-Z0-9]*\.php$", base_name):
            errors.append(
                f"檔案命名錯誤: {base_name}\n\n請使用 PascalCase 並以 .php 結尾。\n\n例如：MyClass.php"
            )
        return errors

    def check_use_statements(self, view):
        errors = []
        content = view.substr(sublime.Region(0, view.size()))

        # 提取所有 use 語句
        use_statements = re.findall(r"^use\s+([^;]+);", content, re.MULTILINE)

        # 建立類別別名字典（如 use Some\Namespace\Class as Alias）
        use_map = {u.split("\\")[-1]: u for u in use_statements}

        # 去除 PHP 註解內容
        content = self.remove_php_comments(content)

        # 使用的類別集合
        used_classes = self.extract_used_classes(content)

        # 找出未通過 use 引入的類別
        missing_classes = used_classes - set(use_map.keys())
        for cls in missing_classes:
            errors.append(f"`{cls}` 類別未通過 `use` 引入，請檢查檔案內容。")

        return errors

    def extract_used_classes(self, content):
        """從程式碼中提取使用到的類別名稱"""
        # 單次匹配提取所有類別使用場景
        pattern = r"""
            ([A-Z][a-zA-Z0-9_]+)::|               # 靜態調用 (::)
            new\s+([A-Z][a-zA-Z0-9_]+)|           # 物件調用 (new)
            @(?:var|param|return)\s+([A-Z][a-zA-Z0-9_]*)|  # PHPDoc 註解
            ([A-Z][a-zA-Z0-9_]*)::class|          # 動態調用與反射
            catch\s*\(\s*([A-Z][a-zA-Z0-9_]*)\s*\$ # 異常捕獲
        """
        matches = re.findall(pattern, content, re.VERBOSE)

        # 將所有匹配結果展平並過濾 None 值
        all_classes = {cls for match in matches for cls in match if cls}

        # 過濾掉完整命名空間（\開頭）的類別
        used_classes = {cls for cls in all_classes if not cls.startswith("\\")}
        return used_classes
        
        # used_classes = set()
        # # 搜尋靜態調用 (::)
        # static_calls = re.findall(r"([A-Z][a-zA-Z0-9_]+)::", content)
        # used_classes.update(static_calls)

        # # 搜尋物件調用 (->)
        # object_calls = re.findall(r"new\s+([A-Z][a-zA-Z0-9_]+)", content)
        # used_classes.update(object_calls)

        # # 檢查型別提示
        # type_hints = re.findall(r"(?::|)\s*\(?([A-Z][a-zA-Z0-9_]*)\)?", content)
        # used_classes.update(type_hints)

        # # 檢查 PHPDoc 註解
        # phpdoc_classes = re.findall(r"@(var|param|return)\s+([A-Z][a-zA-Z0-9_]*)", content)
        # used_classes.update([cls for _, cls in phpdoc_classes])

        # # 檢查動態調用與反射
        # dynamic_calls = re.findall(r"([A-Z][a-zA-Z0-9_]*)::class", content)
        # used_classes.update(dynamic_calls)

        # # 檢查異常捕獲
        # exceptions = re.findall(r"catch\s*\(\s*([A-Z][a-zA-Z0-9_]*)\s*\$", content)
        # used_classes.update(exceptions)

        # return used_classes

    def remove_php_comments(self, content):
        """移除 PHP 程式碼中的註解（單行與多行）。"""
        # 移除單行註解與多行註解
        # pattern = r"(?:/\*[\s\S]*?\*/)|(?://.*?$)|(?:#.*?$)"
        # return re.sub(pattern, "", content, flags=re.MULTILINE)
        
        """移除 PHP 程式碼中的註解與引號內容（單行與多行）。"""
        # 匹配並移除單行註解、多行註解以及引號內容
        pattern = r"""
            /\*[\s\S]*?\*/ |           # 多行註解
            //.*?$ |                   # 單行註解
            #.*?$ |                    # 另一種單行註解
            "(?:\\.|[^"\\])*" |        # 雙引號中的內容
            '(?:\\.|[^'\\])*'          # 單引號中的內容
        """
        return re.sub(pattern, "", content, flags=re.MULTILINE | re.VERBOSE)

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
        sublime.message_dialog(f"------ CodeIgniter 4 Checker ------\n\n{message}\n")

    def show_success_message(self, view, message):
        """顯示成功訊息於狀態列。"""
        view.set_status("ci4_check", f"------ CodeIgniter 4 Checker ------ {message}------\n")
        # 設置一段時間後清除狀態列訊息（例如 5 秒）
        sublime.set_timeout(lambda: view.erase_status("ci4_check"), 5000)
