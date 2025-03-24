"""
AWS Lambda統合モジュール

APIキー生成時にAWS Lambda関数を自動的に作成するための機能を提供します。
"""
import json
import logging
import os
import base64
import boto3
from botocore.exceptions import ClientError

# ロガー設定
logger = logging.getLogger(__name__)

# Lambda関数のコードテンプレート (Node.js)
NODEJS_LAMBDA_CODE = """
const axios = require('axios');

exports.handler = async function(event, context) {
    try {
        // リクエストからスキル情報を取得
        const alexaRequest = event.request || {};
        const alexaResponse = {
            version: '1.0',
            response: {
                outputSpeech: {},
                shouldEndSession: true
            }
        };

        // 特定のインテントかどうかを確認
        if (event.request && event.request.type === 'IntentRequest' && 
            event.request.intent && event.request.intent.name === 'SleepIntent') {
            
            // APIにスリープリクエストを送信
            const response = await axios.post('{{ENDPOINT_URL}}/api/sleep', {}, {
                headers: {
                    'Authorization': 'Bearer {{API_KEY}}'
                }
            });
            
            // 成功メッセージを設定
            alexaResponse.response.outputSpeech = {
                type: 'PlainText',
                text: 'コンピューターをスリープ状態にします。'
            };
            
            return alexaResponse;
        } else {
            // 対応していないリクエストの場合
            alexaResponse.response.outputSpeech = {
                type: 'PlainText',
                text: 'その操作はサポートされていません。コンピューターをスリープ状態にするには、「パソコンをスリープして」と言ってください。'
            };
            return alexaResponse;
        }
    } catch (error) {
        console.error('エラー:', error);
        
        // エラーレスポンスを返す
        return {
            version: '1.0',
            response: {
                outputSpeech: {
                    type: 'PlainText',
                    text: 'すみません、パソコンをスリープ状態にできませんでした。'
                },
                shouldEndSession: true
            }
        };
    }
};
"""

# Lambda関数のコードテンプレート (Python)
PYTHON_LAMBDA_CODE = """
import json
import urllib.request
import urllib.error
import logging

# ロガー設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # リクエストからスキル情報を取得
        request_type = event.get('request', {}).get('type')
        
        # レスポンス初期化
        response = {
            'version': '1.0',
            'response': {
                'outputSpeech': {},
                'shouldEndSession': True
            }
        }
        
        # 特定のインテントかどうかを確認
        if (request_type == 'IntentRequest' and 
            event.get('request', {}).get('intent', {}).get('name') == 'SleepIntent'):
            
            # APIにスリープリクエストを送信
            req = urllib.request.Request('{{ENDPOINT_URL}}/api/sleep', 
                                        data=None,
                                        headers={
                                            'Authorization': 'Bearer {{API_KEY}}'
                                        },
                                        method='POST')
            
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                logger.info(f"API response: {result}")
            
            # 成功メッセージを設定
            response['response']['outputSpeech'] = {
                'type': 'PlainText',
                'text': 'コンピューターをスリープ状態にします。'
            }
            
        else:
            # 対応していないリクエストの場合
            response['response']['outputSpeech'] = {
                'type': 'PlainText',
                'text': 'その操作はサポートされていません。コンピューターをスリープ状態にするには、「パソコンをスリープして」と言ってください。'
            }
        
        return response
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        
        # エラーレスポンスを返す
        return {
            'version': '1.0',
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': 'すみません、パソコンをスリープ状態にできませんでした。'
                },
                'shouldEndSession': True
            }
        }
"""

# Zipファイル作成用のヘルパー関数
def create_lambda_package(code, runtime):
    """
    Lambda関数用のデプロイパッケージを作成
    
    Args:
        code (str): Lambda関数のコード
        runtime (str): ランタイム ("nodejs" または "python")
        
    Returns:
        bytes: Zipファイルのバイナリデータ
    """
    import io
    import zipfile
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
        if runtime == "nodejs":
            zip_file.writestr('index.js', code)
        else:  # python
            zip_file.writestr('lambda_function.py', code)
    
    zip_buffer.seek(0)
    return zip_buffer.read()

def create_lambda_function(api_key, endpoint_url, aws_access_key=None, aws_secret_key=None, 
                          aws_region='us-east-1', runtime="nodejs"):
    """
    AWS Lambda関数を作成する
    
    Args:
        api_key (str): 生成されたAPIキー
        endpoint_url (str): APIエンドポイントURL
        aws_access_key (str): AWS Access Key ID
        aws_secret_key (str): AWS Secret Access Key 
        aws_region (str): AWSリージョン
        runtime (str): ランタイム ("nodejs" または "python")
        
    Returns:
        dict: 作成されたLambda関数の情報
    """
    try:
        # AWSセッション設定
        session_kwargs = {}
        if aws_access_key and aws_secret_key:
            session_kwargs['aws_access_key_id'] = aws_access_key
            session_kwargs['aws_secret_access_key'] = aws_secret_key
        
        session = boto3.Session(region_name=aws_region, **session_kwargs)
        lambda_client = session.client('lambda')
        
        # ランタイム設定
        if runtime == "nodejs":
            runtime_str = "nodejs18.x"
            code_template = NODEJS_LAMBDA_CODE
            handler = "index.handler"
        else:  # python
            runtime_str = "python3.9"
            code_template = PYTHON_LAMBDA_CODE
            handler = "lambda_function.lambda_handler"
        
        # コード内のプレースホルダーを置換
        code = code_template.replace("{{API_KEY}}", api_key).replace("{{ENDPOINT_URL}}", endpoint_url)
        
        # Lambdaロール作成（もしくは既存のロールを使用）
        iam = session.client('iam')
        role_name = 'alexa_sleep_controller_role'
        
        # ロールが存在するか確認
        try:
            role_response = iam.get_role(RoleName=role_name)
            role_arn = role_response['Role']['Arn']
        except ClientError:
            # ロールが存在しない場合は作成
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            role_response = iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Role for Alexa Sleep Controller Lambda function'
            )
            
            # 基本的なログ記録ポリシーをアタッチ
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
            
            role_arn = role_response['Role']['Arn']
            
            # ロールが有効になるまで少し待機
            import time
            time.sleep(10)
        
        # Lambda関数パッケージを作成
        zip_file = create_lambda_package(code, runtime)
        
        # Lambda関数を作成
        function_name = f"AlexaSleepController_{base64.b32encode(os.urandom(3)).decode('utf-8').lower()}"
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime=runtime_str,
            Role=role_arn,
            Handler=handler,
            Code={'ZipFile': zip_file},
            Description='Lambda function to control PC sleep via Alexa',
            Timeout=10,
            MemorySize=128,
            Publish=True,
            Tags={
                'Service': 'AlexaSleepController'
            }
        )
        
        # Alexaスキルのエンドポイントとして設定するための権限を追加
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId='alexa-skill-kit-statement',
            Action='lambda:InvokeFunction',
            Principal='alexa-appkit.amazon.com',
            SourceAccount=session.client('sts').get_caller_identity()['Account']
        )
        
        logger.info(f"Lambda function created: {function_name}")
        
        return {
            'function_name': function_name,
            'function_arn': response['FunctionArn'],
            'runtime': runtime_str,
            'region': aws_region
        }
    
    except Exception as e:
        logger.error(f"Lambda function creation failed: {str(e)}")
        raise

def generate_alexa_skill_json(lambda_arn):
    """
    Alexaスキル定義JSONを生成する
    
    Args:
        lambda_arn (str): Lambda関数のARN
        
    Returns:
        str: Alexaスキル定義JSON
    """
    skill_json = {
        "manifest": {
            "publishingInformation": {
                "locales": {
                    "ja-JP": {
                        "name": "パソコンスリープ",
                        "summary": "Windowsコンピューターをスリープ状態にします",
                        "description": "このスキルを使用すると、Alexaの音声コマンドでWindowsコンピューターをスリープ状態にできます。「アレクサ、パソコンをスリープして」と言うだけです。",
                        "examplePhrases": [
                            "アレクサ、パソコンをスリープして",
                            "アレクサ、コンピューターをスリープモードにして",
                            "アレクサ、PCをスリープ状態にして"
                        ],
                        "keywords": [
                            "スリープ",
                            "PC",
                            "パソコン",
                            "コンピューター",
                            "電源管理"
                        ]
                    },
                    "en-US": {
                        "name": "PC Sleep Controller",
                        "summary": "Put your Windows computer to sleep",
                        "description": "This skill allows you to put your Windows computer to sleep using voice commands with Alexa. Just say 'Alexa, put my computer to sleep'.",
                        "examplePhrases": [
                            "Alexa, put my computer to sleep",
                            "Alexa, sleep my PC",
                            "Alexa, turn my computer to sleep mode"
                        ],
                        "keywords": [
                            "sleep",
                            "PC",
                            "computer",
                            "power management"
                        ]
                    }
                },
                "isAvailableWorldwide": False,
                "testingInstructions": "Ensure your Windows computer is running the Alexa Sleep Controller service.",
                "category": "SMART_HOME",
                "distributionCountries": [
                    "JP",
                    "US"
                ]
            },
            "apis": {
                "custom": {
                    "endpoint": {
                        "uri": lambda_arn
                    }
                }
            },
            "manifestVersion": "1.0",
            "permissions": [],
            "privacyAndCompliance": {
                "allowsPurchases": False,
                "locales": {
                    "ja-JP": {
                        "privacyPolicyUrl": "",
                        "termsOfUseUrl": ""
                    },
                    "en-US": {
                        "privacyPolicyUrl": "",
                        "termsOfUseUrl": ""
                    }
                },
                "isExportCompliant": True,
                "containsAds": False,
                "isChildDirected": False,
                "usesPersonalInfo": False
            }
        },
        "interactionModel": {
            "ja-JP": {
                "interactionModel": {
                    "languageModel": {
                        "invocationName": "パソコンスリープ",
                        "intents": [
                            {
                                "name": "AMAZON.CancelIntent",
                                "samples": []
                            },
                            {
                                "name": "AMAZON.HelpIntent",
                                "samples": []
                            },
                            {
                                "name": "AMAZON.StopIntent",
                                "samples": []
                            },
                            {
                                "name": "SleepIntent",
                                "slots": [],
                                "samples": [
                                    "パソコンをスリープして",
                                    "コンピューターをスリープして",
                                    "PCをスリープ状態にして",
                                    "パソコンをスリープモードにして",
                                    "コンピューターをスリープモードにして",
                                    "スリープモードにして",
                                    "スリープして"
                                ]
                            }
                        ],
                        "types": []
                    }
                }
            },
            "en-US": {
                "interactionModel": {
                    "languageModel": {
                        "invocationName": "pc sleep",
                        "intents": [
                            {
                                "name": "AMAZON.CancelIntent",
                                "samples": []
                            },
                            {
                                "name": "AMAZON.HelpIntent",
                                "samples": []
                            },
                            {
                                "name": "AMAZON.StopIntent",
                                "samples": []
                            },
                            {
                                "name": "SleepIntent",
                                "slots": [],
                                "samples": [
                                    "put my computer to sleep",
                                    "sleep my pc",
                                    "put my pc to sleep",
                                    "turn my computer to sleep mode",
                                    "sleep mode",
                                    "go to sleep mode",
                                    "sleep my computer"
                                ]
                            }
                        ],
                        "types": []
                    }
                }
            }
        }
    }
    
    return json.dumps(skill_json, indent=2)

def get_alexa_skill_setup_instructions(lambda_info):
    """
    Alexaスキルの設定手順を生成する
    
    Args:
        lambda_info (dict): Lambda関数の情報
        
    Returns:
        str: 設定手順
    """
    instructions = f"""
# Alexaスキルの設定手順

Lambda関数が正常に作成されました。以下の情報を使ってAlexaスキルを設定してください。

## Lambda関数情報

- **関数名**: {lambda_info['function_name']}
- **ARN**: {lambda_info['function_arn']}
- **リージョン**: {lambda_info['region']}
- **ランタイム**: {lambda_info['runtime']}

## Alexaスキル設定手順

1. [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)にアクセスします

2. **「スキルの作成」**をクリックします

3. スキル名を「パソコンスリープ」（日本語）または「PC Sleep Controller」（英語）に設定します

4. **「カスタム」**モデルを選択し、**「作成」**をクリックします

5. サイドバーから**「エンドポイント」**を選択します

6. **「AWS Lambda ARN」**を選択し、以下のARNを入力します:
   - デフォルトのリージョン: `{lambda_info['function_arn']}`

7. **「保存」**をクリックします

8. サイドバーから**「対話モデル」** → **「JSONエディター」**を選択します

9. 以下のJSONをアップロードするか、コピー＆ペーストしてください:

```json
{json.dumps(json.loads(generate_alexa_skill_json(lambda_info['function_arn']))['interactionModel']['ja-JP'], indent=2, ensure_ascii=False)}
```

10. **「保存」**をクリックし、**「モデルを構築」**をクリックします

11. 構築が完了したら、**「テスト」**タブに移動します

12. テストを有効にし、「アレクサ、パソコンをスリープして」と入力してテストします

## 確認

スキルが正常に設定されると、Alexaデバイスで「アレクサ、パソコンスリープを開いて」と言った後、
「パソコンをスリープして」と言うことでコンピューターをスリープ状態にできます。
    """
    
    return instructions