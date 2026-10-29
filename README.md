# FORMUS Webサイト

https://formus.jp/ の構成・文章・ロゴ・画像を使用した静的サイトです。
TOPページはミントグリーン、深いグリーン、オフホワイトを使った新しいデザインの初稿です。
サービス詳細とお問い合わせの下層ページは、前回制作した状態を保持しています。
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

- `/` — 動画付きの新TOPページ、NEWS、私たちについて、2つの事業紹介、会社概要、お問い合わせ。
- `/service/` — アウトソーシング事業とリクルーティング事業。
- `/contact.html` — お問い合わせフォームと個人情報の取り扱いモーダル。
- PC・スマートフォンのレイアウト、キーボード対応メニュー、アンカー移動、動画再生・停止、お知らせダイアログ、入力必須チェック。

画像、動画、CSS、JavaScript、フォントはローカルに保存しています。
サイトを開く際の外部 CDN・Google Fonts・アクセス解析への通信はありません。
`asset-sources.json` に取得元・取得時のサイズ・SHA-256 を記録しています。
フォントの CSS はフォント名を元サイトに合わせて変更しています。

フォームはデモ動作です。入力内容は保存・外部送信されず、送信ボタンは入力確認の結果を表示します。
元サイトのフォーム送信先と Google Analytics は除去しています。
検索への登録を避けるため、`noindex` と `robots.txt` を設定しています。

## 検証

開発サーバーを起動してから、クラウド環境に既存の Playwright と Chromium で動作確認できます。

```bash
python3 tools/check_site.py
```

スクリーンショットと確認結果は Git の追跡対象外の `artifacts/` に出力します。

TOPデザイン確認用の画像は `artifacts/formus-top-hero.jpg`、`artifacts/formus-top-desktop.jpg`、`artifacts/formus-top-mobile.jpg` です。
TOPの独自スタイルと処理は `assets/css/home.css` と `assets/js/home.js` に分離しています。
参考サイトの CSS や JavaScript は使用していません。

GitHub上でも確認できる画像を `designs/` に保存しています。
参考指定の `tokyotechnology.jp` と `brain-forest.net` は制作時点で通信許可待ちのため、直接比較を行う前の初稿です。

- [TOP冒頭のデザイン](designs/formus-top-hero.jpg)
- [PC：TOP全体](designs/formus-top-desktop.jpg)
- [スマートフォン：TOP全体](designs/formus-top-mobile.jpg)

## 依存素材

サイトの文章、ロゴ、画像、動画、元のスタイルは参照サイト由来です。
外部ライブラリは Swiper 8.4.7、Modaal 0.4.4、および参照サイトの jQuery 1.11.1。
フォントは Noto Sans JP（Fontsource 5.3.1）と Antonio（Fontsource 5.3.0）です。
同梱のライブラリ・フォントのライセンスは `assets/vendor/` にあります。

GitHub リポジトリ: https://github.com/infoquestcrew-ui/formus-site

## GitHub Pages への公開

ページや画像へのリンクは相対パスで、`/formus-site/` のようなサブディレクトリでも動作します。
ブラウザからアップロードするファイルは次でまとめられます。

```bash
python3 tools/package_site.py
```

`artifacts/formus-site-upload.zip` を解凍し、`index.html` が見える階層の中身を GitHub リポジトリの直下にアップロードします。ZIP 自体はアップロードしません。
公開用は Google Fonts の Noto Sans JP 2.004 の単一フォントを使用し、100 ファイル未満・各ファイル 25 MB 未満にまとめています。
GitHub の Settings → Pages で、Source を Deploy from a branch、Branch を main、フォルダーを / (root) にして Save を押します。
デプロイが終わったら、同じ画面の Visit site から公開 URL を開けます。

公開用アーカイブの確認には、`artifacts/pages-preview` を別ポートで配信し、`SITE_BASE_URL` に `/formus-site` を含めて `tools/check_site.py` を実行できます。
