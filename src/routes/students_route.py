from flask import Blueprint, request, jsonify
from src.models.student import Student
from src.middleware.auth import require_auth, require_teacher
import logging

# Configurar logging
logger = logging.getLogger(__name__)

students_bp = Blueprint('students', __name__)

@students_bp.route('/update-profile', methods=['PUT'])
@require_auth
def update_profile():
    """
    Permite que um aluno atualize suas informações pessoais
    """
    try:
        data = request.get_json()
        user_uid = request.user_uid  # Vem do middleware de autenticação
        
        # Buscar o aluno atual
        student = Student.get_by_uid(user_uid)
        if not student:
            return jsonify({'error': 'Aluno não encontrado'}), 404
        
        # Atualizar apenas os campos permitidos
        if 'name' in data:
            student.name = data['name']
        if 'address' in data:
            student.address = data['address']
        if 'education' in data:
            student.education = data['education']
        if 'photo_url' in data:
            student.photo_url = data['photo_url']
        
        # Salvar as alterações
        if student.save():
            return jsonify({
                'success': True,
                'message': 'Perfil atualizado com sucesso',
                'student': student.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Erro ao salvar alterações'}), 500
            
    except Exception as e:
        logger.error(f"Erro ao atualizar perfil: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@students_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """
    Retorna as informações do perfil do aluno logado
    """
    try:
        user_uid = request.user_uid  # Vem do middleware de autenticação
        
        # Buscar o aluno
        student = Student.get_by_uid(user_uid)
        if not student:
            return jsonify({'error': 'Aluno não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'student': student.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar perfil: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@students_bp.route('/', methods=['GET'])
@require_teacher
def get_all_students():
    """
    Retorna todos os estudantes (apenas para professores)
    """
    try:
        students = Student.get_all()
        students_data = [student.to_dict() for student in students]
        
        return jsonify({
            'success': True,
            'students': students_data
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar estudantes: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@students_bp.route('/close-to-graduation', methods=['GET'])
@require_teacher
def get_students_close_to_graduation():
    """
    Retorna estudantes próximos da graduação (apenas para professores)
    """
    try:
        students = Student.get_students_close_to_graduation()
        students_data = [student.to_dict() for student in students]
        
        return jsonify({
            'success': True,
            'students': students_data
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar estudantes próximos da graduação: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@students_bp.route('/', methods=['POST'])
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
        
        # Criar novo estudante
        student = Student(
            uid=data.get('uid', ''),  # UID será gerado pelo Firebase Auth
            name=data['name'],
            email=data['email'],
            belt=data['belt'],
            age=int(data['age']),
            address=data.get('address', ''),
            education=data.get('education', ''),
            degrees=int(data.get('degrees', 0)),
            start_date=data.get('start_date'),
            photo_url=data.get('photo_url', ''),
            extra_activities=int(data.get('extra_activities', 0))
        )
        
        # Salvar estudante
        if student.save():
            return jsonify({
                'success': True,
                'message': 'Estudante criado com sucesso',
                'student': student.to_dict()
            }), 201
        else:
            return jsonify({'error': 'Erro ao salvar estudante'}), 500
            
    except Exception as e:
        logger.error(f"Erro ao criar estudante: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@students_bp.route('/<student_uid>', methods=['PUT'])
@require_teacher
def update_student(student_uid):
    """
    Atualiza um estudante (apenas para professores)
    """
    try:
        data = request.get_json()
        
        # Buscar estudante
        student = Student.get_by_uid(student_uid)
        if not student:
            return jsonify({'error': 'Estudante não encontrado'}), 404
        
        # Atualizar campos
        if 'name' in data:
            student.name = data['name']
        if 'email' in data:
            student.email = data['email']
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
        if 'start_date' in data:
            student.start_date = data['start_date']
        if 'photo_url' in data:
            student.photo_url = data['photo_url']
        if 'extra_activities' in data:
            student.extra_activities = int(data['extra_activities'])
        
        # Salvar alterações
        if student.save():
            return jsonify({
                'success': True,
                'message': 'Estudante atualizado com sucesso',
                'student': student.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Erro ao salvar alterações'}), 500
            
    except Exception as e:
        logger.error(f"Erro ao atualizar estudante: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@students_bp.route('/<student_uid>/extra-activity', methods=['POST'])
@require_teacher
def add_extra_activity(student_uid):
    """
    Adiciona uma atividade extra para um estudante (apenas para professores)
    """
    try:
        # Buscar estudante
        student = Student.get_by_uid(student_uid)
        if not student:
            return jsonify({'error': 'Estudante não encontrado'}), 404
        
        # Verificar se o aluno pode fazer atividade extra
        if student.belt == 'preta':
            return jsonify({'error': 'Faixa preta não utiliza atividades extras'}), 400
        
        # Adicionar atividade extra
        if student.add_extra_activity():
            return jsonify({
                'success': True,
                'message': 'Atividade extra adicionada com sucesso',
                'student': student.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Erro ao adicionar atividade extra'}), 500
            
    except Exception as e:
        logger.error(f"Erro ao adicionar atividade extra: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@students_bp.route('/<student_uid>/remove-extra-activity', methods=['POST'])
@require_teacher
def remove_extra_activity(student_uid):
    """
    Remove uma atividade extra de um estudante (apenas para professores)
    """
    try:
        # Buscar estudante
        student = Student.get_by_uid(student_uid)
        if not student:
            return jsonify({'error': 'Estudante não encontrado'}), 404
        
        # Verificar se tem atividades para remover
        if student.extra_activities <= 0:
            return jsonify({'error': 'Estudante não possui atividades extras para remover'}), 400
        
        # Remover atividade extra
        student.extra_activities -= 1
        
        if student.save():
            return jsonify({
                'success': True,
                'message': 'Atividade extra removida com sucesso',
                'student': student.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Erro ao remover atividade extra'}), 500
            
    except Exception as e:
        logger.error(f"Erro ao remover atividade extra: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@students_bp.route('/attendance', methods=['POST'])
@require_teacher
def mark_attendance():
    """
    Marca presença para múltiplos estudantes (apenas para professores)
    """
    try:
        data = request.get_json()
        
        if 'student_uids' not in data:
            return jsonify({'error': 'Lista de UIDs de estudantes é obrigatória'}), 400
        
        student_uids = data['student_uids']
        date = data.get('date')  # Data opcional
        
        updated_students = []
        errors = []
        
        for uid in student_uids:
            try:
                student = Student.get_by_uid(uid)
                if student:
                    if student.add_presence(date):
                        updated_students.append(student.to_dict())
                    else:
                        errors.append(f"Erro ao marcar presença para {uid}")
                else:
                    errors.append(f"Estudante {uid} não encontrado")
            except Exception as e:
                errors.append(f"Erro ao processar {uid}: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': f'Presença marcada para {len(updated_students)} estudante(s)',
            'updated_students': updated_students,
            'errors': errors
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao marcar presença: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@students_bp.route('/<student_uid>/attendance-history', methods=['GET'])
@require_auth
def get_attendance_history(student_uid):
    """
    Retorna o histórico de presenças de um estudante
    """
    try:
        # Verificar se é o próprio aluno ou um professor
        user_uid = request.user_uid
        user_role = getattr(request, 'user_role', None)
        
        if user_role != 'professor' and user_uid != student_uid:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Buscar estudante
        student = Student.get_by_uid(student_uid)
        if not student:
            return jsonify({'error': 'Estudante não encontrado'}), 404
        
        # Limitar histórico se especificado
        limit = request.args.get('limit', type=int)
        history = student.history_presences
        
        if limit and limit > 0:
            history = history[-limit:]  # Pegar os últimos N registros
        
        return jsonify({
            'success': True,
            'history': history,
            'total_presences': student.total_presences
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de presenças: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@students_bp.route('/<student_uid>', methods=['GET'])
@require_auth
def get_student(student_uid):
    """
    Retorna informações de um estudante específico
    """
    try:
        # Verificar se é o próprio aluno ou um professor
        user_uid = request.user_uid
        user_role = getattr(request, 'user_role', None)
        
        if user_role != 'professor' and user_uid != student_uid:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Buscar estudante
        student = Student.get_by_uid(student_uid)
        if not student:
            return jsonify({'error': 'Estudante não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'student': student.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar estudante: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

