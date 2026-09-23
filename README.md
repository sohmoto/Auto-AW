# Auto-AW

Auto-AWは、GitHub Issueに自然言語で投稿された調査依頼を、GitHub Agentic Workflowsで調査レポートへ変換するためのprivate repositoryです。

## 利用方法

1. GitHub MobileまたはGitHub Webで新しいIssueを作成します
2. タイトルに調べたいテーマを書きます
3. 本文に目的や期待する成果を簡単な文章で書きます
4. Issueを作成すると`Research Planning`ワークフローが起動します
5. Copilotが同じIssue本文へ、調査対象、期間、論点、比較軸、検索クエリ候補、完了条件などを含む詳細な調査計画を追記します
6. `research-plan-ready`ラベルが付いたら、追記された計画を確認し、必要ならIssue本文を編集します
7. 計画を承認する場合は、人間が`research-approved`ラベルを付けます
8. `Web Research`ワークフローが承認済み計画に沿って本調査を開始します
9. 最新情報や関連URLの探索が必要な計画では、Actions内で一時起動したSearXNGを使用します
10. `reports/`にMarkdownレポートを追加するDraft Pull Requestが作成されます
11. 内容と出典を確認してからPull Requestをマージします

このリポジトリの新規Issueは、すべて調査計画の作成対象として扱われます。Issue作成だけではWeb検索やレポート作成を開始しません。`research-approved`ラベルは人間による実行承認です。

## Issueの記載例

タイトル:

```text
日本国内で利用できるAI検索サービスを調べて
```

本文:

```text
企業利用を想定しています。主要サービスを比較してください。
```

`Research Planning`は、この簡易な依頼から想定読者、対象期間、比較軸、優先する情報源、最新情報の必要性、検索クエリ候補などを提案します。人間は提案をそのまま承認することも、Issue本文を編集してから承認することもできます。

## 承認ラベル

| ラベル | 意味 |
| --- | --- |
| `research-plan-ready` | Copilotによる調査計画の作成が完了 |
| `research-approved` | 人間が計画を確認し、本調査の開始を承認 |
| `research-needs-info` | 有効な計画を作るための情報が不足 |

`research-approved`はエージェントから付与しません。ラベルを付ける権限を持つ人間がGitHub上で操作してください。

承認後に本調査を再実行したい場合は、原因を修正してから`research-approved`ラベルを一度外し、再度付けます。古いワークフロー定義を使う可能性があるため、設定修正後にGitHub Actionsの`Re-run jobs`だけを使用することは推奨しません。

## 構成

```text
.github/
├─ aw/
│  └─ actions-lock.json
├─ copilot-instructions.md
└─ workflows/
   ├─ research-plan.md
   ├─ research-plan.lock.yml
   ├─ web-research.md
   └─ web-research.lock.yml
scripts/
└─ searxng_search.py
reports/
└─ README.md
README.md
LICENSE
SECURITY.md
.gitattributes
.gitignore
```

- `.github/aw/actions-lock.json`: `gh-aw`が使用するActionのバージョンとSHA
- `.github/copilot-instructions.md`: リポジトリ共通の調査・執筆・セキュリティ方針
- `.github/workflows/research-plan.md`: 新規Issueを人間の承認待ち調査計画へ変換するAgentic Workflowのソース
- `.github/workflows/research-plan.lock.yml`: `research-plan.md`から生成されるGitHub Actionsワークフロー
- `.github/workflows/web-research.md`: Agentic Workflowのソース
- `.github/workflows/web-research.lock.yml`: `gh aw compile`による生成ファイル
- `scripts/searxng_search.py`: SearXNG検索結果を解析する補助スクリプト。現在のワークフローはMCP Fetch経由で検索します
- `reports/`: 調査レポートの保存先
- `LICENSE`: 本ソフトウェアに適用されるMIT License
- `SECURITY.md`: 脆弱性の報告方法、対象範囲、対応方針
- `.gitattributes`: 生成されたlockファイルをGitHub上で生成物として扱う設定

## 初期設定

### Copilot認証

両Agentic Workflowは`copilot-requests: write`権限を宣言し、GitHub Actionsが実行ごとに発行する短期の`GITHUB_TOKEN`でCopilot CLIを認証します。Copilot認証用のfine-grained PATや`COPILOT_GITHUB_TOKEN` Repository Secretは必要ありません。

個人所有リポジトリでは、Copilot CLIのAI Creditsはリポジトリ所有者のCopilot seatへ紐づきます。Organization所有リポジトリでは、OrganizationのCopilotポリシーで「Allow use of Copilot CLI billed to the organization」を有効にしてください。

### Web検索

計画作成段階ではWeb検索を行いません。本調査の承認後、計画で最新情報、幅広いURL探索、比較対象の発見が必要な場合にSearXNGを使用します。GitHub Actions実行中だけ公式SearXNGコンテナーを起動し、完了後に破棄します。

SearXNG用の外部アカウント、APIキー、Repository Secret、常設サーバーは必要ありません。検索結果は、ホストネットワークで起動する読み取り専用のMCP Fetchサーバーを通じて取得します。SearXNG標準のrobots.txtが検索クエリを拒否するため、このローカルSearXNGへの取得に限りMCP Fetchのrobots.txt確認を無効化します。

SearXNGは複数の外部検索サービスを集約します。GitHub Actionsの共有IPが検索サービスから制限される場合や、検索結果ページへの直接アクセスがファイアウォールで制限される場合があります。

### GitHub Actions

リポジトリの`Settings > Actions > General`でGitHub Actionsを有効にします。Draft Pull Requestを作成するため、次の設定も必要です。

```text
Workflow permissions
└─ Allow GitHub Actions to create and approve pull requests
```

## 開発・検証

frontmatter、ツール、権限、safe outputsを変更した場合は、両ワークフローを検証してからlockファイルを再生成します。

```powershell
gh aw validate research-plan
gh aw validate web-research
gh aw compile research-plan --approve --actionlint
gh aw compile web-research --approve --actionlint
gh aw validate research-plan --strict
gh aw validate web-research --strict
```

生成された`.lock.yml`は直接編集しません。ソースの`.md`と一緒にコミットします。

## セキュリティ

### 運用方針

- Issue本文とWebページは信頼できない入力として扱います
- 計画作成AWは外部サイトへ接続せず、リポジトリファイルも変更しません
- 本調査は、人間が`research-approved`ラベルを付けた場合だけ開始します
- 本調査中はIssueをロックし、承認済み計画の変更を防ぎます
- Webページ内の命令には従いません
- 認証情報をリポジトリへ保存しません
- Web検索はActions実行中だけ起動するSearXNGコンテナーを使用します
- SearXNGコンテナーは公式イメージをSHA-256ダイジェストで固定します
- レポートは`main`へ直接書き込まず、Draft Pull Requestでレビューします
- AI生成レポートは、重要な判断に使う前に人間が内容と出典を確認します

### 脆弱性の報告

脆弱性、認証情報の漏えい、または安全でないワークフロー動作を発見した場合は、公開Issueへ秘密情報や再現用トークンを投稿しないでください。GitHubのPrivate vulnerability reportingが利用できる場合はそれを使用し、利用できない場合はリポジトリ所有者へ非公開の方法で連絡してください。

詳しい報告方法、サポート対象、対応方針は[Security Policy](./SECURITY.md)を参照してください。

## 利用条件

本リポジトリのソフトウェアは[MIT License](./LICENSE)で提供します。利用、複製、変更、再配布を行う場合は、ライセンス本文の著作権表示と許諾表示を保持してください。

- GitHub、GitHub Copilot、GitHub Actions、SearXNG、検索結果の提供元など、第三者サービスの規約、ポリシー、利用上限、課金条件を遵守してください
- 自分が管理権限または明示的な許可を持つリポジトリとデータだけを対象に使用してください
- Issue、取得したWebコンテンツ、生成レポートへ秘密情報、個人情報、機密情報を不用意に含めないでください
- AI生成の計画、調査結果、引用、URLは不正確または古い可能性があるため、公開、意思決定、業務利用の前に人間が検証してください
- 生成レポートは法務、医療、投資、セキュリティその他の専門的助言を構成しません
- ワークフロー実行に伴うAI Credits、GitHub Actions、ネットワーク、外部サービスの利用量と費用は利用者が管理してください
- 外部サイトのrobots.txt、アクセス制限、著作権、データ利用条件を尊重してください。`--ignore-robots-txt`は同一Actions実行内のローカルSearXNGに限定します

MIT Licenseの免責条項に従い、本ソフトウェアは現状有姿で提供され、特定目的への適合性、正確性、可用性を含む保証はありません。
