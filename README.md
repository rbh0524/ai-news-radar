# 📡 AI 新聞雷達

自動蒐集全球 AI 產業、研究與社群最新動態，每 6 小時更新一次。

## 🏗️ 架構

```
Python (RSS 抓取) → Jinja2 (HTML 生成) → GitHub Actions (定時排程) → GitHub Pages (部署)
```

## 📂 專案結構

```
ai-news-site/
├── .github/workflows/
│   └── deploy.yml          # GitHub Actions — 每 6 小時自動部署
├── scripts/
│   ├── fetch_news.py       # RSS 新聞抓取腳本
│   └── generate_site.py    # 靜態 HTML 產生器
├── templates/
│   └── index.html          # Jinja2 HTML 模板
├── data/                   # (自動產生) 新聞 JSON 資料
├── docs/                   # (自動產生) 靜態網站輸出
├── requirements.txt        # Python 套件依賴
└── README.md
```

## 🚀 本地開發

```bash
# 安裝依賴
pip install -r requirements.txt

# 抓取新聞
python scripts/fetch_news.py

# 產生網站
python scripts/generate_site.py

# 預覽
open docs/index.html
# 或
python -m http.server 8000 -d docs
```

## 📡 新聞來源

| 來源 | 分類 |
|------|------|
| TechCrunch AI | Industry |
| The Verge AI | Technology |
| MIT Technology Review | Research |
| Google AI Blog | Research |
| OpenAI Blog | Research |
| Ars Technica | Technology |
| VentureBeat AI | Industry |
| Hacker News | Community |

## ⚙️ GitHub Pages 設定

1. 在 GitHub 建立 repo 並推送程式碼
2. 前往 **Settings → Pages**
3. Source 選 **GitHub Actions**
4. 完成！每次 push 或每 6 小時會自動更新

## 📄 授權

MIT License
