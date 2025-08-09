from functools import wraps
from flask import request, jsonify
from firebase_admin import auth
from src.models.student import Student
from src.models.teacher import Teacher

def require_auth(f):
    """
    Decorator que requer autenticação válida
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token não fornecido'}), 401
        token = auth_header.split(' ')[1]
        try:
            decoded_token = auth.verify_id_token(token)
            request.user = decoded_token
        except Exception:
            return jsonify({'error': 'Token inválido'}), 401

        uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        
        # Buscar o usuário no sistema
        student = Student.get_by_uid(uid)
        teacher = Teacher.get_by_uid(uid)
        
        if student:
            user_data = {
                'uid': uid,
                'email': email,
                'role': 'aluno',
                'name': student.name
            }
        elif teacher:
            user_data = {
                'uid': uid,
                'email': email,
                'role': 'professor',
                'name': teacher.name
            }
        else:
            return jsonify({'error': 'Usuário não encontrado no sistema'}), 404
        
        # Adicionar dados do usuário à requisição
        request.current_user = user_data
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_teacher(f):
    """
    Decorator que requer que o usuário seja um professor
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = getattr(request, 'user', None)
        if not user or user.get('role') != 'professor':
            return jsonify({'error': 'Acesso restrito a professores'}), 403
        return f(*args, **kwargs)
    
    return decorated_function

def require_student(f):
    """
    Decorator que requer que o usuário seja um aluno
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user') or request.current_user['role'] != 'aluno':
            return jsonify({'error': 'Acesso restrito a alunos'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function