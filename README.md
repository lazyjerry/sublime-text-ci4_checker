# CodeIgniter 4 PHP File Checker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CodeIgniter 4 PHP File Checker 是一款 Sublime Text 插件，用於檢查 CodeIgniter 4 專案中的 PHP 檔案是否符合命名規範，並檢查類別是否正確通過 `use` 語句引入。

## 功能

- **檔案命名檢查**: 檢查 PHP 檔案是否符合 PascalCase 命名規範。
- **use 語句檢查**: 檢查程式碼中使用到的類別是否正確通過 `use` 語句引入。
- **移除註解與字串干擾**: 自動忽略 PHP 註解和引號內的內容，避免誤判。
- **內建類別過濾**: 自動過濾 PHP 內建類別（如 `Exception`、`DateTime` 等），避免誤報。

## 安裝

1. **下載插件**：
   - 將此專案克隆或下載到 Sublime Text 的插件目錄：
     ```
     git clone https://github.com/你的用戶名/ci4-php-file-checker.git
     ```

2. **重啟 Sublime Text**：
   - 重啟後，插件會自動啟用，並在檔案保存時運行檢查。

## 使用方法

1. 打開一個 CodeIgniter 4 專案中的 PHP 檔案。
2. 修改並保存檔案後，插件會自動檢查檔案的命名規則與 `use` 語句的正確性。
3. 檢查結果：
   - **成功**：狀態列顯示檢查通過訊息。
   - **失敗**：彈出對話框，列出檢查中的錯誤。

## 檢查邏輯

### 檔案命名檢查
檔案名稱需符合以下規範：
- 使用 PascalCase 命名（例如：`MyClass.php`）。
- 必須以 `.php` 結尾。

### 類別使用檢查
檢查以下類別使用情況：
- 靜態方法調用（例如：`ClassName::method()`）。
- 物件創建（例如：`new ClassName()`）。
- PHPDoc 註解中的型別（例如：`@param ClassName`）。
- 動態類別調用（例如：`ClassName::class`）。
- 異常捕獲（例如：`catch (ClassName $e)`）。

內建類別（例如：`Exception`、`DateTime`）將被自動忽略。

## 已知限制

- 不支持處理極為複雜的多行字符串或動態生成的程式碼。
- 需要確保專案遵循標準的 PSR-4 命名規範。

## 貢獻指南

歡迎貢獻此專案！如果有任何問題或建議，請提交 Issue 或 Pull Request。

### 開發步驟
1. 克隆此專案：
git clone https://github.com/lazyjerry/sublime-text-ci4_checker.git
2. 修改代碼並提交 Pull Request。

## 授權

此專案採用 [MIT License](LICENSE)。

---

感謝您使用 CodeIgniter 4 PHP File Checker！
