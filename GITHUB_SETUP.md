# GitHubリポジトリへのプッシュ手順

このドキュメントでは、Alexa Sleep Controllerプロジェクトを新しいGitHubリポジトリにプッシュする方法を説明します。

## 準備

1. [GitHub](https://github.com/)にアカウントを持っていることを確認します
2. 新しい空のリポジトリを作成します（README、.gitignore、ライセンスなしで）

## ローカル環境で必要なファイル

プロジェクトには以下の重要なファイルが含まれています：

- `main.py`: アプリケーションのエントリーポイント
- `app.py`: Flaskアプリケーションとルート
- `auth.py`: 認証機能
- `sleep_controller.py`: スリープ制御機能
- `win_service.py`: Windowsサービス実装
- `install_service.bat`: サービスインストールスクリプト
- `templates/`: HTMLテンプレート
- `static/`: CSSとその他の静的ファイル
- `.gitignore`: Gitで無視するファイル（作成済み）

## プッシュ手順

ローカルマシンで以下の手順を実行します：

```bash
# Replitからプロジェクトファイルをダウンロード

# リポジトリを初期化
git init

# ファイルをステージング
git add .

# 最初のコミット
git commit -m "Initial commit: Alexa Sleep Controller for Windows"

# リモートリポジトリを追加（URLをあなたのリポジトリURLに置き換えてください）
git remote add origin https://github.com/yourusername/alexa-sleep-controller.git

# プッシュ
git push -u origin main
```

## requirements.txtファイル

GitHubプロジェクトには以下の依存関係を含むrequirements.txtファイルを作成することをお勧めします：

```
flask==2.3.3
flask-login==0.6.2
flask-sqlalchemy==3.1.1
flask-wtf==1.2.1
gunicorn==23.0.0
pywin32==306; platform_system == "Windows"
waitress==2.1.2
werkzeug==2.3.7
email-validator==2.1.0
pyopenssl==23.2.0
```

## ライセンス

MITライセンスなど、適切なライセンスファイルを追加することを検討してください。

## その他の推奨事項

- リリースを作成：インストール可能なパッケージとしてリリースを作成
- `CONTRIBUTING.md`を追加：他の開発者が貢献する方法を説明
- 詳細なセットアップドキュメントを追加：Windowsサービスのトラブルシューティングなど