# Windows用 Alexa スリープコントローラー

AWSを介してAmazon AlexaからWindowsをリモートでスリープ状態にするためのPythonベースのWindowsサービスです。

## 機能

- **リモートスリープ制御**: AlexaからのボイスコマンドでWindowsをスリープ状態に
- **安全なAPI**: APIキー認証によって保護されたエンドポイント
- **Windowsサービス**: バックグラウンドでWindowsサービスとして動作
- **Webコントロールパネル**: APIキーの管理とスリープリクエストの監視のためのシンプルなダッシュボード
- **ログ記録**: トラブルシューティングのための詳細なログ
- **多言語対応**: 日本語と英語のインターフェース

## インストール

### 必要条件

- Windows 10以降
- Python 3.6以降
- 管理者権限（サービスインストール用）

### セットアップ手順

1. **パッケージをダウンロード**して、お好みの場所に展開します。

2. **インストーラーを実行**:
   - `install_service.bat`をダブルクリックして、サービスをインストールし、起動します。
   - このスクリプトは必要なPythonパッケージをインストールし、Windowsサービスをセットアップします。

3. **コントロールパネルにアクセス**:
   - Webブラウザを開き、次のURLに移動: `http://localhost:5000`
   - デフォルトのログイン情報:
     - ユーザー名: `admin`
     - パスワード: `admin`
   - **重要**: セキュリティのためにこれらの認証情報を変更してください！

4. **APIキーを生成**:
   - コントロールパネルで「新しいキーを生成」をクリック
   - このキーを安全に保存してください - 一度だけ表示されます

## Alexa連携のセットアップ

### 方法1: 自動AWS Lambda統合（推奨）

このアプリケーションには、AWS Lambda関数を自動的に生成して設定する機能が追加されました：

1. **AWS Lambda統合でAPIキーを生成**:
   - コントロールパネルで「新しいキーを生成」をクリックし、「APIキー生成とAWS Lambda連携」を選択
   - AWS認証情報と希望の設定を入力
   - システムがエンドポイントと連携するLambda関数を自動的に作成

2. **Alexaスキルの設定**:
   - 成功ページに表示される手順に従う
   - Alexaスキル用に生成されたJSONをコピー
   - Alexa開発者コンソールと提供されたLambda ARNを使用してスキルを設定

### 方法2: 手動設定

AWS Lambdaを手動で設定する場合：

1. **AWS Lambda関数を作成**:
   - AWS Lambdaに移動し、新しい関数を作成
   - Node.jsまたはPythonランタイムを使用
   - APIキーを使用してエンドポイントにPOSTリクエストを送信するコードを実装

2. **Alexaスキルを作成**:
   - Alexa Developer Consoleでカスタムスキルを作成
   - スリープモード起動のためのインテントを設定
   - スキルをLambda関数にリンク

### ネットワーク設定

ホームネットワーク外からPCにアクセスするには：

- ルーターでポート転送を設定（ポート5000をPCのローカルIPに転送）
- または、ngrokなどのサービスを使用して安全なトンネリングを設定

Windows環境の詳細なセットアップ手順については、[WINDOWS_SETUP.ja.md](WINDOWS_SETUP.ja.md)を参照してください。

## サンプルLambda関数（Node.js）

```javascript
const axios = require('axios');

exports.handler = async function(event, context) {
    try {
        const response = await axios.post('http://あなたのエンドポイント:5000/api/sleep', {}, {
            headers: {
                'X-API-Key': 'あなたのAPIキー'
            }
        });
        
        return {
            statusCode: 200,
            body: JSON.stringify('パソコンをスリープ状態にします。')
        };
    } catch (error) {
        console.error('エラー:', error);
        return {
            statusCode: 500,
            body: JSON.stringify('申し訳ありません、パソコンをスリープ状態にできませんでした。')
        };
    }
};
```

## トラブルシューティング

- サービスが起動しない場合は、Windowsのサービス管理コンソールでステータスを確認してください
- ファイアウォールがポート5000を許可していることを確認してください
- ログファイル `alexa_sleep.log` でエラーメッセージを確認してください

## ライセンス

MITライセンス

## 貢献

Issueや改善の提案は大歓迎です！詳しくは[CONTRIBUTING.md](CONTRIBUTING.md)をご覧ください。