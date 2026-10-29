# FORMUS Webサイト

https://formus.jp/ の構成・文章・ロゴ・画像を使用した静的サイトです。
SolvvyのPC・スマートフォン画面と動きを確認し、FORMUSのグリーンに合わせて新規実装したデザイン案です。
TOP・サービス詳細・お問い合わせの3ページで、配色・書体・ヘッダー・フッターを統一しています。
既存の `infoquestcrew-ui` リポジトリは変更していません。

## 起動

Python 3 があれば起動できます。Node.js、パッケージのインストール、ビルド、API キーは不要です。

```bash
cd /workspace/formus-site
python3 -m http.server 4174 --bind 127.0.0.1
```

配信するディレクトリは、この README があるリポジトリ直下です。
任意の静的ホスティングにも配置できます。

## ページと機能

- `/` — 大きな英字とFORMUSロゴを中心にしたTOPページ、私たちについて、2つの事業紹介、会社概要、お問い合わせ。
- `/service/` — アウトソーシング事業とリクルーティング事業。
- `/contact.html` — お問い合わせフォームと個人情報の取り扱いモーダル。
- PC・スマートフォンのレイアウト、キーボード対応メニュー、アンカー移動、ロゴ描画、見出しのマスク表示、スクロール連動の文字・写真移動、ヘッダー追従、入力必須チェック。

Aboutはすべての段落を一続きの本文にまとめ、大きな写真と横並びにしています。
本文・写真を拡大し、サービス・会社概要・お問い合わせも上下の余白と文字サイズを調整しています。
写真下の小さな文言・セクション右上の補足ラベル・NEWS・独立した停止ボタンは削除しています。
ロゴは初回の描画とパーツの組み立て、ヘッダーロゴのホバー再描画、会社概要のスクロール連動に対応しています。TOP背面ロゴのマウス追従はありません。
英語の帯はスクロール操作に依存せず、右から左へ一定速度でつなぎ目なく流れ続けます。PCは約72px/秒、スマートフォンは約44px/秒です。
帯そのものをクリック、またはフォーカスしてEnter・Spaceを押すと帯だけ停止・再開できます。停止ボタンを別途表示することなく、キーボード操作にも対応しています。OSの「動きを減らす」も尊重します。

画像、CSS、JavaScript、フォントはローカルに保存しています。TOPの動画要素・再生操作・動画ファイルを削除し、動画のダウンロードも行いません。
サイトを開く際の外部 CDN・Google Fonts・アクセス解析への通信はありません。
`asset-sources.json` に取得元・取得時のサイズ・SHA-256 を記録しています。
フォントの CSS はフォント名を元サイトに合わせて変更しています。

GitHub Pagesの確認用フォームはデモ動作です。入力内容は保存・外部送信されず、確認ボタンは入力確認の結果を表示します。
事業紹介の本文・フォーム項目・個人情報の取り扱いの全10条を保持しています。個人情報の表示はブラウザ標準のダイアログを使い、Escapeや閉じるボタンで元の入力画面へ戻れます。
元サイトのフォーム送信先と Google Analytics は除去しています。
検索への登録を避けるため、`noindex` と `robots.txt` を設定しています。

## 検証

開発サーバーを起動してから、クラウド環境に既存の Playwright と Chromium で動作確認できます。

```bash
python3 tools/check_site.py
```

スクリーンショットと確認結果は Git の追跡対象外の `artifacts/` に出力します。

確認用画像と動きのGIFは、サーバー起動後に次で再生成できます。GIFの生成にはffmpegが必要です。

```bash
python3 tools/capture_preview.py --motion
```

デザイン確認用の画像は `designs/` に保存します。
共通スタイルと処理は `assets/css/home-v2.css` と `assets/js/home.js`、下層ページのレイアウトは `assets/css/pages.css`、フォームは `assets/js/contact.js` です。
参考サイトの CSS や JavaScript は使用していません。

GitHub上でも確認できる画像を `designs/` に保存しています。
参考指定の `solvvy.co.jp` は実画面とスクロール時の表示、見出しマスク・画像パララックスなどの動きを確認済みです。参考サイトのコードやロゴは同梱せず、FORMUSの素材と独自CSS・JavaScriptで実装しています。

- [TOP冒頭のデザイン](designs/formus-top-hero.jpg)
- [PC：TOP全体](designs/formus-top-desktop.jpg)
- [スマートフォン：TOP全体](designs/formus-top-mobile.jpg)
- [PC：事業内容](designs/formus-service-desktop.jpg)
- [スマートフォン：事業内容](designs/formus-service-mobile.jpg)
- [PC：お問い合わせ](designs/formus-contact-desktop.jpg)
- [スマートフォン：お問い合わせ](designs/formus-contact-mobile.jpg)
- [実際のブラウザで収録した動きのプレビュー](designs/formus-motion-preview.gif)
- [スクロールせずに流れる英語の帯](designs/formus-marquee-preview.gif)

## 依存素材

サイトの文章、ロゴ、画像はFORMUSの現行サイト由来です。
現行3ページの動作は独自JavaScriptとブラウザ標準機能で実装しており、旧版のSwiper・Modaal・jQueryは読み込みません。旧版のファイルとライセンスは同梱されています。
フォントは Noto Sans JP（Fontsource 5.3.1）と Antonio（Fontsource 5.3.0）、Poppins（Fontsource 5.3.0）です。
同梱のライブラリ・フォントのライセンスは `assets/vendor/` にあります。

GitHub リポジトリ: https://github.com/infoquestcrew-ui/formus-site

現在の確認用ブランチは `design-solvvy-refresh` です。`main` にはまだマージしていません。
GitHubでの確認・反映・公開の操作は [GitHub設定手順](docs/GITHUB_SETUP.md) を参照してください。

## GitHub Pages への公開

ページや画像へのリンクは相対パスで、`/formus-site/` のようなサブディレクトリでも動作します。
ブラウザからアップロードするファイルは次でまとめられます。

```bash
python3 tools/package_site.py
```

`artifacts/formus-site-upload.zip` を解凍し、`index.html` が見える階層の中身を GitHub リポジトリの直下にアップロードします。ZIP 自体はアップロードしません。
公開用は Google Fonts の Noto Sans JP 2.004 の単一フォントを使用し、100 ファイル未満・各ファイル 25 MB 未満にまとめています。
確認用のGitHub Pagesは設定済みです。公開URLは https://infoquestcrew-ui.github.io/formus-site/ です。Settings → Pages の公開元は Deploy from a branch、Branch は design-solvvy-refresh、フォルダーは / (root) で、このブランチの更新が自動反映されます。mainへの反映と公開ブランチの切り替えは docs/GITHUB_SETUP.md を参照してください。
デプロイが終わったら、同じ画面の Visit site から公開 URL を開けます。

公開用アーカイブの確認には、`artifacts/pages-preview` を別ポートで配信し、`SITE_BASE_URL` に `/formus-site` を含めて `tools/check_site.py` を実行できます。

## Xserverでformus.jpを差し替える場合

操作手順は [Xserverへの設置手順](docs/XSERVER_SETUP.md) にまとめています。公開先は既存の `formus.jp/public_html` です。DNSやネームサーバーは変更しません。

Xserver用は次の2種類です。

- [確認用ZIP](downloads/formus-xserver-preview.zip) — `renewal-preview/` へ設置し、現サイトを残して確認。
- [本番用ZIP](downloads/formus-xserver-public.zip) — 確認後、`public_html` 直下へ設置。

どちらもXserverのPHPで `info@formus.jp` にメールを送信します。送信元も同じアドレスで、入力者のアドレスをReply-Toに設定します。メールパスワード・SMTP認証情報・データベースは不要です。自動返信は行いません。

本番用では `noindex` を解除し、canonical・robots.txt・sitemap.xmlをFORMUSの本番URLに設定します。既存の `.htaccess` やSSL設定は含めず、上書きしません。GitHub Pagesで配信する確認用のHTML・フォームは変更しません。

```bash
python3 tools/package_xserver.py
PHP_BIN=php python3 tools/check_xserver.py
```

PHP 8.3以上のサポート中のバージョンを使用してください。検証ではメールをローカルで捕捉して外部へ送信しません。Xserverでの実際の受信は、設置後に確認する必要があります。
