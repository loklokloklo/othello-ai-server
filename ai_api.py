from flask import Flask, request, jsonify
from flask_cors import CORS
from ai_player import decide_move

app = Flask(__name__)
CORS(app)  # ← この行を追加！

@app.route('/api/ai_move', methods=['POST'])
def get_ai_move():
    try:
        data = request.get_json(force=True)
        print('[AI API] 受信データ:', data)

        board = data['board']
        player = data['player']

        # 🔥 ここで変換！重要！
        player_val = 1 if player == 'black' else -1

        move = decide_move(board, player_val)
        print('[AI API] AIの着手:', move)

        return jsonify({'move': move})
    except Exception as e:
        print('[AI API] エラー:', e)
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)
