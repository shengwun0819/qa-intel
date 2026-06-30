# qa-intel 知識庫

qa-intel 所有 skill 共用的結構化知識儲存區。

---

## 目錄結構

```
knowledge/
└── repos/
    ├── <repo-name>.md    # 由 /repo-scout 建立，每個 repo 一個檔案
    └── ...
```

---

## 知識檔案格式

每個 `repos/<repo-name>.md` 包含：

| 欄位 | 說明 |
|------|------|
| Frontmatter | repo 名稱、路徑/URL、掃描日期、類型 |
| 概覽 | Repo 用途與定位 |
| 技術棧 | 語言、框架、主要依賴 |
| 目錄結構 | 根目錄一層說明 |
| 核心模組 | 最重要的 3–7 個模組與職責 |
| API / 介面 | 主要 endpoints 或介面 |
| 測試結構 | 框架、目錄、覆蓋概況 |
| 關鍵慣例與注意事項 | 命名慣例、設計決策、已知坑 |
| 已知風險模組 | 邏輯複雜或測試薄弱的模組 |

---

## 如何建立 / 更新知識

執行 `/repo-scout`，提供 repo 路徑或 GitHub URL。

## 哪些 skill 會讀取知識庫

| Skill | 讀取方式 |
|-------|---------|
| `/risk-analyzer` | 讀取對應 repo 知識，輔助風險判斷 |
| `/gen-test-cases` | 讀取對應 repo 知識，補充測試背景 |

---

## 知識時效性

知識庫是掃描當下的快照。若 repo 有重大變更（架構調整、新模組），建議重新執行 `/repo-scout` 更新。
`last-scanned` 欄位記錄上次掃描日期，可作為判斷是否需要更新的依據。
