from flask import Blueprint, request, jsonify
from firebase_admin import auth
from src.models.student import Student
from src.models.teacher import Teacher
from src.middleware.auth import require_auth, require_teacher

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """
    Verifica o token de autenticação do Firebase
    """
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({'error': 'Token não fornecido'}), 400
        
        # Verificar o token com o Firebase
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        
        # Buscar o usuário no Firestore para determinar o papel
        student = Student.get_by_uid(uid)
        teacher = Teacher.get_by_uid(uid)
        
        if student:
            user_data = {
                'uid': uid,
                'email': email,
                'role': 'aluno',
                'name': student.name,
                'belt': student.belt,
                'age': student.age,
                'total_presences': student.total_presences,
                'presences_for_next_degree': student.calculate_presences_for_next_degree()
            }
        elif teacher:
            user_data = {
                'uid': uid,
                'email': email,
                'role': 'professor',
                'name': teacher.name
            }
        else:
            # Usuário não encontrado no sistema
            return jsonify({'error': 'Usuário não encontrado no sistema'}), 404
        
        return jsonify({
            'success': True,
            'user': user_data
        }), 200
        
    except auth.InvalidIdTokenError:
        return jsonify({'error': 'Token inválido'}), 401
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/register-student', methods=['POST'])
@require_auth
@require_teacher
def register_student():
    """
    Permite que um professor cadastre um novo estudante no sistema
    """
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['name', 'email', 'belt', 'age']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        # Gerar UID único para o aluno
        import uuid
        uid = str(uuid.uuid4())
        
        # Criar novo estudante
        student = Student(
            uid=uid,
            name=data['name'],
            email=data['email'],
            belt=data['belt'],
            age=int(data['age']),
            address=data.get('address', ''),
            education=data.get('education', ''),
            degrees=int(data.get('degrees', 0))
        )
        
        # Salvar no Firestore
        if student.save():
            return jsonify({
                'success': True,
                'message': 'Estudante registrado com sucesso',
                'student': student.to_dict()
            }), 201
        else:
            return jsonify({'error': 'Erro ao salvar estudante'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/register-teacher', methods=['POST'])
def register_teacher():
    """
    Registra um novo professor no sistema
    """
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['uid', 'name', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        # Criar novo professor
        teacher = Teacher(
            uid=data['uid'],
            name=data['name'],
            email=data['email']
        )
        
        # Salvar no Firestore
        if teacher.save():
            return jsonify({
                'success': True,
                'message': 'Professor registrado com sucesso',
                'teacher': teacher.to_dict()
            }), 201
        else:
            return jsonify({'error': 'Erro ao salvar professor'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

