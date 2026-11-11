# WhatsApp 客服 AI 工作流 V2.0

把本專案的 [最新版本連結](https://github.com/collieai-g/whatsapp-customer-service-agent/releases/latest) 交給你的 AI。發行頁的 `whatsapp-customer-service-agent.zip` 包含完整工作流。AI 可從連結下載後按 [啟動指引](START_HERE.md) 設定，也可以直接讀取你上傳的 ZIP。

工作流可免費下載及使用。執行需要有瀏覽器操作、私人狀態保存和排程能力的 AI 主機。AI 主機如有費用，按所用方案計算。WhatsApp Web 的帳戶連結由你本人完成。

## 預設設定

| 項目 | 預設值 |
| --- | --- |
| 巡查頻率 | 每 5 分鐘 |
| 營業時段 | 香港時間，每天全天 |
| 首次或無待答時觀察 | 30 秒 |
| 成功回覆後再觀察 | 30 秒，每次成功回覆重新計時 |
| 觀察時等待 | 每次等待最多 10 秒再檢查，接近期限時縮短等待 |
| 自動發送上限 | 每輪每個對話 3 次，全輪合共 10 次 |
| 文字及補問上限 | 每則 600 字，每次最多 2 個補問 |

告訴 AI 你的公司及希望修改的設定，例如「香港時間星期一至五 09:00–18:00，每 10 分鐘巡查，回覆後觀察 20 秒」。AI 會在私人公司設定保存修改。授權啟用時，AI 使用主機的原生工具建立或更新排程，再讀回頻率及狀態。

## 版本與檔案

- [啟動指引](START_HERE.md) 供接收連結或 ZIP 的 AI 閱讀。
- [預設設定](settings.defaults.json) 提供可讀取的巡查、觀察及回覆上限。
- [公司設定範本](portable/company-profile.example.json) 供匯入或對話式設定。
- [驗收清單](portable/ACCEPTANCE.md) 說明如何核對帳戶、設定、排程及傳送結果。

更新版本時，在儲存庫根目錄執行 `python tools/build_release.py --output-dir <輸出目錄>`，把產生的 ZIP 及 SHA-256 檔加入 GitHub Release。每個 Release 沿用同一個 ZIP 附件名稱。給使用者最新版本頁即可接續下載，個別版本也可以用發行頁固定連結分享。
