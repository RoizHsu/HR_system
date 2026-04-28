# HR 系統跨平台部署指南

## 📋 環境需求

- **Python**: 3.10+ 
- **Node.js**: 16+
- **系統**: Windows / macOS / Linux

---

## 🔧 後端設置 (Django)

### 步驟 1: 建立虛擬環境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 步驟 2: 安裝依賴（跨平台）

```bash
# 升級 pip
pip install --upgrade pip setuptools

# 方法 A：直接安裝（推薦）
pip install -r requirements.txt

# 方法 B：使用 pip-compile（開發者）
pip install pip-tools
pip-compile requirements.in -o requirements.txt --resolver=backtracking
pip install -r requirements.txt
```

### 步驟 3: 初始化資料庫

```bash
python manage.py migrate
```

### 步驟 4: 建立超級使用者（可選）

```bash
python manage.py createsuperuser
```

### 步驟 5: 啟動後端服務

```bash
python manage.py runserver 0.0.0.0:8000
```

後端會運行在 `http://127.0.0.1:8000`

---

## 🎨 前端設置 (Vue.js)

### 步驟 1: 安裝依賴

```bash
cd HR_web
npm install
```

### 步驟 2: 啟動開發服務器

```bash
npm run dev
```

前端會運行在 `http://localhost:5173`

---

## 🔌 CORS 和跨域問題排查

### 已配置的 CORS 白名單

後端 (`settings.py`) 已設定允許以下來源：
- `http://localhost:5173`
- `http://127.0.0.1:5173`

### 如果遇到 CORS 錯誤

#### 1️⃣ 檢查後端是否運行

```bash
curl http://127.0.0.1:8000/api/
```

應該看到 API 回應（可能是 401 Unauthorized，這是正常的）

#### 2️⃣ 檢查前端 API 端點

打開瀏覽器開發者工具（F12），在 Network 標籤檢查請求：
- 看看是否發送到正確的 URL
- 查看響應頭是否包含 `Access-Control-Allow-Origin`

#### 3️⃣ 如果需要臨時允許所有來源

編輯 `HR_system/settings.py`：

```python
# 臨時調試用（！不要在生產環境使用！）
CORS_ALLOW_ALL_ORIGINS = True
```

然後重啟 Django 伺服器。

---

## 📦 依賴管理

### 添加新套件

1. **編輯 `requirements.in`**：
   ```
   your-package>=1.0.0
   ```

2. **重新編譯**：
   ```bash
   pip-compile requirements.in -o requirements.txt --resolver=backtracking
   ```

3. **安裝**：
   ```bash
   pip install -r requirements.txt
   ```

### 為什麼使用 pip-tools？

- ✅ **跨平台相容**：自動解析依賴，避免系統差異
- ✅ **安全可控**：明確列出所有間接依賴
- ✅ **易於更新**：修改 `requirements.in` 後自動同步
- ✅ **版本固定**：完整記錄版本，便於復現

---

## 🧪 檢查清單

完成以下檢查確保系統正常運行：

- [ ] 虛擬環境已激活（macOS/Linux 看 prompt 前的 `(venv)`）
- [ ] 後端依賴已安裝：`pip list | grep django`
- [ ] 資料庫已遷移：`python manage.py migrate`
- [ ] 後端服務已運行：`python manage.py runserver`
- [ ] 前端依賴已安裝：`npm list` 有輸出
- [ ] 前端開發伺服器已運行：`npm run dev`
- [ ] CORS 已配置：檢查 `settings.py` 中的 `CORS_ALLOWED_ORIGINS`
- [ ] 前端能訪問後端 API：瀏覽器能打開 `http://127.0.0.1:8000/api/`

---

## 🆘 常見問題

### Q: 執行 `python -m venv venv` 失敗
**A**: 請確認：
- Python 版本 ≥ 3.10
- 路徑沒有特殊字符
- 有資料夾寫入權限

### Q: `django-cors-headers` 未安裝
**A**: 運行 `pip install -r requirements.txt` 重新安裝

### Q: 前端無法連接後端
**A**: 檢查：
1. 後端是否在 `http://127.0.0.1:8000` 運行
2. 瀏覽器開發者工具看 Network 標籤
3. 查看後端終端是否有錯誤訊息

### Q: Windows 和 macOS 安裝不同套件版本
**A**: 使用 `pip-tools` 管理依賴：
```bash
pip-compile requirements.in -o requirements.txt
pip install -r requirements.txt
```

---

## 📝 開發工作流

### 日常開發

```bash
# 終端 1：後端
cd HR_system
source venv/bin/activate  # Windows: venv\Scripts\activate
python manage.py runserver

# 終端 2：前端
cd HR_web
npm run dev
```

### 添加新依賴

```bash
cd HR_system
echo "new-package==1.0.0" >> requirements.in
pip-compile requirements.in
pip install -r requirements.txt
# 提交 requirements.txt 和 requirements.in
```

---

✅ 設置完成！現在可以開始開發了~ 🚀
