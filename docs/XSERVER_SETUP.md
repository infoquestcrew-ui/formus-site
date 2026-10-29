# Xserverで現在のFORMUSサイトと差し替える手順

サーバーとドメインは現在のXserverをそのまま使います。DNS・ネームサーバー・ドメインの移管は不要です。GitHub Pagesの独自ドメイン設定も行いません。

新しいサイトはHTML・CSS・JavaScriptで表示し、お問い合わせの送信だけPHPで処理します。データベースやWordPressのインストールは不要です。

お問い合わせの受信先・送信元は `info@formus.jp`、メールに返信すると入力者のアドレスへ返信できます。自動返信メールは送信しません。メールアドレスのパスワード入力は不要です。

## 1. アップロード用ZIPをダウンロード

以下の2つをパソコンへ保存します。GitHubの「Code → Download ZIP」で取得する開発用一式とは異なります。

- [確認用ZIPをダウンロード](https://infoquestcrew-ui.github.io/formus-site/downloads/formus-xserver-preview.zip)
- [本番用ZIPをダウンロード](https://infoquestcrew-ui.github.io/formus-site/downloads/formus-xserver-public.zip)

確認用は検索への登録を抑制したファイルです。確認用でもフォームを送信すると実際に `info@formus.jp` にメールを送ります。本番用は検索除外を解除し、FORMUSのURLを設定したファイルです。

GitHub上の確認サイトはこれまで通り入力確認のみです。PHPによるメール送信はXserverに配置したファイルで動きます。

## 2. 現在のサイトをバックアップ

添付画像の画面から、左側の `formus.jp` を開きます。通常、その中に `public_html` フォルダーがあります。ここがサイトの公開先です。

```text
formus.jp/
├─ public_html/          ← サイトのファイル
├─ mail/                 ← メール関連。変更しません
└─ その他の設定フォルダー
```

1. `formus.jp` を開いた状態で、右側の `public_html` を選択します。
2. 上の **圧縮** をクリックし、ZIPでバックアップを作ります。
3. 作成されたZIPを選択し、**ダウンロード** でパソコンにも保存します。
4. バックアップは `formus.jp` の直下など、`public_html` の外に保管してください。

バックアップには隠しファイルの `.htaccess` も含めます。ダウンロードしたZIPに元の `index.html` や画像が入っていることを確認してから進みます。

`public_html` フォルダーそのものを削除・名前変更する必要はありません。`mail`・`ssl`・`.spamassassin` なども変更しません。

`public_html` 内に `wp-admin`・`wp-content` がある場合はWordPressの可能性があります。その場合はこのHTMLサイトの上書き手順を実行せず、既存の構成を確認してください。

## 3. 現在のサイトを残したまま確認用ページを設置

1. `formus.jp → public_html` を開きます。
2. 上の **新規フォルダ** で `renewal-preview` を作成します。
3. `renewal-preview` を開きます。
4. 上の **アップロード** から、確認用の `formus-xserver-preview.zip` をアップロードします。
5. アップロードしたZIPを選択し、上の **展開** をクリックします。
6. 展開先を確認し、`renewal-preview` の直下に次のファイルが並ぶようにします。余分な親フォルダーが作られた場合は、中身を `renewal-preview` 直下へ移します。

```text
public_html/
└─ renewal-preview/
   ├─ index.html
   ├─ contact.html
   ├─ contact-submit.php
   ├─ robots.txt
   ├─ assets/
   └─ service/
```

次のURLを開くと、新しいサイトだけ確認できます。

**https://formus.jp/renewal-preview/**

現在の `https://formus.jp/` の表示は、この段階では変わりません。確認用URLは公開URLなので、URLを知っている人は閲覧できます。

展開後の確認用ZIPはサーバーから削除して構いません。展開済みファイルは残します。

## 4. PHPとメールを確認

Xserverの **サーバーパネル → PHP Ver.切替** で `formus.jp` のPHPバージョンを確認します。PHP 8.3以上のサポート中のバージョンを使用してください。すでに条件を満たしていれば変更不要です。同じドメインで別のPHPアプリも動かしている場合は、その互換性も確認してから変更します。

1. `https://formus.jp/renewal-preview/contact.html` を開きます。
2. 必須項目と同意チェックを入力し、自分でテスト送信します。
3. 「お問い合わせを受け付けました」と表示されることを確認します。
4. **info@formus.jpの受信箱で、実際にメールが届いたことを確認します。**
5. 日本語の本文、入力者のアドレスへの返信、スマートフォンでの表示も確認します。

送信受付の表示だけでは、メールの到着までは確認できません。現在のサイトを差し替える前に、実際の受信を確認してください。

届かない場合は、迷惑メールフォルダーとXserverのWEBメールでも確認します。送信時にエラーが表示された場合は、表示された文言を控えて確認してください。コードの試験はローカルのメール受け取り用プログラムで行っており、Xserverでの実送信・到着はアップロード後の確認が必要です。

フォームは固定の `info@formus.jp` のみに送ります。入力内容の検証、同意チェック、別サイトからの送信対策、二重送信防止、連続送信制限を実装しています。実際の送信後、同じ接続元からの再送は1分ほど間隔を空けます。

## 5. 確認できたら本番サイトを差し替える

1. 現在のサイトのバックアップが手元にあることを再確認します。
2. ファイルマネージャで **`formus.jp/public_html`** を開きます。`renewal-preview` の中ではありません。
3. **アップロード** から、本番用の `formus-xserver-public.zip` をアップロードします。
4. ZIPを選択し、**展開** します。
5. 同じファイル名について上書きが表示されたら、本番用ファイルで上書きします。
6. 次のファイルが `public_html` の直下にあることを確認します。

```text
public_html/
├─ index.html
├─ contact.html
├─ contact-submit.php
├─ robots.txt
├─ sitemap.xml
├─ assets/
├─ service/
├─ .htaccess              ← 既存の設定を保持
└─ renewal-preview/       ← 確認用フォルダー
```

本番用ZIPには `.htaccess` を含めていません。既存のSSL・転送設定を上書きしないためです。他の既存ファイルを一括削除する必要もありません。

**上書き展開ができない場合:** 本番用ZIPをパソコンで展開し、FTPソフト等で中身を `public_html` にアップロードして同名ファイルを上書きします。外側の `formus-xserver-public` フォルダーごと置くと、トップページは切り替わりません。

この操作中はファイルごとに更新されるため、アクセスの少ない時間帯に行ってください。既存サイトに `index.php` や独自の転送・WordPressの設定がある場合は、優先して表示されるファイルや `.htaccess` の内容を確認してから切り替えます。

## 6. 本番の確認と片付け

- [TOP](https://formus.jp/)
- [事業内容](https://formus.jp/service/)
- [お問い合わせ](https://formus.jp/contact.html)

PCとスマートフォンで、写真・アニメーション・ページ移動・フォームの実受信を確認します。本番URLでも、テストを1回送信して受信を確認してください。

古い表示が出る場合はブラウザを強制再読み込みします。変わらなければ、XserverやCDN等のキャッシュが残っていないか確認します。

確認後、サーバー上のアップロードしたZIPは削除します。`renewal-preview` も不要になったら削除できます。バックアップはパソコンや公開領域外に残します。

問題があった場合は、バックアップを展開し、元のファイルと `.htaccess` を元の場所に戻します。旧サイトに存在しなかった `contact-submit.php` など今回追加したファイルは、今回追加したことを確認できるものだけ取り除きます。`mail` や `ssl` のフォルダーには触れません。

## ファイルを再生成・検証する場合

```bash
python3 tools/package_xserver.py
PHP_BIN=php python3 tools/check_xserver.py
```

`downloads/` に2種類のZIP、`artifacts/xserver/` に展開したファイルを生成します。検証では本物のメールを送信せず、ローカルのプログラムでメールの宛先・返信先・日本語本文・失敗時の動作を確認します。

## Xserver公式マニュアル

- [ファイルマネージャの操作](https://www.xserver.ne.jp/manual/man_tool_file.php)
- [初期フォルダーとpublic_html](https://www.xserver.ne.jp/manual/man_server_folder.php)
- [PHPのバージョン切り替え](https://www.xserver.ne.jp/manual/man_program_php_ver.php)
