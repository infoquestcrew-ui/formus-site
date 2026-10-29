# GitHubでの確認と反映

リポジトリ: https://github.com/infoquestcrew-ui/formus-site

現在の確認用ブランチ: `design-solvvy-refresh`

このブランチではTOPの動画を削除し、Solvvyの実画面を参照して、大きな英字・ロゴ描画・見出しマスク・文字と写真のスクロール連動・浮く固定ヘッダーを実装しています。サービス詳細とお問い合わせも同じデザインに刷新しています。
英語の帯はスクロールせずに流れ続けます。NEWS・写真下の文言・右上の補足ラベル・独立した停止ボタンは削除し、Aboutの本文は一続きにしています。背面ロゴはマウスに追従しません。
現在のリポジトリはユーザーの設定によりPublicです。確認用ブランチをPagesで公開し、mainは前回の状態を保持します。

## 1. 今回のファイルを開く

1. GitHubにログインしてリポジトリを開く。
2. ファイル一覧の左上のブランチ選択で `design-solvvy-refresh` を選ぶ。
3. `designs` フォルダーで確認用の画像を見る。

ブランチの直接リンク:
https://github.com/infoquestcrew-ui/formus-site/tree/design-solvvy-refresh

画像だけではスクロール演出を確認できないため、実際の動作は次の方法で確認します。

## 2. 自分のPCで無料で動かす

1. `design-solvvy-refresh` を選んだ状態で、緑の **Code → Download ZIP** を押す。
2. ダウンロードしたZIPを展開する。
3. 無料のVisual Studio Codeで、`index.html` が入っているフォルダーを開く。
4. VS Codeの拡張機能から **Live Server** をインストールする。
5. `index.html` を右クリックし、**Open with Live Server** を選ぶ。
6. 開いたブラウザで各セクション、流れる英語、メニューを確認し、事業内容とお問い合わせページも開く。

Python 3が導入されているPCでは、フォルダー内で次を実行する方法も使えます。

```bash
python3 -m http.server 4174 --bind 127.0.0.1
```

OSやブラウザの「視差効果を減らす」「動きを減らす」が有効な場合、アニメーションは自動的に抑制されます。

## 3. 確認済みの変更をmainに反映する

デザインの確認後、mainに採用する際に行います。

1. 次の比較画面を開く。
   https://github.com/infoquestcrew-ui/formus-site/compare/main...design-solvvy-refresh
2. **base: main / compare: design-solvvy-refresh** になっていることを確認する。
3. **Create pull request** を押す。
4. 差分を確認し、**Merge pull request → Confirm merge** を押す。

この操作でソースコードの変更がmainに反映されます。サイトの公開には公開先の設定も必要です。

## 4. インターネット上で公開する場合

現在のリポジトリはPublicなので、無料のGitHub Pagesを利用できます。

GitHub Pagesは設定済みです。公開元は `design-solvvy-refresh` ブランチの `/ (root)` で、このブランチの更新が自動反映されます。最初の設定をやり直す必要はありません。

確認用サイトの設定は次のとおりです。

1. リポジトリの **Settings → Pages** を開く。
2. Source は **Deploy from a branch**。
3. Branch は **design-solvvy-refresh**、Folder は **/ (root)**。
4. 設定を変更した場合は **Save** を押す。
5. デプロイ完了後、同じ画面の **Visit site** を開く。

公開URL:

- TOP: https://infoquestcrew-ui.github.io/formus-site/
- 事業内容: https://infoquestcrew-ui.github.io/formus-site/service/
- お問い合わせ: https://infoquestcrew-ui.github.io/formus-site/contact.html

mainへのマージ後に、公開対象もmainに切り替えたい場合は、上記Branchを **main** に変更してSaveを押します。
確認用ブランチの更新は、そのブランチをPagesの公開対象にしている間だけ自動反映されます。

今後リポジトリをPrivateに戻す場合、GitHubの無料プランではPagesを利用できなくなります。
コードを非公開のまま無料でサイトを公開したい場合は、Cloudflare Pagesなど別の公開先が必要です。

お問い合わせフォームは入力確認のみのデモで、実際のメール送信は行いません。

現在のFORMUSのXserverへ設置する場合は、[Xserverへの設置手順](XSERVER_SETUP.md) と専用ZIPを使用してください。専用ZIPはPHPで `info@formus.jp` に送信するフォームを含みます。
