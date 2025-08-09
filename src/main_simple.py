from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Dados mock para demonstração
mock_students = [
    {
        'uid': 'student1',
        'name': 'João Silva',
        'email': 'joao@email.com',
        'belt': 'azul',
        'age': 25,
        'total_presences': 45,
        'degrees': 2,
        'presences_for_next_degree': 5
    },
    {
        'uid': 'student2',
        'name': 'Maria Santos',
        'email': 'maria@email.com',
        'belt': 'roxa',
        'age': 28,
        'total_presences': 120,
        'degrees': 1,
        'presences_for_next_degree': 8
    }
]

mock_teacher = {
    'uid': 'teacher1',
    'name': 'Professor Carlos',
    'email': 'carlos@cedjj.com'
}

# Rotas da API
@app.route('/api/auth/verify-token', methods=['POST'])
def verify_token():
    """Mock da verificação de token"""
    data = request.get_json()
    email = data.get('email', 'demo@cedjj.com')
    
    if 'professor' in email or 'teacher' in email:
        return jsonify({
            'success': True,
            'user': {
                'uid': 'teacher1',
                'email': email,
                'role': 'professor',
                'name': 'Professor Carlos'
            }
        })
    else:
        return jsonify({
            'success': True,
            'user': {
                'uid': 'student1',
                'email': email,
                'role': 'aluno',
                'name': 'João Silva',
                'belt': 'azul',
                'age': 25,
                'total_presences': 45,
                'presences_for_next_degree': 5
            }
        })

@app.route('/api/students/', methods=['GET'])
def get_students():
    """Retorna lista de estudantes"""
    return jsonify({
        'success': True,
        'students': mock_students
    })

@app.route('/api/students/<uid>', methods=['GET'])
def get_student(uid):
    """Retorna dados de um estudante"""
    student = next((s for s in mock_students if s['uid'] == uid), None)
    if student:
        return jsonify({
            'success': True,
            'student': student
        })
    return jsonify({'error': 'Estudante não encontrado'}), 404

@app.route('/api/students/close-to-graduation', methods=['GET'])
def get_students_close_to_graduation():
    """Retorna estudantes próximos da graduação"""
    close_students = [s for s in mock_students if s['presences_for_next_degree'] <= 10]
    return jsonify({
        'success': True,
        'students': close_students,
        'count': len(close_students)
    })

@app.route('/api/students/', methods=['POST'])
def create_student():
    """Cria novo estudante"""
    data = request.get_json()
    new_student = {
        'uid': f"student{len(mock_students) + 1}",
        'name': data['name'],
        'email': data['email'],
        'belt': data['belt'],
        'age': int(data['age']),
        'total_presences': 0,
        'degrees': int(data.get('degrees', 0)),
        'presences_for_next_degree': 25  # Default para faixa branca
    }
    mock_students.append(new_student)
    
    return jsonify({
        'success': True,
        'message': 'Estudante criado com sucesso',
        'student': new_student
    }), 201

@app.route('/api/attendance/mark', methods=['POST'])
def mark_attendance():
    """Marca presença"""
    data = request.get_json()
    student_uids = data.get('student_uids', [])
    
    updated_students = []
    for uid in student_uids:
        for student in mock_students:
            if student['uid'] == uid:
                student['total_presences'] += 1
                if student['presences_for_next_degree'] > 0:
                    student['presences_for_next_degree'] -= 1
                updated_students.append(student)
    
    return jsonify({
        'success': True,
        'message': f'Presença marcada para {len(updated_students)} estudante(s)',
        'updated_students': updated_students
    })

@app.route('/api/attendance/history/<uid>', methods=['GET'])
def get_attendance_history(uid):
    """Retorna histórico de presenças"""
    student = next((s for s in mock_students if s['uid'] == uid), None)
    if not student:
        return jsonify({'error': 'Estudante não encontrado'}), 404
    
    # Mock de histórico
    history = ['2025-08-01', '2025-08-03', '2025-08-05']
    
    return jsonify({
        'success': True,
        'student_uid': uid,
        'student_name': student['name'],
        'total_presences': student['total_presences'],
        'presences_for_next_degree': student['presences_for_next_degree'],
        'history': history,
        'has_more': False
    })

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

