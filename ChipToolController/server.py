from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route('/ls', methods=['GET'])
def run_ls():
    try:
        # コマンドを実行し、結果を取得
        result = subprocess.run(['ls'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            # 成功時の出力を返す
            return jsonify(output=result.stdout.split('\n'))
        else:
            # エラー時の出力を返す
            return jsonify(error=result.stderr), 500
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
#    app.run(host='localhost', port=8082)
    app.run(host='0.0.0.0', port=8082, debug=False)

