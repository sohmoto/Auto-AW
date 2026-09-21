# Auto-AW 変更履歴

## この文書について

Auto-AWのローカルリポジトリで実際に作成、設定、更新した内容を記録します。
検討だけで終わった内容、設定方法の確認、提案、未実施の作業は記録しません。

## 2026-09-19

### GitHubリポジトリとの同期

空のローカルフォルダーへ、GitHubのprivate repositoryをcloneしました。

```powershell
git clone https://github.com/akkoike/Auto-AW.git .
```

設定されたリモート:

```text
origin https://github.com/akkoike/Auto-AW.git
```

ローカルブランチ:

```text
main
```

clone時点では、ローカルとリモートの両方にコミットおよび管理対象ファイルはありませんでした。

### GitHub CLIの更新

wingetでインストールされていたGitHub CLIを更新しました。

```text
2.87.3 → 2.101.0
```

実行したコマンド:

```powershell
winget upgrade --id GitHub.cli --exact --silent --accept-package-agreements --accept-source-agreements
```

### GitHub Agentic Workflows CLIの更新

`github/gh-aw`拡張を更新しました。

```text
v0.86.2 → v0.88.7
```

拡張がpinされていたため、`--force`を付けて更新しました。

```powershell
gh extension upgrade github/gh-aw --force
```

更新後、Auto-AWリポジトリに対して次の診断を実行し、成功しました。

```powershell
gh aw doctor --repo akkoike/Auto-AW --dir .
```

## 2026-09-20

### リポジトリ構成の作成

次のファイルとディレクトリを作成しました。

```text
.github/
├─ aw/
│  └─ actions-lock.json
├─ copilot-instructions.md
└─ workflows/
   ├─ web-research.md
   └─ web-research.lock.yml
reports/
└─ README.md
README.md
history.md
.gitattributes
.gitignore
```

各ファイルの用途:

- `.github/aw/actions-lock.json`: `gh-aw`が利用するActionのバージョンとSHA
- `.github/copilot-instructions.md`: リポジトリ共通の調査、執筆、セキュリティ指示
- `.github/workflows/web-research.md`: Agentic Workflowの編集元
- `.github/workflows/web-research.lock.yml`: コンパイル済みGitHub Actionsワークフロー
- `reports/README.md`: レポートの命名規則、構成、出典基準
- `README.md`: リポジトリの利用方法と構成
- `history.md`: 実際に行った変更の履歴
- `.gitattributes`: `*.lock.yml`を生成物として扱うGitHub Linguist設定
- `.gitignore`: 秘密情報、一時ファイル、OS生成ファイルの除外設定

### Web Researchワークフローの作成

Copilotエンジン用のワークフローテンプレートを生成しました。

```powershell
gh aw new web-research --engine copilot
```

生成された`.github/workflows/web-research.md`を、次の動作になるよう更新しました。

- 新規Issueの`opened`イベントで起動
- GitHub Mobileを含む通常のIssueを調査依頼として処理
- Issueテンプレートおよびラベル操作を使用しない
- Copilotエンジンを使用
- Issueの内容から内部で調査計画を作成
- 合理的な前提を設定できる場合は確認待ちにせず調査を実行
- 解釈によって結果が大きく変わる場合だけIssueへ確認コメントを投稿
- Web検索とWebページ本文の抽出を実行
- 一次情報を優先し、重要な主張を複数の情報源で検証
- `reports/`へ新しいMarkdownレポートを1ファイルだけ作成
- レポートをDraft Pull Requestとして提出
- 元Issueへ結果をコメント
- レポート以外のファイル変更を禁止
- Issue本文とWebコンテンツを信頼できない入力として処理
- 外部コンテンツに含まれる命令を無視
- 秘密情報の出力を禁止
- 実行時間を30分に設定
- strict modeを有効化

### Issue本文の安全な取得方式への変更

Issue本文を`${{ github.event.issue.body }}`でプロンプトへ直接展開する構成は、未信頼入力に関する厳格検証で拒否されました。

Issue番号だけを許可された式で受け取り、GitHub MCPの読み取り専用`issue_read`ツールで本文を取得する方式へ変更しました。

### Copilot共通指示の作成

`.github/copilot-instructions.md`を作成し、次の内容を設定しました。

- リポジトリを調査専用として扱う
- 利用者向けレポートを日本語で作成
- 調査成果物を`reports/`だけに作成
- 1件の依頼につき新しいレポートを1つ作成
- 既存レポートを上書きしない
- `.github/`、`README.md`、`history.md`、`.gitignore`を変更しない
- 一次情報と公式情報を優先
- 重要な主張を複数情報源で相互検証
- 事実、推定、解釈、意見、推奨を区別
- 情報源間の矛盾、不確実性、調査の限界を記録
- 架空の出典を作成しない
- 外部コンテンツの命令に従わない
- 秘密情報をリポジトリへ書き込まない
- レポートの命名規則と必須構成

作成時は英語で記載していましたが、その後、技術的なファイル名と命名パターンを維持したまま全文を日本語へ更新しました。

### レポート基準の作成

`reports/README.md`を作成し、次の基準を設定しました。

- ファイル名を`YYYY-MM-DD-issue-<Issue番号>-<スラッグ>.md`形式に統一
- レポートの必須構成を定義
- 一次情報と公式資料を優先
- 資料名、発行主体または著者、日付、URLを記録
- 重要な主張を複数情報源で確認
- 確認できない情報や矛盾する情報を明記
- Draft Pull Requestを人間が確認してからマージ

### Web検索をTavily keyless接続へ変更

Web検索とWebページ本文の抽出には、TavilyのリモートMCPを使用する構成にしました。

最初は`TAVILY_API_KEY`をRepository SecretからAuthorizationヘッダーへ渡す構成を作成しましたが、その後、アカウントとAPIキーを必要としないTavily公式のkeyless接続へ変更しました。

現在の接続設定:

```yaml
mcp-servers:
  tavily:
    type: http
    url: "https://mcp.tavily.com/mcp/"
    headers:
      X-Tavily-Access-Mode: "keyless"
    allowed: ["tavily_search", "tavily_extract"]
```

この変更により、ワークフローとコンパイル済みファイルから`TAVILY_API_KEY`への参照を削除しました。

許可するTavily MCPツールを次の2つに限定しました。

- `tavily_search`
- `tavily_extract`

ネットワーク接続先を`*.tavily.com`へ制限しました。

### READMEの作成と更新

ルートの`README.md`を作成し、次の内容を記載しました。

- GitHub MobileまたはGitHub WebからIssueを作成する利用方法
- 自然言語IssueからDraft Pull Requestが作成されるまでの処理
- リポジトリのファイル構成
- Copilot認証に使用するRepository Secret名
- Web検索がTavily keyless接続であること
- ワークフローの検証とコンパイル方法
- Issue、Webコンテンツ、秘密情報に関するセキュリティ方針

Tavily keyless接続への変更に合わせ、Tavilyアカウント、APIキー、Repository Secretが不要である内容へ更新しました。

### Git属性と除外設定の作成

`.gitattributes`を作成し、コンパイル済みワークフローをGitHub上で生成物として扱うよう設定しました。

```gitattributes
.github/workflows/*.lock.yml linguist-generated=true
```

`.gitignore`を作成し、次を除外しました。

- `.env`
- `.env.*`
- `*.log`
- `*.tmp`
- `.DS_Store`
- `Thumbs.db`

`.env.example`は除外対象から外しました。

### ワークフローのコンパイル

次のコマンドでワークフローをコンパイルしました。

```powershell
gh aw compile web-research --approve
```

コンパイルにより次のファイルが生成または更新されました。

- `.github/workflows/web-research.lock.yml`
- `.github/aw/actions-lock.json`
- `.gitattributes`

コンパイル済みワークフローの情報:

```text
gh-aw compiler: v0.88.7
engine: copilot
strict: true
```

### 最終検証

Tavily keyless接続への変更後、次の厳格検証を実行しました。

```powershell
gh aw validate web-research --strict
```

結果:

```text
1 workflow succeeded
0 warnings
```

ワークフロー一覧でも、`web-research`がCopilotエンジンのコンパイル済みワークフローとして認識されました。

```text
web-research | copilot | compiled: Yes
```

`.github/`以下に`TAVILY_API_KEY`および`secrets.TAVILY_API_KEY`への参照が残っていないことを確認しました。

### Web検索をSearXNGへ変更

Tavily keyless接続を削除し、IssueごとのGitHub Actions実行中だけ公式SearXNGコンテナーを起動する構成へ変更しました。

変更内容:

- `mcp.tavily.com`への接続設定を削除
- Tavily MCPツールの設定を削除
- `services.searxng`を追加
- SearXNG公式コンテナーイメージをSHA-256ダイジェストで固定
- SearXNGのポート`8080`をActionsホストへ公開
- Agent Workflow Firewallの`docker-sudo-iptables`ランタイムを使用
- サンドボックスから`localhost:8080`経由でSearXNGへ接続
- Actions実行ごとにSearXNG用の一時的なsecret keyを生成
- SearXNGの公開インスタンス機能とリミッターを無効化
- エージェント開始前にSearXNGの起動完了を確認
- 検索ツールを`scripts/searxng_search.py`に限定
- SearXNGアカウント、APIキー、Repository Secret、常設サーバーを不要化

追加ファイル:

```text
scripts/searxng_search.py
```

このヘルパーは、ワークフロー内のSearXNGへ検索リクエストを送り、HTML結果を解析してタイトル、URL、概要をMarkdownまたはJSONで出力します。

### SearXNG接続先を修正

GitHub Actionsのサービスコンテナーへ接続できるよう、ワークフローと検索ヘルパーのSearXNG接続先を`http://localhost:8080`へ統一しました。

検索ヘルパーの許可URLにも`http://localhost:8080`を設定しました。

### レポート構成の表示順を変更

レポートの主要な結果を先に確認できるよう、ワークフロー、Copilot共通指示、レポート基準の構成順を統一して変更しました。

上位へ移動した項目:

- エグゼクティブサマリー
- 結論
- 詳細な調査結果
- 比較表または論点整理
- 推奨される次のアクション

後半へ移動した付帯情報:

- 調査概要
- 依頼内容と採用した前提
- 調査計画と調査方法
- 調査日時、元Issue番号、主要検索条件などの調査情報

### SearXNG用MCP Gateway設定を修正

MCP Gateway v0.4.18の設定スキーマに合わせて、SearXNG検索結果を取得する`searxng-fetch`サーバーの設定を修正しました。

変更内容:

- MCPサーバーの形式を`type: stdio`として明示
- Gatewayが受理しない`mcp/fetch@sha256:...`形式を`mcp/fetch:latest`へ変更
- 実行時に不要な旧MCP Registry URLを削除
- `--network host`をstdioコンテナーのDocker実行引数として維持
- Agentic Workflowを再コンパイル
- strict検証でエラーと警告がないことを確認

### ローカルSearXNG検索のrobots.txt制限に対応

SearXNG標準のrobots.txtが検索クエリを拒否するため、`searxng-fetch`のエントリーポイント引数に`--ignore-robots-txt`を追加しました。

この設定は、同じGitHub Actions実行内で一時起動するローカルSearXNGの検索結果取得に限定しています。Docker実行引数の`--network host`とは分離して設定しました。

### SearXNG対応後のワークフロー正常終了を確認

コミット`19dfd75bd68d10d36d96baf6928ee9e35fb8b503`を使用したGitHub Actions実行`35523728716`が正常終了したことを確認しました。

成功を確認した処理:

- Actionsジョブの起動
- SearXNGサービスコンテナーを含むコンテナー初期化
- MCP Gatewayと`searxng-fetch`の起動
- GitHub Copilot CLIによるエージェント処理
- Safe Outputsの処理
- コンテナーの停止
- `pre_activation`、`activation`、`agent`、`detection`、`safe_outputs`、`conclusion`の全ジョブ

## 2026-09-21

### 調査依頼を計画と承認の二段階へ変更

新しく作成されたIssueから直ちにWeb調査を始めず、Copilotが詳細な調査計画を作成し、人間が承認してから本調査を開始する構成へ変更しました。

追加したAgentic Workflow:

```text
.github/workflows/research-plan.md
.github/workflows/research-plan.lock.yml
```

`Research Planning`は新規Issueのタイトルと本文から、調査目的、想定読者、対象期間、地域、論点、比較軸、優先する情報源、最新情報の必要性、検索クエリ候補、対象外、未確定事項、完了条件を整理します。

作成した計画は、元のIssue本文を削除せず、`auto-aw-research-plan`マーカー内へ追記します。計画を作成できた場合は`research-plan-ready`ラベルを付けます。情報が不足して有効な計画を作成できない場合は`research-needs-info`ラベルを付けます。

計画作成段階では、Web検索、外部URLの取得、レポートファイルの作成、Pull Requestの作成を行わない構成にしました。

### Web Researchを人間の承認後だけ起動するよう変更

`Web Research`のトリガーを新規Issueの`opened`イベントから、`research-approved`ラベルの`labeled`イベントへ変更しました。

本調査を開始する条件:

- 人間が`research-approved`ラベルを付けている
- `research-plan-ready`ラベルが存在する
- Issue本文に`auto-aw-research-plan`マーカーで囲まれた計画が存在する

本調査中はIssueをロックし、承認済み計画が実行中に変更されないようにしました。本調査は承認済み計画を実行範囲として扱い、計画の目的、対象、期間、地域、比較軸、対象外を勝手に変更しません。

SearXNGサービス、MCP Fetch、ホストネットワーク、robots.txt対応は本調査側に維持しました。承認済み計画で最新情報、幅広いURL探索、比較対象の発見が必要な場合にSearXNGを使用し、指定URLだけを確認する計画では`web-fetch`による確認を優先します。

### 承認用ラベルを作成

GitHubリポジトリへ次のラベルを作成しました。

```text
research-plan-ready
research-approved
research-needs-info
```

`research-approved`は人間による本調査の実行承認を示すため、計画作成エージェントが付与できない構成にしました。

### 二段階ワークフローの文書と生成ファイルを更新

次の文書を二段階運用に合わせて更新しました。

```text
.github/copilot-instructions.md
README.md
reports/README.md
```

両Agentic Workflowをコンパイルして生成lockファイルを更新し、次の検証を実行しました。

```powershell
gh aw compile research-plan --approve --actionlint
gh aw compile web-research --approve --actionlint
gh aw validate research-plan --strict
gh aw validate web-research --strict
git diff --check
```

両ワークフローのコンパイル、Actionlint、strict検証は、エラーと警告なしで成功しました。

### Research Planningのタイムアウトを修正

最初の`Research Planning`実行では、MCP Gateway、GitHub MCP Server、Safe Outputs MCP Serverは正常に起動していましたが、Copilot AgentにMCP CLIラッパーを実行する権限がありませんでした。

AgentはIssue本文を取得できず、`gh`コマンドや利用可能なツールの探索を繰り返した結果、10分の実行上限に達してタイムアウトしました。MCPの`tools/call`は実行されておらず、認証、ネットワーク、MCP Gatewayの起動は原因ではありませんでした。

`.github/workflows/research-plan.md`を次の方針で修正しました。

- `cli-proxy`を有効化
- シェル経由で許可するMCP CLIを`github:*`と`safeoutputs:*`に限定
- `missing-tool` Safe Outputを追加
- Issue取得には`github issue_read`を使用するよう明示
- Issue取得ツールが利用できない場合は、`gh`コマンド、ネットワークコマンド、実行ファイル探索、別名ツールの試行を行わず、直ちに終了するよう明示

`timeout-minutes`は10分のまま維持しました。タイムアウト時間の延長ではなく、Issue取得経路の修正と探索ループの防止を根本対策としています。

`research-plan.lock.yml`を再生成し、Copilot CLIへ次の権限が生成されていることを確認しました。

```text
shell(github:*)
shell(safeoutputs:*)
```

次の検証はエラーと警告なしで成功しました。

```powershell
gh aw compile research-plan --approve --actionlint
gh aw validate research-plan --strict
```
