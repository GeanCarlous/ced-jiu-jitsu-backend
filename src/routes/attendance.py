from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models.student import Student
from src.models.class_session import ClassSession
from src.middleware.auth import require_auth, require_teacher

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/mark', methods=['POST'])
@require_auth
@require_teacher
def mark_attendance():
    """
    Marca presença para um ou mais estudantes (apenas para professores)
    """
    try:
        data = request.get_json()
        current_user = request.current_user
        
        # Validar dados obrigatórios
        if 'student_uids' not in data:
            return jsonify({'error': 'Lista de estudantes é obrigatória'}), 400
        
        student_uids = data['student_uids']
        if not isinstance(student_uids, list) or len(student_uids) == 0:
            return jsonify({'error': 'Lista de estudantes deve conter pelo menos um UID'}), 400
        
        # Data da aula (opcional, padrão é agora)
        class_date = data.get('date')
        if class_date:
            class_date = datetime.fromisoformat(class_date.replace('Z', '+00:00'))
        else:
            class_date = datetime.now()
        
        # Criar sessão de aula
        class_session = ClassSession(
            date=class_date,
            instructor_uid=current_user['uid'],
            attended_students=student_uids
        )
        
        # Salvar a aula
        if not class_session.save():
            return jsonify({'error': 'Erro ao salvar aula'}), 500
        
        # Marcar presença para cada estudante
        updated_students = []
        errors = []
        
        for student_uid in student_uids:
            student = Student.get_by_uid(student_uid)
            if student:
                if student.add_presence(class_date):
                    student_dict = student.to_dict()
                    student_dict['presences_for_next_degree'] = student.calculate_presences_for_next_degree()
                    updated_students.append(student_dict)
                else:
                    errors.append(f'Erro ao marcar presença para {student.name}')
            else:
                errors.append(f'Estudante com UID {student_uid} não encontrado')
        
        response_data = {
            'success': True,
            'message': f'Presença marcada para {len(updated_students)} estudante(s)',
            'class_id': class_session.class_id,
            'updated_students': updated_students
        }
        
        if errors:
            response_data['errors'] = errors
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@attendance_bp.route('/history/<uid>', methods=['GET'])
@require_auth
def get_attendance_history(uid):
    """
    Retorna o histórico de presenças de um estudante
    """
    try:
        # Verificar se o usuário pode acessar estes dados
        current_user = request.current_user
        if current_user['role'] != 'professor' and current_user['uid'] != uid:
            return jsonify({'error': 'Acesso negado'}), 403
        
        student = Student.get_by_uid(uid)
        if not student:
            return jsonify({'error': 'Estudante não encontrado'}), 404
        
        # Parâmetros de paginação
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Obter histórico de presenças
        history = student.history_presences[offset:offset + limit]
        
        return jsonify({
            'success': True,
            'student_uid': uid,
            'student_name': student.name,
            'total_presences': student.total_presences,
            'presences_for_next_degree': student.calculate_presences_for_next_degree(),
            'history': [date.isoformat() if hasattr(date, 'isoformat') else str(date) for date in history],
            'has_more': len(student.history_presences) > offset + limit
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@attendance_bp.route('/class/<class_id>', methods=['GET'])
@require_auth
@require_teacher
def get_class_attendance(class_id):
    """
    Retorna informações de uma aula específica (apenas para professores)
    """
    try:
        class_session = ClassSession.get_by_id(class_id)
        if not class_session:
            return jsonify({'error': 'Aula não encontrada'}), 404
        
        # Obter informações dos estudantes presentes
        students_data = []
        for student_uid in class_session.attended_students:
            student = Student.get_by_uid(student_uid)
            if student:
                students_data.append({
                    'uid': student.uid,
                    'name': student.name,
                    'belt': student.belt,
                    'total_presences': student.total_presences
                })
        
        return jsonify({
            'success': True,
            'class': {
                'class_id': class_session.class_id,
                'date': class_session.date.isoformat(),
                'instructor_uid': class_session.instructor_uid,
                'attended_students_count': len(class_session.attended_students),
                'attended_students': students_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@attendance_bp.route('/classes', methods=['GET'])
@require_auth
@require_teacher
def get_classes():
    """
    Retorna lista de aulas em um período (apenas para professores)
    """
    try:
        # Parâmetros de data
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if not start_date_str or not end_date_str:
            return jsonify({'error': 'Datas de início e fim são obrigatórias'}), 400
        
        start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        
        classes = ClassSession.get_by_date_range(start_date, end_date)
        
        classes_data = []
        for class_session in classes:
            classes_data.append({
                'class_id': class_session.class_id,
                'date': class_session.date.isoformat(),
                'instructor_uid': class_session.instructor_uid,
                'attended_students_count': len(class_session.attended_students)
            })
        
        return jsonify({
            'success': True,
            'classes': classes_data,
            'count': len(classes_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

