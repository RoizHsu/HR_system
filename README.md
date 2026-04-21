# HR 簡易系統 (HR Management System)

這是一個基於**前後端分離架構**開發的簡易人力資源管理系統 (HR System)。
前端採用 **Vue.js** 提供高互動性與流暢的使用者體驗，後端則使用 **Django** (Python) 負責強大且安全的商業邏輯處理與 API 服務。

## 🛠 技術棧 (Tech Stack)

### 前端 (Frontend)
* **核心框架**: Vue.js
* **架構特色**: 採用組件化 (Component-based) 開發的單頁應用程式 (SPA)，讓畫面切換更快速平滑。
* **資料溝通**: 透過 `Axios` 或 `Fetch API` 向後端發送 HTTP 請求，進行資料的非同步更新。

### 後端 (Backend)
* **核心框架**: Python + Django
* **API 架構**: Django REST Framework (DRF)
* **架構特色**: 負責資料庫模型定義 (ORM)、業務邏輯運算、使用者身份驗證與權限控管 (Authentication & Authorization)。

## 🏗 系統架構設計 (Architecture)

本專案採用前後端完全分離的設計模式，運作流程如下：
1. **獨立運行**：Vue.js 前端專注於畫面渲染、狀態管理 (State Management) 與路由控制；Django 後端則專注於資料處理，作為純粹的 API 伺服器。
2. **RESTful API 溝通**：前端透過發送帶有 JSON 格式的 HTTP 請求 (GET, POST, PUT, DELETE) 給 Django 的 API 端點。
3. **跨域處理 (CORS)**：後端配置了 `django-cors-headers`，允許前端應用程式跨域請求後端資源。
4. **低耦合高擴展**：前後端代碼分離，不僅提升了開發效率，也方便未來獨立升級或抽換技術棧。

## ✨ 主要功能 (Features)
* 員工基本資料管理 (新增、查詢、修改、刪除)
* 簡易打卡與出缺勤紀錄
* 系統權限控管 (HR 管理員與一般員工)

---

## 🚀 快速啟動 (Getting Started)

### 1. 後端啟動 (Django)
請確保你的環境已安裝 Python 3.x。
```bash
# 1. 進入後端專案目錄
cd <後端目錄名稱>

# 2. 建立並啟動虛擬環境 (建議)
python -m venv venv
source venv/bin/activate  # Windows 請使用 venv\Scripts\activate

# 3. 安裝依賴套件
pip install -r requirements.txt

# 4. 執行資料庫遷移
python manage.py migrate

# 5. 啟動開發伺服器
python manage.py runserver
```
*(後端預設運行於 `http://127.0.0.1:8000/`)*

### 2. 前端啟動 (Vue)
請確保你的環境已安裝 Node.js 與 npm。
```bash
# 1. 進入前端專案目錄
cd <前端目錄名稱>

# 2. 安裝依賴套件
npm install

# 3. 啟動開發伺服器
npm run serve
```
*(前端預設運行於 `http://localhost:8080/`)*


## 後端django

<img width="301" height="522" alt="image" src="https://github.com/user-attachments/assets/834fae2d-ed8e-43f5-80c6-2f7965686e92" />
更新20260410

---
## 前端vue
### 首頁
<img width="1876" height="739" alt="image" src="https://github.com/user-attachments/assets/c0824798-33c9-4fc6-85ae-c33c8c719dfa" />


### 登入
<img width="649" height="333" alt="image" src="https://github.com/user-attachments/assets/dc7b8ff3-cdd4-4c6c-85b3-7c7bc8821b5b" />


### 註冊
<img width="627" height="753" alt="image" src="https://github.com/user-attachments/assets/eb69e9c0-dd4f-47d9-a865-697e47f6fa4b" />

### HR系統切換
<img width="579" height="344" alt="image" src="https://github.com/user-attachments/assets/912b5f82-c946-4f9e-8542-5a72e8c25515" />


### 首頁選單
<img width="218" height="204" alt="image" src="https://github.com/user-attachments/assets/149913c5-3e2c-4bff-8a29-9e2fdb82a439" />


### 網頁
<img width="1276" height="358" alt="image" src="https://github.com/user-attachments/assets/fc00ceef-8e8c-4ac7-aa6c-63dbbe0ec003" />


### 打卡紀錄
<img width="1317" height="266" alt="image" src="https://github.com/user-attachments/assets/61392643-4f55-4c2b-b8d9-477ac4e816e5" />
### 新增提早打卡
<img width="374" height="78" alt="image" src="https://github.com/user-attachments/assets/2e645e3a-e8f8-471a-9530-24a672ef713a" />
<img width="569" height="376" alt="image" src="https://github.com/user-attachments/assets/2a33933f-5c9e-465f-a626-0d395a74e7d1" />
### 休假紀錄
<img width="1908" height="246" alt="image" src="https://github.com/user-attachments/assets/ec0e1700-32ec-4654-ba5d-f58a0b42e1e7" />


### 加班紀錄
<img width="1225" height="398" alt="image" src="https://github.com/user-attachments/assets/df5a1e67-bceb-4589-a207-c0a24aee2716" />


### 修改資料
<img width="1295" height="712" alt="螢幕擷取畫面 2026-04-10 110536" src="https://github.com/user-attachments/assets/b78557c5-cf40-4fee-89a3-1e88f9d5a6b9" />


---

