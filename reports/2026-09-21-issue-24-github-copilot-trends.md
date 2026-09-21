# GitHub Copilotの最新技術動向調査(2026年9月時点)

## エグゼクティブサマリー

GitHub Copilotは、2026年に入り単なる「コード補完・チャット支援ツール」から「エージェント型の開発プラットフォーム」へと性格を大きく変えている。特筆すべき動向は以下の3点である。

1. **課金体系の抜本的な転換**: 2026年6月1日付で、従来の「プレミアムリクエスト(Premium Request Unit, PRU)」方式から、トークン消費量に基づく「GitHub AI Credits(GitHub AIクレジット)」方式へ全面移行した。基本プラン料金(Pro $10/月、Pro+ $39/月、Business $19/ユーザー/月、Enterprise $39/ユーザー/月)自体は変更されていないが、モデル利用の従量制課金が強化された([GitHub Blog, 2026-04-27](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing))。
2. **対応モデルの急速な拡大と入れ替わり**: Anthropic Claude系(Sonnet/Opus/Haiku/Fable系列)、OpenAI GPT-5.x/GPT-6系列、Google Gemini 3.x Flash系列、xAI Grok、Microsoft MAI-Code、Moonshot Kimi系列など、複数ベンダーのモデルを横断的に提供している。一方でモデルのライフサイクルは速く、2026年10月19日に複数モデル(Gemini 3.7 Flash、GPT-5.5、GPT-5.4、GPT-5.4 mini、GPT-5 mini、Grok 4.5)の廃止が予告されている([GitHub Changelog, 2026-09-18](https://github.blog/changelog/2026-09-18-upcoming-deprecation-of-selected-github-copilot-models-in-mid-october))。
3. **Coding Agent(旧称: Copilot Workspace系機能を統合したクラウドエージェント)の高度化**: Issueの割り当てからリポジトリ調査・計画立案・コード変更・プルリクエスト作成までを自律的に行う「Copilot cloud agent」が中核機能として定着し、Dev Containerを用いたローカル環境相当でのエージェント実行や、サードパーティエージェント(Anthropic Claude、OpenAI Codex)への作業委任機能(Pro+/Max限定・プレビュー)なども追加されている([GitHub Docs, 取得日2026-09-21](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent); [GitHub Blog changelog, 2026-09-18](https://github.blog/changelog/2026-09-18-github-copilot-weekly-releases-september-14))。

競合ツール(Cursor、Amazon Q Developer、Codeiumほか)との比較では、GitHub Copilotは「マルチIDE対応・マルチモデル・GitHubエコシステムとの統合」を強みとする一方、Cursorは「マルチファイルリファクタリングの専用UI(Composer)」、Amazon Q DeveloperはAWS運用・移行支援に強みがあるとする複数の二次情報が一致していた。ただし、この比較は一次情報(公式ベンチマーク等)による裏付けが乏しく、技術メディアの評価記事に依存している点に留意が必要である。

## 結論

- GitHub Copilotは2026年、「補完ツール」から「マルチモデル・マルチエージェントの開発プラットフォーム」へと明確に軸足を移した。
- 料金体系は名目上安定(基本料金据え置き)だが、実質的には2026年6月の従量課金移行により、ヘビーユーザーのコスト構造が変化した。
- 対応モデルの数は増加傾向にあるが、同時に定期的なモデル廃止(デプリケーション)が行われており、利用側は継続的なモデル選定の見直しが必要。
- セキュリティ面では、MCP(Model Context Protocol)サーバー統合に伴う新たなガバナンス機能(MCPサーバーのアクセス制御、シークレットスキャン連携など)が2026年前半から強化されている。
- 競合との比較については、一次情報による厳密な機能・性能比較は確認できず、複数の技術メディアの評価(二次情報)に基づく傾向の整理にとどまる。

## 詳細な調査結果

### 1. 料金体系(プラン・エディション)の変化

GitHub公式プラン紹介ページおよびGitHub Docsの記載によると、2026年9月時点の個人向け・組織向けプランは以下の通り。

- **個人向け**: Free($0)、Pro($10/月)、Pro+($39/月)、Max($100/月)。学生向けにCopilot Student(無料)も提供。
- **組織・エンタープライズ向け**: Business($19/ユーザー/月)、Enterprise($39/ユーザー/月)。

2026年4月27日付のGitHub Blog公式発表によると、2026年6月1日付でプレミアムリクエスト単位(PRU)方式から「GitHub AI Credits」方式へ全面移行した。主なポイントは次の通り。

- 基本プラン料金は変更なし(Pro $10、Pro+ $39、Business $19/ユーザー、Enterprise $39/ユーザー)。
- クレジットは入力・出力・キャッシュ済みトークンの消費量に応じて消化され、各モデルの公表API料金に基づいて計算される。
- コード補完(インライン補完)とNext Edit Suggestionsは全プランでクレジット消費対象外として維持。
- 従来存在した「クレジット枯渇時の低コストモデルへのフォールバック」は廃止され、クレジット枯渇後は管理者設定の予算管理に委ねられる。
- Copilotコードレビューは、AIクレジットに加えてGitHub Actionsの実行時間(分)も消費するようになった。
- 移行に伴う救済措置として、Business/Enterpriseの既存顧客に対し、2026年6月〜8月の3か月間、通常より多いクレジット(Business: $30分、Enterprise: $70分相当)を促進策として付与。

GitHub Docs(取得日2026-09-21)によるAIクレジット割当ての詳細は以下の通り(基本クレジット + Flex割当ての合計)。

| プラン | 月額 | 基本クレジット | Flex割当 | 月間合計クレジット目安 |
|---|---|---|---|---|
| Copilot Pro | $10 | 1,000 | 500 | 1,500 |
| Copilot Pro+ | $39 | 3,900 | 3,100 | 7,000 |
| Copilot Max | $100 | 10,000 | 10,000 | 20,000 |
| Copilot Business | $19/ユーザー | ユーザーあたり1,900(総量) | - | 1,900 |
| Copilot Enterprise | $39/ユーザー | ユーザーあたり3,900(総量) | - | 3,900 |

Business/Enterpriseでは、組織内でクレジットをプール(共有)できる仕組みが導入されており、個々のユーザーの未消化分が無駄にならない設計となっている(2026-04-27付GitHub Blog記事)。

### 2. 対応LLMモデルの変遷

GitHub公式プランページ(取得日2026-09-21)に掲載されているモデル一覧(Free/Pro/Pro+/Max全プランで共通に利用可能、ただしプランにより優先度・レート制限は異なる)は以下の通り。

- Anthropic: Claude Fable 5 / Fable 5.1、Claude Haiku 4.5、Claude Sonnet 4 / 4.6 / 5、Claude Opus 4.7 / 4.8(高速モード含む、プレビュー) / 5
- OpenAI: GPT-5 mini、GPT-5.2、GPT-5.2-Codex、GPT-5.3-Codex、GPT-5.4、GPT-5.4 mini、GPT-5.5、GPT-5.6 Sol / Terra / Luna、GPT-6 Astra
- Microsoft: MAI-Code-1.1-Flash
- Google: Gemini 3.5 / 3.6 / 3.7 / 3.8 Flash
- xAI: Grok 4.5、Grok 4.6
- Moonshot AI: Kimi K2.7 Code、Kimi K3

一方、2026年9月18日付GitHub Changelogでは、2026年10月19日付で以下のモデルが廃止される予定であることが公式に告知されている。

| 廃止対象モデル | 廃止日 | 推奨代替モデル |
|---|---|---|
| Gemini 3.7 Flash | 2026-10-19 | Gemini 3.8 Flash |
| GPT-5.5 | 2026-10-19 | GPT-5.6 Sol |
| GPT-5.4 | 2026-10-19 | GPT-5.6 Sol |
| GPT-5.4 mini | 2026-10-19 | GPT-5.6 Luna |
| GPT-5 mini | 2026-10-19 | GPT-5.6 Luna |
| Grok 4.5 | 2026-10-19 | Grok 4.6 |

この廃止は、Copilot Chat、インライン編集、Ask/Agentモード、コード補完を含む全Copilot体験に適用される。Business/Enterpriseでは、デフォルトのモデル有効化設定に従い、代替モデルは管理者が明示的に無効化していない限り自動的に有効化される。

また、2026年9月14日付のリリースノート(2026-09-18公開の週次changelog)では、「auto model selection(自動モデル選択)」機能に、コスト・品質・応答速度のバランスを調整できる「efficiency(効率)」「balance(バランス)」「intelligence(高度)」の3段階の選択肢が追加されたことが確認できた。

### 3. Coding Agent・機能アップデートの動向

GitHub公式ドキュメント「About GitHub Copilot cloud agent」(取得日2026-09-21)によれば、Copilot cloud agent(旧Copilot Workspaceを統合した非同期エージェント)は、リポジトリを調査し、計画を立案し、ブランチ上でコード変更を行い、任意でプルリクエストを作成できる機能として位置づけられている。GitHub Issue、Visual Studio Code(GitHub Pull Requests拡張機能経由)など複数の経路からタスクを割り当て可能。

2026年9月14日〜18日の週次リリースノート(GitHub Changelog)からは、以下の具体的なアップデートが確認された。

- **コードレビュー機能の強化**: 指摘済みコメントの自動解決、コミットメッセージの提案、シェルツールを用いた変更検証、複数エージェントの所見を統合する「Lite reviews」。
- **VS Code 1.138のエージェント機能拡張**: Dockerと対応するDev Container構成がある場合、プロジェクト固有のツール・依存関係を使ってローカルのDev Container上でエージェントを実行できる機能(段階的ロールアウト)。非アクティブなエージェントセッションの自動クローズ(プレビュー)。Agents ウィンドウから直接プルリクエストを作成する機能。
- **管理者向け機能**: VS Code Agentsウィンドウの利用状況を可視化する利用メトリクスの一般提供開始(アクティブユーザー数、セッション数、メッセージ数など)。リポジトリのカスタムプロパティ値をCopilotが提案する機能(パブリックプレビュー)。AIクレジット上限到達時に組織へ予算増額をリクエストできる機能の一般提供開始(Business/Enterprise、マネージドユーザー企業を除く)。
- **Copilotアプリ**: Sentryのクラッシュレポートと連携し、エラー調査からコード修正・プルリクエスト作成までを支援する「Sentryキャンバス」機能。

また、Copilot Pro+/Max限定のプレビュー機能として、Anthropic Claude(Claude Code)やOpenAI Codexなどサードパーティのコーディングエージェントへタスクを委任できる機能が公式プランページに記載されている(取得日2026-09-21時点、プレビュー表記)。

### 4. セキュリティ・プライバシー関連の機能強化

検索結果からは、Model Context Protocol(MCP)サーバー統合に伴うセキュリティ・ガバナンス機能の強化が2026年の主要トピックの一つであることが確認できた。

- GitHub公式製品ページ(github.com/features/copilot)には、「MCP統合の保護」「開発者がアクセスできるMCPサーバーの制御」といった機能訴求が掲載されている(一次情報、取得日2026-09-21)。
- 2026年5月5日付のGitHub Changelogでは、「GitHub MCP Serverでのシークレットスキャン連携」が一般提供(GA)されたことが確認された(GitHub Secret Protection有効化済みリポジトリ対象、2026年3月からパブリックプレビュー)。
- Visual Studio 2026のリリースノート(Microsoft Learn、取得日2026-09-21)には、MCPサーバーの構成・アセットが承認後に変更された場合に検知し再承認を求める「トラスト検証」機能が追加されたと記載されている。
- 米国NSA関連のMedia Defense掲載資料(2026年6月2日付)や複数の技術メディア記事(Checkmarx、Scalekitなど)は、MCP自体のセキュリティリスク(サーバーのなりすまし、データ漏えいリスクなど)を業界全体の課題として指摘しており、GitHub Copilotに限らずMCPエコシステム全体への懸念として言及されている。これらは二次情報であり、GitHub Copilot固有のインシデントを示すものではない点に留意する。

これらの情報から、GitHub Copilotは2026年、MCPサーバーとの連携拡大に伴い、企業のセキュリティ・ガバナンス担当者からの要求に応える形でアクセス制御・監査・シークレット検出などの機能強化を進めていると整理できる。ただし、企業のセキュリティ運用担当者向けの詳細な設定手順やポリシーの網羅的な確認までは、本調査の範囲内では実施していない。

### 5. 開発者コミュニティでの評価・利用状況

一次情報(GitHub公式)では利用状況の定量データ(アクティブユーザー数の推移等)は本調査で確認できなかった。技術メディア(二次情報)からは、以下のような評価傾向が読み取れた。

- 「マルチIDE対応・GitHubワークフローとの統合」が評価される一方、「Cursorの方が複雑なマルチファイルリファクタリングに強い」という評価がvibecodingacademy.aiやakshayghalme.comなど複数の技術ブログで共通して見られた。
- 「AWS運用・移行に強いAmazon Q Developer」「AWS非依存でIDEを問わず使いたい場合はGitHub Copilot」という棲み分けの評価も複数サイトで一致していた。
- これらはいずれも技術メディアの評価記事(二次情報)であり、独立した定量的なベンチマークやユーザーサーベイの一次データは本調査では確認できていない。

## 比較表:主要プラン・機能の整理

| 項目 | Copilot Free | Copilot Pro | Copilot Pro+ | Copilot Max | Copilot Business | Copilot Enterprise |
|---|---|---|---|---|---|---|
| 月額(2026-09時点) | $0 | $10/ユーザー | $39/ユーザー | $100/ユーザー | $19/ユーザー | $39/ユーザー |
| 月間AIクレジット目安 | 限定的な割当 | 1,500(基本1,000+Flex 500) | 7,000(基本3,900+Flex 3,100) | 20,000(基本10,000+Flex 10,000) | 1,900/ユーザー(総量) | 3,900/ユーザー(総量) |
| モデル選択 | 自動選択のみ | 対応モデル一覧から選択可 | 対応モデル一覧+プレミアムモデル優先 | 同左+優先アクセス | 対応モデル一覧から選択可 | 同左+優先アクセス |
| Coding Agent(クラウドエージェント) | 制限あり(サードパーティ不可) | 利用可 | 利用可+サードパーティエージェント委任(プレビュー) | 同左 | 利用可 | 利用可+高度なガバナンス |
| コードレビュー(PR) | 不可 | 可 | 可 | 可 | 可 | 可 |
| 組織管理・ポリシー管理 | 不可 | 不可 | 不可 | 不可 | 可 | 可(拡張) |
| IP補償(IP Indemnity) | 不可 | 不可 | 不可 | 不可 | 可 | 可 |
| SAML SSO | 不可 | 不可 | 不可 | 不可 | 不可(要確認) | 可 |

出典: GitHub公式プランページ([github.com/features/copilot/plans](https://github.com/features/copilot/plans))およびGitHub Docs([docs.github.com/en/copilot/get-started/plans](https://docs.github.com/en/copilot/get-started/plans))、いずれも取得日2026-09-21。表中の数値・機能有無は取得時点のスナップショットであり、今後変更される可能性がある。

## 推奨される次のアクション

1. **利用中/検討中のプランで、2026年10月19日に廃止予定のモデル(Gemini 3.7 Flash、GPT-5.5、GPT-5.4、GPT-5.4 mini、GPT-5 mini、Grok 4.5)を使用しているワークフローがないか確認し、必要に応じて代替モデルへの切り替えを検討する。**
2. **2026年6月の従量課金移行に伴い、実際のAIクレジット消費実績(特にCoding Agentやコードレビューなどエージェント系機能の利用が多い場合)を確認し、想定コストとのギャップがないか点検する。**
3. **MCPサーバーを利用する場合は、GitHub/Microsoft双方が提供するMCPトラスト機能(アクセス制御、シークレットスキャン連携、変更検知による再承認)の設定状況を確認する。**
4. **競合ツール(Cursor、Amazon Q Developer等)との比較が必要な場合は、二次情報の評価記事だけでなく、各ベンダーの公式ベンチマークやPoC(概念実証)による定量評価を追加で実施することを検討する。**
5. **想定読者(経営層向け/エンジニア向け)、比較対象製品の要否、対象地域(グローバル/日本市場限定)について、次回調査依頼時に明確化してもらうことで、より的を絞った追加調査が可能になる。**

## 情報源間の相違

- 料金体系については、GitHub公式の一次情報(プランページ、Docs、Blog発表)相互で金額の食い違いは確認されなかった。
- 技術メディアの一部記事(techjacksolutions.com、cloudzero.com等)では、Enterprise料金を「$39/seat」、Business料金を「$19/seat」と記載しており、GitHub公式情報と整合していた。ただし一部サイト(automationatlas.io等)は情報の更新時期が古い可能性があり、2026年6月の従量課金移行前の情報(プレミアムリクエスト方式)を引きずっている記述も見られたため、料金・クレジット制度の詳細については必ずGitHub公式ページを優先して確認すべきである。
- 競合比較記事間では、「Cursorが機能面で優れる」とする記事と「GitHub Copilotがエコシステム統合で優れる」とする記事が併存しており、評価軸(コスト、機能の網羅性、統合のしやすさ等)によって結論が分かれていた。これは記事執筆者の立場・想定読者の違いによるものと考えられ、優劣の断定は避けた。

## 不確実な点・未確認事項・調査の限界

- Copilot Businessプランのプラン比較表における「SAML SSO」の有無について、GitHub公式プランページの一部表示が省略されていたため、正確な仕様はGitHub Docsの詳細ページで別途確認することを推奨する(本調査では「不可(要確認)」として保留した)。
- 開発者コミュニティでの定量的な評価(利用者数、満足度調査等)について、GitHub公式の一次データは本調査の範囲内では確認できなかった。
- 競合ツール(Cursor、Amazon Q Developer、Codeium等)の比較は、いずれも技術メディアによる二次情報に基づくものであり、独立した定量ベンチマークによる裏付けは行っていない。
- 承認済み計画に記載の「想定読者(経営層向け/エンジニア向け)」「具体的な対象期間」「対象地域」「比較対象製品の指定」は未確定事項として計画に明記されていたため、計画の「前提」欄に示された提案(直近6か月〜1年、グローバル中心、比較は補足的に実施)を採用した。この前提により、結果の重み付け(特に比較表の詳細度)が変わる可能性がある。
- MCPセキュリティに関する記述は、GitHub固有の機能(シークレットスキャン連携等)と、MCPエコシステム全体に対する業界的な懸念(NSA関連資料や複数ベンダーの一般論)が混在しているため、GitHub Copilot固有の対策と業界一般の課題を区別して読む必要がある。
- 本調査はSearXNG経由の検索結果と、そこから辿った一次情報ページの取得によるものであり、GitHub公式ドキュメントサイトの全ページを網羅的に確認したものではない。特にEnterprise向けの詳細なポリシー管理・監査ログ機能などは深掘りできていない。

## 出典一覧

1. GitHub, "GitHub Copilot · Plans & pricing", https://github.com/features/copilot/plans, 取得日2026-09-21(一次情報)
2. GitHub Docs, "Plans for GitHub Copilot", https://docs.github.com/en/copilot/get-started/plans, 取得日2026-09-21(一次情報)
3. GitHub Blog(Changelog), "GitHub Copilot is moving to usage-based billing", 2026-04-27, https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing(一次情報)
4. GitHub Changelog, "Upcoming deprecation of selected GitHub Copilot models in mid-October", 2026-09-18, https://github.blog/changelog/2026-09-18-upcoming-deprecation-of-selected-github-copilot-models-in-mid-october(一次情報)
5. GitHub Changelog, "GitHub Copilot weekly releases — September 14", 2026-09-18, https://github.blog/changelog/2026-09-18-github-copilot-weekly-releases-september-14(一次情報)
6. GitHub Docs, "About GitHub Copilot cloud agent", https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent, 取得日2026-09-21(一次情報)
7. GitHub Changelog, "Secret scanning with GitHub MCP Server is now generally available", 2026-05-05, https://github.blog/changelog/2026-05-05-secret-scanning-with-github-mcp-server-is-now-generally-available(一次情報、タイトル・概要はSearXNG検索結果スニペットで確認、本文の直接取得は未実施)
8. Microsoft Learn, "Visual Studio 2026 release notes", https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes, 取得日2026-09-21(一次情報寄り、MCPトラスト検証機能への言及)
9. 技術メディア記事(二次情報、料金傾向のクロスチェック用): CloudZero「GitHub Copilot cost: what teams actually pay in 2026」、Opslyft「GitHub Copilot Pricing 2026」、Layer3Labs「GitHub Copilot Pricing (2026)」など、SearXNG検索結果より
10. 技術メディア記事(二次情報、競合比較): vibecodingacademy.ai「Best AI Coding Assistants 2026」、akshayghalme.com「Cursor vs Claude Code vs Copilot vs Codex vs AWS Q Developer」、techbuzz.ai「Amazon Q Developer vs GitHub Copilot」など、SearXNG検索結果より
11. Scalekit, "GitHub Copilot Added MCP. Now Your Security Team Has Questions", 2026-02-24(二次情報、MCPガバナンスの論点整理として参照)

## 調査概要

- **調査日時**: 2026年9月21日(UTC)
- **元Issue番号**: #24(「GitHub Copilot調査」)
- **使用した主要検索条件**: "GitHub Copilot changelog 2026"、"GitHub Copilot pricing plans Individual Business Enterprise 2026"、"GitHub Copilot MCP trust layer security 2026"、"GitHub Copilot vs Cursor vs Amazon Q Developer comparison 2026"、"GitHub Copilot coding agent official documentation" ほか(ワークフロー内SearXNG、検索言語:all、safesearch=1)

## 依頼内容と採用した前提

- **元の簡易依頼**: 「GitHub Copilotの最新技術動向を教えてください。」
- **承認操作を行ったユーザー**: akkoike(`research-approved`ラベル付与によりIssue #24の計画を承認)
- **承認済み計画の要旨**: GitHub Copilot本体(Chat、Coding Agent等)の新機能・対応モデル・料金体系・セキュリティ強化・コミュニティ評価を中心に、直近6か月〜1年程度、グローバル(必要に応じ日本語情報も参照)を対象に調査。比較対象製品は明示されていないため、Copilot単独の動向整理を主軸とし、代表的な競合(Cursor、Amazon Q Developer、Codeium等)との簡易比較を補足的に実施。GitHub公式情報源を優先し、一次情報が確認できない場合に限り技術メディアを補助的に参照。
- **計画からの変更点**: 計画で「未確定」とされていた具体的な対象期間・対象地域・想定読者・比較対象の要否については、計画の「前提」欄に記載された提案(直近6か月〜1年、グローバル中心、簡易比較を補足的に実施)をそのまま採用し、本調査の範囲を独自に拡大・縮小することはしなかった。

## 調査計画と調査方法

1. Issue #24本文中の`auto-aw-research-plan`(該当マーカー内の承認済み計画)を確認し、調査目的・対象・論点・情報源優先順位・完了条件を整理した。
2. ワークフロー内のSearXNG(`http://localhost:8081/search`)を用いて、料金、モデル、Coding Agent、セキュリティ、競合比較の5つの論点それぞれについて検索クエリを実行した。
3. 検索結果から一次情報(GitHub公式ブログ・Changelog・Docs)を優先的に選定し、`web-fetch`相当のツール(`searxng-fetch`のfetch機能によるHTTP取得)で本文を確認した。
4. 一次情報が確認できない、または詳細が不足する論点(セキュリティの一部、競合比較)については、複数の技術メディア記事を横断的に確認し、二次情報である旨を明記した上で参考情報として整理した。
5. 各情報の公開日・取得日を可能な限り記録し、矛盾や不確実性、調査で確認できなかった点を「情報源間の相違」「不確実な点・未確認事項・調査の限界」の章にまとめた。

## 調査情報

- 対象Issue: akkoike/Auto-AW#24
- 調査実施者: Auto-AW Web Research Agent(GitHub Copilot上で動作)
- 主要利用ツール: GitHub MCP(issue_read)、searxng-fetch(SearXNG検索・Web取得)
- 調査範囲: GitHub Copilot本体(Copilot Chat、Coding Agent、Copilot CLI、Copilotアプリ等)の技術動向、料金体系、対応モデル、セキュリティ機能、競合比較(補足)
