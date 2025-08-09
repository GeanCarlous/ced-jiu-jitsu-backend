from flask import Blueprint, request, jsonify
from src.models.student import Student
from src.middleware.auth import require_auth, require_teacher
from firebase_admin import auth

students_bp = Blueprint('students', __name__)

@students_bp.route('/', methods=['GET'])
@require_auth
@require_teacher
def get_all_students():
    """
    Retorna todos os estudantes (apenas para professores)
    """
    try:
        students = Student.get_all()
        students_data = []
        
        for student in students:
            student_dict = student.to_dict()
            student_dict['presences_for_next_degree'] = student.calculate_presences_for_next_degree()
            students_data.append(student_dict)
        
        return jsonify({
            'success': True,
            'students': students_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@students_bp.route('/<uid>', methods=['GET'])
@require_auth
def get_student(uid):
    """
    Retorna dados de um estudante específico
    """
    try:
        # Verificar se o usuário pode acessar estes dados
        current_user = request.current_user
        if current_user['role'] != 'professor' and current_user['uid'] != uid:
            return jsonify({'error': 'Acesso negado'}), 403
        
        student = Student.get_by_uid(uid)
        if not student:
            return jsonify({'error': 'Estudante não encontrado'}), 404
        
        student_dict = student.to_dict()
        student_dict['presences_for_next_degree'] = student.calculate_presences_for_next_degree()
        
        return jsonify({
            'success': True,
            'student': student_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@students_bp.route('/', methods=['POST'])
@require_auth
@require_teacher
def create_student():
    """
    Cria um novo estudante (apenas para professores)
    """
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['name', 'email', 'belt', 'age']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400

        # Criar usuário no Firebase Auth
        try:
            user_record = auth.create_user(
                email=data['email'],
                password=data.get('password', 'aluno123'),  # senha padrão, pode ser alterada depois
                display_name=data['name']
            )
            uid = user_record.uid
        except auth.EmailAlreadyExistsError:
            return jsonify({'error': 'Email já cadastrado no Auth'}), 400
        except Exception as e:
            return jsonify({'error': f'Erro ao criar usuário no Auth: {str(e)}'}), 500

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
            student_dict = student.to_dict()
            student_dict['presences_for_next_degree'] = student.calculate_presences_for_next_degree()
            
            return jsonify({
                'success': True,
                'message': 'Estudante criado com sucesso',
                'student': student_dict
            }), 201
        else:
            return jsonify({'error': 'Erro ao salvar estudante'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@students_bp.route('/<uid>', methods=['PUT'])
@require_auth
@require_teacher
def update_student(uid):
    """
    Atualiza dados de um estudante (apenas para professores)
    """
    try:
        data = request.get_json()
        
        # Buscar estudante existente
        student = Student.get_by_uid(uid)
        if not student:
            return jsonify({'error': 'Estudante não encontrado'}), 404
        
        # Atualizar campos fornecidos
        if 'name' in data:
            student.name = data['name']
        if 'belt' in data:
            student.belt = data['belt']
        if 'age' in data:
            student.age = int(data['age'])
        if 'address' in data:
            student.address = data['address']
        if 'education' in data:
            student.education = data['education']
        if 'degrees' in data:
            student.degrees = int(data['degrees'])
        
        # Salvar alterações
        if student.save():
            student_dict = student.to_dict()
            student_dict['presences_for_next_degree'] = student.calculate_presences_for_next_degree()
            
            return jsonify({
                'success': True,
                'message': 'Estudante atualizado com sucesso',
                'student': student_dict
            }), 200
        else:
            return jsonify({'error': 'Erro ao atualizar estudante'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@students_bp.route('/close-to-graduation', methods=['GET'])
@require_auth
@require_teacher
def get_students_close_to_graduation():
    """
    Retorna estudantes próximos da graduação (10 presenças ou menos)
    """
    try:
        max_presences = request.args.get('max_presences', 10, type=int)
        students = Student.get_students_close_to_graduation(max_presences)
        
        students_data = []
        for student in students:
            student_dict = student.to_dict()
            student_dict['presences_for_next_degree'] = student.calculate_presences_for_next_degree()
            students_data.append(student_dict)
        
        return jsonify({
            'success': True,
            'students': students_data,
            'count': len(students_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

