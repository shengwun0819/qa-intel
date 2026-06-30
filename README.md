# qa-intel

個人 QA 智慧工具集——以 AI agent 驅動的測試案例產出、風險評估與 codebase 知識管理。

設計為**可攜式個人工具**：帶著走，每家公司用 `/repo-scout` 建立知識庫，核心方法論不變。

→ 第一次使用？查看 [docs/scenarios.html](docs/scenarios.html) 了解所有使用情境。

---

## 架構概覽

```
qa-intel/
├── skills/
│   ├── repo-scout/       # Skill：掃描 repo → 建立知識庫
│   ├── risk-analyzer/    # Skill：PR / branch 風險評估
│   └── gen-test-cases/   # Skill：產出手動測試案例
├── knowledge/
│   └── repos/            # 知識庫（由 repo-scout 寫入，不上傳至 git）
└── agents/
    └── repo-reader/      # Sub-agent：codebase 深度閱讀（被 repo-scout 呼叫）
```

---

## 可用 Skills

| Skill | 指令 | 說明 |
|-------|------|------|
| repo-scout | `/repo-scout` | 掃描 repo，建立結構化知識庫快照 |
| risk-analyzer | `/risk-analyzer` | 分析 PR / branch 的開發風險，可結合 Scrum Tool的 AC |
| gen-test-cases | `/gen-test-cases` | 從 task 或需求描述產出手動測試案例 |

---

## 安裝

```bash
# 安裝為 Claude Code plugin
claude plugin install https://github.com/your-username/qa-intel
```

或 clone 後手動安裝：

```bash
git clone https://github.com/your-username/qa-intel ~/.claude/plugins/qa-intel
```

---

## 快速開始

### Step 1：讓 qa-intel 了解你的 repo

```
/repo-scout
> repo 路徑：/path/to/your/repo
> 模式：comprehensive（初次建議）
```

產出：`knowledge/repos/<repo-name>.md`（本機保存，不上傳至 git）

### Step 2：分析開發風險（merge 前）

```
/risk-analyzer
> PR URL 或 branch：feat/your-feature
> Task ID：abc123（選填，有則分析 AC 覆蓋缺口）
```

### Step 3：產出測試案例

```
/gen-test-cases
> Task ID 或直接描述需求
> 測試階段：Development 或 Verification
```

---

## 典型工作流程

### Sprint 開始
```
/repo-scout（建立或更新知識庫）
```

### Feature 開發中（RD）
```
/risk-analyzer（branch + Task）
→ 確認實作方向是否符合 AC
→ 提早發現遺漏的邊界條件
```

### PR Review 前（QA）
```
/risk-analyzer（PR URL + Task）
→ 確認 AC 全部有對應實作
→ 識別需要重點測試的高風險模組
```

### 測試準備（QA）
```
/gen-test-cases（Task ID）
→ 產出完整 Verification phase 測試案例
→ 自動寫入 Scrum Tool（ClickUp / Jira）
```

---

## 環境需求

| 工具 | 用途 | 必要性 |
|------|------|--------|
| Claude Code CLI | 執行所有 skill | 必要 |
| `gh` CLI（已登入） | `risk-analyzer` 讀取 private PR diff | PR 分析時需要 |
| Scrum Tool API Token | gen-test-cases 讀寫 Scrum Tool | 依 `pm_tool` 設定 |

---

## 知識庫說明

`knowledge/repos/` 下每個 `.md` 檔案代表一個 repo 的知識快照，包含：

- Repo 概覽與定位、技術棧
- 目錄結構與各目錄職責
- 核心模組說明與 API / 介面清單
- 測試結構與覆蓋狀況
- **已知風險模組**（影響 risk-analyzer 分析重點）

知識庫是時間快照，不上傳至 git（由 `.gitignore` 排除）。  
repo 有重大架構調整時執行 `/repo-scout` 更新。

---

## Token 消耗參考

| 操作 | 預估 token |
|------|-----------|
| `/repo-scout` Comprehensive（中型 repo） | 20k – 80k |
| `/repo-scout` Quick | 3k – 8k |
| `/risk-analyzer`（有知識庫 + PR + Task） | 10k – 30k |
| `/gen-test-cases` Verification phase | 8k – 20k |

---

## 未來規劃

- Phase 1：輸入自動化（自動偵測當前 branch PR、從 branch 名稱萃取 Task ID）
- Phase 2：risk-analyzer → gen-test-cases 直接銜接（風險報告自動轉為測試重點）
- Phase 3：更多 Scrum Tool支援（Jira、Linear）
- Phase 4：Integration / E2E Test 自動產出
