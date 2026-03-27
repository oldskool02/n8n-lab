from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route('/recover', methods=['POST'])
def recover():
    try:
        subprocess.Popen(
            ["/home/ianw/scripts/full-recovery.sh"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return jsonify({"status": "Recovery started"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "OK"}), 200

@app.route('/')
def home():
    return """
    <h1>Recovery Service Running</h1>
    <p>Status: OK</p>
    <p>Use the recovery UI to trigger restore.</p>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
