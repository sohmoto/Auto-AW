# `network.allowed` の `local` 修正と再コンパイルによる問題解決可能性の調査

## 2. エグゼクティブサマリー

`network.allowed` の値を `localhost` から `local` に変更し、`gh aw compile` 相当の再コンパイルによって `.github/workflows/web-research.lock.yml` を更新した修正は、直前に発生していた **stale lock file（編集元Markdownとlockファイルの不一致）** の問題を解消する方向として妥当です。

確認できた範囲では、2026年9月20日 16:05:21 UTC のコミット `de857fdb` において、`web-research.md` は `network.allowed: [defaults, local]` となり、lockファイルも同時に更新されています。lockファイルのメタデータには新しいfrontmatter hashが記録され、生成元も `gh-aw v0.88.7` と示されています。

ただし、修正後の `main` ブランチで実際にIssueイベントを処理したGitHub Actions実行は、確認できた最新の実行一覧にはまだありません。そのため、結論は **「stale lock file問題は解消された可能性が高いが、ワークフロー全体が正常動作することまでは未検証」** です。

## 3. 結論

- **lock file不一致エラーについては、今回の修正で解決する見込みが高い**です。
- `localhost` ではなく `local` を指定したことは、確認済みの生成済みlockファイルにも反映されています。
- `.md` と `.lock.yml` を再コンパイル後に同一コミットで更新しているため、前回の `stale_lock_file_failed` の直接原因には対処できています。
- ただし、実行結果一覧では、修正コミット `de857fdb` 後のWeb Research実行の成功までは確認できませんでした。
- 次に、Issueを1件開いて、`Check workflow lock file` が成功するか、続いてSearXNG/MCP接続とレポート生成まで成功するかを確認する必要があります。

## 4. 詳細な調査結果

### 4.1 直前の失敗原因

Issue #11 は、Web Researchワークフローが「コンパイル済みlockファイルがソースMarkdownと一致しない」ため起動できなかったと報告しています。失敗分類は `stale_lock_file_failed` です。

前回の実行は、コミット `c1709a843f05e55c180c4481899bff41919b901e` に対して実行され、2026年9月20日 15:56:24 UTC に開始され、失敗しました。

### 4.2 修正内容

修正後の `.github/workflows/web-research.md` では、次の設定が確認できます。

```yaml
network:
  allowed:
    - defaults
    - local
```

同じファイルでは、SearXNGの接続先として `http://localhost:8081` を使用しています。これは、`local` がネットワーク許可エコシステムを表し、実際のHTTP接続先のホスト名・ポートとは別の概念であることを示します。

また、修正コミットのメッセージは `Compile corrected web research workflow` であり、「supported local network ecosystemを使用し、workflow lock fileを再生成した」と説明されています。

### 4.3 lockファイル更新の確認

修正後の `.github/workflows/web-research.lock.yml` には、以下が確認できます。

- 生成元: `gh-aw v0.88.7`
- `GH_AW_INFO_ALLOWED_DOMAINS: '["defaults","local"]'`
- `SEARXNG_URL: http://localhost:8081`
- SearXNGサービスのホストポート: `8081:8080`
- MCP fetchコンテナーのネットワーク: `--network host`
- lockファイル先頭のfrontmatter hashが更新済み

このため、少なくとも設定値を変更したのにlockファイルを再生成していない、という前回の状態からは進展しています。

### 4.4 修正後の実行状況

確認できたGitHub Actions実行では、修正前の実行は次のとおりです。

- 2026年9月20日 15:56:24 UTC開始: stale lock fileで失敗
- 2026年9月20日 14:50:28 UTC開始: 成功。ただし、これは別の修正コミットに対する実行
- 2026年9月20日 13:46:28 UTC開始: agent failureで失敗

修正コミット `de857fdb` の後に、Issueイベントを処理したWeb Research実行の成功記録は、今回取得した最新10件の実行一覧には含まれていません。したがって、再コンパイルが正しいことは確認できますが、GitHub Actions上の実動作は未確認です。

## 5. 比較表または構造化した分析

| 確認項目 | 修正前 | 修正後 | 判定 |
|---|---|---|---|
| `network.allowed` のローカル指定 | `localhost` | `local` | 修正済み |
| `.md` と`.lock.yml`の同期 | 不一致で起動阻止 | 同一修正コミットで再生成 | 解消見込みが高い |
| SearXNG URL | `http://localhost:8081` | `http://localhost:8081` | 維持されており妥当 |
| SearXNGポート | ホスト8081 → コンテナー8080 | ホスト8081 → コンテナー8080 | 維持されており妥当 |
| lockファイルの生成バージョン | 旧状態 | `gh-aw v0.88.7` | 更新済み |
| 修正後の実ワークフロー成功 | 未確認 | 未確認 | 追加検証が必要 |

## 6. 推奨される次のアクション

1. Issueを1件作成して、修正後の`main`ブランチでWeb Researchを起動する。
2. 実行ログの `Check workflow lock file` ステップが成功することを確認する。
3. 同じ実行で、SearXNGサービスのhealthcheck、MCP `searxng-fetch` の起動、Web Research agentの実行を確認する。
4. 成功した場合は、今回の問題は実質的に解決したと判断する。
5. lock checkが再度失敗した場合は、ログ中の`[hash-debug]`出力を確認し、Markdownのfrontmatter、import内容、改行・エンコーディング差分を比較する。

## 7. 情報源間の相違

今回確認した情報源の間で、`network.allowed` の修正内容に関する直接的な矛盾はありません。

一方、過去のIssue #11本文は「lock fileがソースMarkdownと一致しない」と報告しており、修正後のファイルは`local`への変更とlockファイル再生成を示しています。しかし、GitHub Actions実行履歴には修正後の成功実行がまだ確認できないため、**設定上の修正確認**と**実行結果による検証**の間に差があります。

## 8. 不確実な点、未解決事項、調査の限界

- 修正コミット後のWeb Research実行がまだ行われていない、または今回取得した実行一覧の範囲外である可能性があります。
- `network.allowed: local` が、利用中の`gh-aw`バージョンおよびGitHub Actions実行環境で期待どおりにSearXNGへの接続を許可するかは、実行ログでの確認が必要です。
- lockファイルのhash値が一致していることを、ローカルで`gh aw compile --validate`を実行した結果としては確認できていません。Git上の生成済みlockファイルとコミット履歴から判断しています。
- SearXNGの検索、MCP Gateway、外部Web取得、レポート作成までを一つの修正後実行で完了できるかは未確認です。

## 9. 出典一覧

1. GitHub Issue #11「[aw] Web Research has stale lock file」— GitHub Actions（発行主体: GitHub Actions）、2026年9月20日。  
   https://github.com/akkoike/Auto-AW/issues/11
2. GitHub Actions実行 `35521131543`「Web Research」— `akkoike/Auto-AW`、2026年9月20日 15:56:24 UTC開始。  
   https://github.com/akkoike/Auto-AW/actions/runs/35521131543
3. コミット `de857fdbf9d97325cea34be01aabfac951afd1d8`「Compile corrected web research workflow」— akkoike、2026年9月20日 16:05:21 UTC。  
   https://github.com/akkoike/Auto-AW/commit/de857fdbf9d97325cea34be01aabfac951afd1d8
4. `web-research.md` 修正後ファイル — `akkoike/Auto-AW` の`main`ブランチ。  
   https://github.com/akkoike/Auto-AW/blob/main/.github/workflows/web-research.md
5. `web-research.lock.yml` 修正後ファイル — `akkoike/Auto-AW` の`main`ブランチ。  
   https://github.com/akkoike/Auto-AW/blob/main/.github/workflows/web-research.lock.yml
6. GitHub Agentic Workflows Network Configuration — GitHub公式ドキュメント。  
   https://github.github.com/gh-aw/reference/network/

## 10. 調査概要

- 調査日: 2026年9月20日
- 対象リポジトリ: `akkoike/Auto-AW`
- 対象ブランチ: `main`
- 主な対象: `web-research.md`、`web-research.lock.yml`、Issue #11、GitHub Actions実行履歴
- 判定: stale lock file問題は解消見込みが高いが、修正後の実行成功は未確認

## 11. 依頼内容と採用した前提

### 依頼内容

「ローカルで`network: allowed:`の`localhost`指定を`local`に修正し、再度コンパイルした。これで先ほどの問題は解決するか」を確認すること。

### 採用した前提

- 「先ほどの問題」は、直近のIssue #11で報告されたstale lock fileエラーを指すものと解釈しました。
- 「再度コンパイル」は、2026年9月20日 16:05:21 UTCのコミット`de857fdb`で実施された再生成を指すものと解釈しました。
- GitHub上で取得できるファイル、コミット、Issue、Actions実行履歴を根拠とし、未取得のローカル実行結果は推測しませんでした。

## 12. 調査計画と調査方法

1. リポジトリの最新状態とdefault branchを確認。
2. 関連Issueの本文を確認し、直前の失敗原因を特定。
3. 修正後の`web-research.md`を取得し、`network.allowed`とSearXNG接続設定を確認。
4. 修正後の`web-research.lock.yml`を取得し、生成情報、許可ドメイン、サービス設定を確認。
5. 修正コミットの日時、メッセージ、親コミットを確認。
6. GitHub Actions実行履歴と修正後実行の有無を比較。
7. 設定修正による原因解消と、実行成功による動作確認を分離して結論化。

## 13. 調査情報

- 調査実施日時: 2026年9月20日
- 元Issue番号: #11を関連Issueとして採用
- 使用した主要検索・確認条件:
  - `repo:akkoike/Auto-AW` のIssue一覧
  - `.github/workflows/web-research.md`
  - `.github/workflows/web-research.lock.yml`
  - `web-research.md` のコミット履歴
  - GitHub Actionsの直近実行一覧
- 重要な確認点:
  - 修正後の設定値は`defaults`と`local`
  - SearXNG URLは`http://localhost:8081`
  - lockファイルは`gh-aw v0.88.7`で生成
  - 修正後の実行成功は未確認
