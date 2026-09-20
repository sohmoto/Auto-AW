# Auto-AW

Auto-AWは、GitHub Issueに自然言語で投稿された調査依頼を、GitHub Agentic Workflowsで調査レポートへ変換するためのprivate repositoryです。

## 利用方法

1. GitHub MobileまたはGitHub Webで新しいIssueを作成します
2. タイトルに調べたいテーマを書きます
3. 本文に目的、対象、期間、比較したい観点などを自由な文章で書きます
4. Issueを作成すると`Web Research`ワークフローが自動的に起動します
5. エージェントが内部で調査計画を作り、Actions内で一時起動したSearXNGでWebを検索します
6. `reports/`にMarkdownレポートを追加するDraft Pull Requestが作成されます
7. 内容と出典を確認してからPull Requestをマージします

Issueテンプレートやラベル操作は必要ありません。このリポジトリの新規Issueは、すべて調査依頼として扱われます。

## Issueの記載例

タイトル:

```text
日本国内で利用できるAI検索サービスを調べて
```

本文:

```text
企業利用を想定しています。
料金、セキュリティ、日本語対応、情報源の透明性を比較してください。
できるだけ最新の公式情報を優先してください。
```

依頼が曖昧でも合理的な前提を置ける場合、エージェントは前提をレポートに記載して調査を続行します。解釈によって結果が大きく変わる場合だけ、Issueに確認コメントを投稿します。

## 構成

```text
.github/
├─ aw/
│  └─ actions-lock.json
├─ copilot-instructions.md
└─ workflows/
   ├─ web-research.md
   └─ web-research.lock.yml
scripts/
└─ searxng_search.py
reports/
├─ README.md
└─ 2026-09-20-issue-1-screen.md
README.md
history.md
.gitattributes
.gitignore
```

- `.github/aw/actions-lock.json`: `gh-aw`が使用するActionのバージョンとSHA
- `.github/copilot-instructions.md`: リポジトリ共通の調査・執筆・セキュリティ方針
- `.github/workflows/web-research.md`: Agentic Workflowのソース
- `.github/workflows/web-research.lock.yml`: `gh aw compile`による生成ファイル
- `scripts/searxng_search.py`: SearXNG検索結果を解析する補助スクリプト。現在のワークフローはMCP Fetch経由で検索します
- `reports/`: 調査レポートの保存先
- `history.md`: 環境構築と操作の履歴
- `.gitattributes`: 生成されたlockファイルをGitHub上で生成物として扱う設定

## 初期設定

### Copilot認証

個人のGitHub Copilotサブスクリプションを使用する場合は、Copilot Requestsへのアクセスを持つfine-grained PATをRepository Secretとして登録します。

```powershell
gh secret set COPILOT_GITHUB_TOKEN
```

### Web検索

Web検索にはSearXNGを使用します。IssueごとのGitHub Actions実行中だけ公式SearXNGコンテナーを起動し、完了後に破棄します。

SearXNG用の外部アカウント、APIキー、Repository Secret、常設サーバーは必要ありません。検索結果は、ホストネットワークで起動する読み取り専用のMCP Fetchサーバーを通じて取得します。SearXNG標準のrobots.txtが検索クエリを拒否するため、このローカルSearXNGへの取得に限りMCP Fetchのrobots.txt確認を無効化します。

SearXNGは複数の外部検索サービスを集約します。GitHub Actionsの共有IPが検索サービスから制限される場合や、検索結果ページへの直接アクセスがファイアウォールで制限される場合があります。

### GitHub Actions

リポジトリの`Settings > Actions > General`でGitHub Actionsを有効にします。Draft Pull Requestを作成するため、次の設定も必要です。

```text
Workflow permissions
└─ Allow GitHub Actions to create and approve pull requests
```

## 開発・検証

frontmatter、ツール、権限、safe outputsを変更した場合は、検証してからlockファイルを再生成します。

```powershell
gh aw validate web-research
gh aw compile web-research --approve
gh aw validate web-research --strict
```

生成された`.lock.yml`は直接編集しません。ソースの`.md`と一緒にコミットします。

## セキュリティ

- Issue本文とWebページは信頼できない入力として扱います
- Webページ内の命令には従いません
- 認証情報をリポジトリへ保存しません
- Web検索はActions実行中だけ起動するSearXNGコンテナーを使用します
- SearXNGコンテナーは公式イメージをSHA-256ダイジェストで固定します
- レポートは`main`へ直接書き込まず、Draft Pull Requestでレビューします
- AI生成レポートは、重要な判断に使う前に人間が内容と出典を確認します
