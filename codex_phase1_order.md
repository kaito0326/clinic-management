# Codex実装依頼文（Phase 1: 基盤構築）

## 目的
クリニック経営モニタリングアプリのMVP基盤を構築してください。  
このフェーズでは、以下を実装対象とします。

- DBスキーマ
- ファイルアップロード基盤
- 月報PDFドラフト保存〜確定の基盤
- 月次推移CSV取込基盤
- 将来キャッシュイベントCRUD
- 月次詳細APIの骨格
- ダッシュボードAPIの骨格

このフェーズでは、AIコメント生成や対話機能は実装しません。  
ただし、後から追加しやすい構造にしてください。

---

## 技術前提
以下を前提にしてください。

- フロントエンド: Next.js
- バックエンド: Next.js API Routes または Route Handlers
- DB: PostgreSQL
- ORM: Prisma 想定
- ストレージ: ローカルまたはクラウドストレージ抽象化可能な構造
- PDF解析・CSV解析はサービス層に分離
- TypeScript 前提

---

## 設計原則
以下を厳守してください。

### 1. rawデータを壊さない
- アップロードされた元ファイルは必ず保存する
- raw_files テーブルを使う

### 2. 会計科目を再分類しない
- PL/BS CSVの勘定科目、補助科目はそのまま保持する
- 原価/販管費などの独自再分類はしない

### 3. PDF由来データは下書き→確定を分ける
- 月報PDFは monthly_report_drafts に保存
- 確定後に monthly_reports へ保存
- 返済予定表PDFも将来的に同じ思想で扱う前提にする

### 4. 分析対象は正式データのみ
- 月報は monthly_reports の is_latest=true のみ
- 月次推移は monthly_financial_lines の is_latest=true のみ
- 将来イベントは cash_events の status=active のみ

### 5. 同月再登録は最新版切替
- 旧版を削除せず is_latest=false にする

---

## 今回実装するDBテーブル
以下をPrisma schemaで実装してください。

### clinics
- clinic_id
- clinic_name
- is_active
- created_at
- updated_at

### raw_files
- file_id
- clinic_id
- file_type
- source_file_name
- storage_path
- uploaded_at
- uploaded_by
- parse_status
- parse_error_message
- related_year_month
- is_latest

### monthly_report_drafts
- report_draft_id
- clinic_id
- source_file_id
- year_month
- data_status
- as_of_date
- elapsed_working_days
- planned_working_days
- patient_count
- new_patient_count_insurance
- insurance_points
- private_revenue
- medical_revenue
- patient_count_insurance
- patient_count_private
- avg_daily_patient_count
- avg_daily_patient_count_insurance
- avg_daily_patient_count_private
- avg_daily_points_insurance
- avg_daily_new_patient_count_insurance
- unit_price_insurance
- new_patient_count_private
- avg_daily_new_patient_count_private
- monthly_comment
- draft_status
- created_at
- updated_at

### monthly_reports
- monthly_report_id
- clinic_id
- source_file_id
- source_draft_id
- year_month
- data_status
- as_of_date
- elapsed_working_days
- planned_working_days
- patient_count
- new_patient_count_insurance
- insurance_points
- private_revenue
- medical_revenue
- patient_count_insurance
- patient_count_private
- avg_daily_patient_count
- avg_daily_patient_count_insurance
- avg_daily_patient_count_private
- avg_daily_points_insurance
- avg_daily_new_patient_count_insurance
- unit_price_insurance
- new_patient_count_private
- avg_daily_new_patient_count_private
- monthly_comment
- confirmed_at
- confirmed_by
- is_latest
- created_at
- updated_at

### monthly_financial_lines
- financial_line_id
- clinic_id
- source_file_id
- statement_type
- fiscal_year
- year_month
- account_name
- sub_account_name
- amount
- row_order
- is_total_row
- is_latest
- created_at
- updated_at

### cash_events
- cash_event_id
- clinic_id
- event_type
- event_name
- scheduled_month
- amount_estimated
- certainty_level
- is_recurring
- recurrence_type
- recurrence_interval
- recurrence_end_month
- current_amount
- new_amount
- change_start_month
- change_end_month
- memo
- source_type
- source_draft_id
- status
- created_at
- updated_at
- confirmed_at
- confirmed_by

### analysis_results
- analysis_result_id
- clinic_id
- year_month
- analysis_type
- source_report_id
- generated_at
- summary_text
- key_points_json
- anomaly_flags_json
- prompt_version
- is_latest

### loan_schedule_drafts
- loan_schedule_draft_id
- clinic_id
- source_file_id
- lender_name
- loan_name
- monthly_payment
- repayment_start_month
- repayment_end_month
- balloon_payment_month
- balloon_payment_amount
- memo
- draft_status
- created_at
- updated_at

---

## enum定義
以下のenumを定義してください。

### file_type
- monthly_report_pdf
- pl_csv
- bs_csv
- loan_schedule_pdf

### statement_type
- pl
- bs

### data_status
- confirmed
- provisional
- invalid

### draft_status
- draft
- reviewing
- confirmed
- invalid

### event_type
- loan_repayment
- lease_fee
- lease_renewal
- renewal_fee
- repair_cost
- tax_payment
- bonus_payment
- asset_purchase
- other_cash_out

### certainty_level
- confirmed
- estimated
- tentative

### source_type
- manual
- loan_schedule_pdf

### record_status
- active
- invalid

### parse_status
- uploaded
- parsed
- parse_error

---

## バックエンドAPI実装対象
以下のAPIを実装してください。

### 1. クリニック
- `GET /api/clinics`
- `GET /api/clinics/[clinicId]`

### 2. ファイル
- `POST /api/files/upload`
- `GET /api/files`
- `GET /api/files/[fileId]`

### 3. 月報
- `POST /api/monthly-reports/drafts/from-pdf`
- `GET /api/monthly-reports/drafts/[reportDraftId]`
- `PATCH /api/monthly-reports/drafts/[reportDraftId]`
- `POST /api/monthly-reports/drafts/[reportDraftId]/confirm`
- `GET /api/monthly-reports/[clinicId]/[yearMonth]`
- `GET /api/monthly-reports`

### 4. 月次推移
- `POST /api/financial-lines/import-csv`
- `GET /api/financial-lines/import-results/[fileId]`
- `GET /api/financial-lines`
- `GET /api/financial-lines/summary`

### 5. 将来イベント
- `GET /api/cash-events`
- `POST /api/cash-events`
- `PATCH /api/cash-events/[cashEventId]`
- `POST /api/cash-events/[cashEventId]/invalidate`

### 6. 集約表示
- `GET /api/monthly-detail`
- `GET /api/dashboard`

---

## APIの振る舞い要件

### files/upload
- multipart/form-data を受け取る
- ファイルを保存
- raw_files レコード作成
- parse_status は最初 uploaded

### monthly-reports/drafts/from-pdf
このフェーズでは、**本格PDF解析は不要**です。  
代わりに次の仮実装で構いません。

- file_id を受け取る
- monthly_report_drafts に空またはダミー初期値で1件作る
- draft_status=draft
- 後でPDF解析実装を差し替えやすい構造にする

### monthly-reports/drafts/[id]/confirm
- 入力済みドラフトを monthly_reports にコピー
- 同じ clinic_id + year_month の旧 is_latest=true を false
- 新レコード is_latest=true
- ドラフトの draft_status=confirmed

### financial-lines/import-csv
このフェーズでは、CSV取込を最低限実装してください。

要件:
- file_id を受け取る
- raw_files から file_type を見て statement_type を判断
- CSVを読み込む
- 月列を認識する簡易ロジックを入れる
- 縦持ちに変換して monthly_financial_lines に保存
- 同じ clinic_id + statement_type + year_month の旧 is_latest=true を false

※ 厳密なフォーマット依存ロジックはあとで改善できるよう、パーサーをサービス層へ分離してください。

### cash-events
通常のCRUDを実装してください。  
無効化は物理削除ではなく status=invalid にしてください。

### monthly-detail
このフェーズでは骨格APIで構いません。  
次をまとめて返してください。

- 月報正式データ
- PL summary
- BS summary
- cash_events の当月分簡易一覧

比較計算やAIコメントはまだ不要です。

### dashboard
このフェーズでは骨格APIで構いません。  
次を返してください。

- 直近 month の月報サマリー
- PL summary
- BS summary
- 今後3か月の cash_events 件数と合計

---

## サービス層の構成
以下のように責務分離してください。

- `fileStorageService`
- `monthlyReportDraftService`
- `monthlyReportConfirmService`
- `financialCsvImportService`
- `cashEventService`
- `monthlyDetailService`
- `dashboardService`

今後追加予定のため、以下も空でもよいので置き場所を作ってください。

- `loanScheduleDraftService`
- `analysisService`
- `comparisonService`
- `projectionService`

---

## バリデーション要件

### monthly_report_draft confirm時
最低限これを必須にしてください。
- clinic_id
- year_month
- data_status
- patient_count
- insurance_points
- medical_revenue

data_status=provisional の場合は追加で
- elapsed_working_days
- planned_working_days

### cash_event create/update時
- clinic_id 必須
- event_type 必須
- event_name 必須
- scheduled_month 必須
- amount_estimated 必須

### financial-lines/import-csv
- file_id 必須
- raw_files に存在すること
- file_type が pl_csv or bs_csv であること

---

## 実装上の注意
- 日付ではなく年月は `YYYY-MM` 文字列でもよいが、扱いは一貫させること
- 今後の拡張を考え、比較計算ロジックはAPIハンドラに直書きしない
- Prisma transaction を使って is_latest の切替を安全に行うこと
- 例外は API レスポンスとして分かる形で返すこと
- ログは最低限入れること
- テストしやすいように、パーサーとDB更新処理を分けること

---

## テスト対象
最低限、以下のテストを追加してください。

### DB / Service
- monthly_report confirmで旧 is_latest が落ちる
- cash_event invalidate で status が invalid になる
- financial CSV import で旧最新版が落ちる

### API
- files/upload
- monthly-reports confirm
- cash-events create/update/invalidate
- financial-lines import-csv

---

## このフェーズで不要なもの
以下は実装しないでください。

- AIコメント生成
- 対話API
- 返済予定表PDF解析本体
- 精密なPDF解析
- 前月比、前年同月比、3か月平均比較
- 暫定月予想着地計算
- 会計推移の高度な集計
- フロントの完成度の高いUI

---

## 成果物として期待するもの
- Prisma schema
- migration
- API route handlers
- service 層
- CSV import の最低限動く実装
- 月報ドラフト→確定の流れが動く実装
- cash_events CRUD
- monthly-detail / dashboard の骨格API
- 最低限のテスト
