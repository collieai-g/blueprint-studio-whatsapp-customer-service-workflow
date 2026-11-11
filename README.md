# Blueprint Studio WhatsApp Customer Service Workflow

**藍圖工作室 WhatsApp 客戶服務工作流**

由藍圖工作室開發，供 AI 按你的公司資料和回覆政策定時巡查 WhatsApp Web、處理待回覆訊息及核對發送結果。

[**下載工作流 ZIP**](https://github.com/collieai-g/blueprint-studio-whatsapp-customer-service-workflow/releases/latest/download/whatsapp-customer-service-agent.zip)

## 開始使用

1. 把 ZIP 交給你的 AI，請它先讀取 `START_HERE.md`。也可以把發行頁連結直接交給 AI，讓它取得 ZIP。[最新發行頁](https://github.com/collieai-g/blueprint-studio-whatsapp-customer-service-workflow/releases/latest)
2. AI 開啟 WhatsApp Web，由你本人用手機掃碼。已有登入分頁時，AI 核對帳戶後即可沿用。
3. 在對話中告訴 AI 你的公司、服務、回覆範圍及政策。AI 整理公司設定供你核對，也可匯入你已有的設定。
4. 按你已授權的巡查及發送範圍，AI 使用主機原生功能建立或更新排程，讀回巡查頻率和啟用狀態，再執行首輪。已有一輪開始時沿用該輪，其後由排程接續。

工作流可免費下載及使用。執行需要能操作瀏覽器、保存私人狀態和管理原生排程的 AI 主機。主機如有費用，按所用方案計算。排程、實際觸發及訊息送達以各自的執行結果核對。

## English quick start

Blueprint Studio developed this workflow for scheduled WhatsApp Web customer service. Download the ZIP and ask your AI to read `START_HERE.md`. Link your WhatsApp account and describe your business and reply policy in chat. After you authorize automation, a host with browser access, private state storage and native scheduling can set up and verify recurring message checks.

## V2 預設設定

| 項目 | 預設值 |
| --- | --- |
| 巡查頻率 | 每 5 分鐘 |
| 營業時段 | 香港時間（`Asia/Hong_Kong`），每天全天 |
| 首次或無待答時觀察 | 30 秒 |
| 成功回覆後再觀察 | 30 秒，每次成功回覆重新計時 |
| 觀察時等待 | 每次最多 10 秒再檢查，接近期限時按剩餘時間縮短 |
| 每輪發送上限 | 每個對話 3 次，全輪合共 10 次 |
| 每則回覆上限 | 600 字元，最多 2 個補問 |

你可以直接說「香港時間星期一至五 09:00–18:00，每 10 分鐘巡查，回覆後觀察 20 秒」。AI 把修改保存到私人公司設定，再按核對後的設定建立或更新排程。營業時段外的待回覆事項留到下一個可處理輪次。

## 版本與檔案

v2.0.1 更新專案名稱與使用文件。

- 收到連結或 ZIP 的 AI 從啟動指引開始。[啟動指引](START_HERE.md)
- 預設設定包含巡查頻率、營業時段、觀察及回覆上限。[預設設定](settings.defaults.json)
- 公司設定範本可供匯入或用於對話式設定。[公司設定範本](portable/company-profile.example.json)
- 驗收清單說明如何核對帳戶、設定、排程和傳送結果。[驗收清單](portable/ACCEPTANCE.md)

## 維護發行版本

在儲存庫根目錄執行 `python tools/build_release.py --output-dir <輸出目錄>`，把產生的 ZIP 和 SHA-256 檔加入 GitHub Release。每個版本沿用 `whatsapp-customer-service-agent.zip` 附件名稱，讓本頁的下載連結指向最新發行版本。分享固定版本時，使用該版本的發行頁連結。
