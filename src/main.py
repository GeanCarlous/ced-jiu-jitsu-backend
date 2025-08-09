from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Importe os blueprints reais
from src.routes.students import students_bp
from src.routes.attendance import attendance_bp
from src.routes.auth import auth_bp
# Adicione outros blueprints se necessário

# Registre os blueprints com prefixo /api
app.register_blueprint(students_bp, url_prefix='/api/students')
app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
# app.register_blueprint(...)

# Servir arquivos estáticos do React
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    static_folder = os.path.join(app.root_path, 'static')
    if path != "" and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    else:
        index_path = os.path.join(static_folder, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder, 'index.html')
        else:
            return "Sistema CED Jiu-Jitsu - Em desenvolvimento", 200

from src.config import get_db
from flask import jsonify

@app.route('/api/firebase-test')
def firebase_test():
    try:
        db = get_db()
        # Tenta buscar um documento de teste
        test_ref = db.collection('test').document('connection')
        test_ref.set({'ok': True}, merge=True)
        doc = test_ref.get()
        return jsonify({'success': True, 'data': doc.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

