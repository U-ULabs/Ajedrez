from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from chess_logic.game_manager import GameManager
import os

app = Flask(__name__, static_folder='frontend/dist', static_url_path='/')
CORS(app)  # Enable CORS for all routes (for dev)

game_manager = GameManager()

@app.route("/")
def index():
    if os.path.exists(app.static_folder + '/index.html'):
        return send_from_directory(app.static_folder, 'index.html')
    return "React Frontend not built yet. Run 'npm run build' in frontend directory."

@app.route("/api/game/state", methods=["GET"])
def get_game_state():
    return jsonify(game_manager.get_game_state())

@app.route("/api/game/move", methods=["POST"])
def move_piece():
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    
    from_x = data.get("from_x")
    from_y = data.get("from_y")
    to_x = data.get("to_x")
    to_y = data.get("to_y")
    
    if any(v is None for v in [from_x, from_y, to_x, to_y]):
        return jsonify({"success": False, "message": "Missing coordinates"}), 400
        
    result = game_manager.move_player(from_x, from_y, to_x, to_y)
    return jsonify(result)

@app.route("/api/game/reset", methods=["POST"])
def reset_game():
    game_manager.reset_game()
    return jsonify({"success": True, "state": game_manager.get_game_state()})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
