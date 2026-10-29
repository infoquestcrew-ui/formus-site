# GitHubでの確認と反映

リポジトリ: https://github.com/infoquestcrew-ui/formus-site

現在の確認用ブランチ: `design-solvvy-refresh`

このブランチではTOPの動画を削除し、スクロール表示の仕組みを先行実装しています。
Solvvyの画面と実際の動きの確認は通信許可待ちです。比較・調整が終わるまで、Solvvyに合わせた最終版としては扱わないでください。
リポジトリのPrivate設定は変更していません。

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
6. 開いたブラウザでページをスクロールして、各セクション、メニュー、お知らせ表示を確認する。

Python 3が導入されているPCでは、フォルダー内で次を実行する方法も使えます。

```bash
python3 -m http.server 4174 --bind 127.0.0.1
```

OSやブラウザの「視差効果を減らす」「動きを減らす」が有効な場合、アニメーションは自動的に抑制されます。

## 3. 確認済みの変更をmainに反映する

Solvvyとの比較・調整とデザイン確認が終わってから行います。

1. 次の比較画面を開く。
   https://github.com/infoquestcrew-ui/formus-site/compare/main...design-solvvy-refresh
2. **base: main / compare: design-solvvy-refresh** になっていることを確認する。
3. **Create pull request** を押す。
4. 差分を確認し、**Merge pull request → Confirm merge** を押す。

この操作でソースコードの変更がmainに反映されます。サイトの公開には公開先の設定も必要です。

## 4. インターネット上で公開する場合

現在のリポジトリはPrivateです。GitHubの無料プランではPrivateリポジトリにGitHub Pagesを使えません。
Private設定を維持して無料でサイトを公開したい場合は、Cloudflare PagesなどPrivateリポジトリと連携できる公開先を利用します。
その場合、コードを非公開に保ててもサイトのURL自体は通常誰でも閲覧できます。

Cloudflare Pagesを使う場合の基本設定:

- GitHub接続先: `infoquestcrew-ui/formus-site`
- Production branch: `main`
- Framework preset: `None`
- Build command: 空欄（ビルド不要）
- Build output directory: `.`（index.htmlがあるリポジトリ直下）

GitHub Pagesを利用できるプランの場合は、リポジトリの **Settings → Pages** で次を指定します。

- Source: **Deploy from a branch**
- Branch: **main**
- Folder: **/ (root)**

保存後、デプロイが完了すると同じ画面の **Visit site** から公開URLを確認できます。
お問い合わせフォームは入力確認のみのデモで、実際のメール送信は行いません。
