import logging
from datetime import datetime
from typing import Dict, List, Optional
from src.config import get_db

# Configurar logging
logger = logging.getLogger(__name__)

class Student:
    """
    Modelo para representar um estudante de jiu-jitsu
    """
    
    def __init__(self, uid: str, name: str, email: str, belt: str, age: int, 
                 address: str = "", education: str = "", degrees: int = 0, 
                 start_date: str = None, photo_url: str = "", extra_activities: int = 0):
        self.uid = uid
        self.name = name
        self.email = email
        self.belt = belt
        self.age = age
        self.address = address
        self.education = education
        self.degrees = degrees
        self.start_date = start_date or datetime.now().strftime("%Y-%m-%d")
        self.photo_url = photo_url
        self.extra_activities = extra_activities  # Número de atividades extras feitas
        self.total_presences = 0
        self.last_presence_date = None
        self.history_presences = []
    
    def to_dict(self) -> Dict:
        """
        Converte o objeto Student para um dicionário
        """
        return {
            'uid': self.uid,
            'name': self.name,
            'email': self.email,
            'belt': self.belt,
            'age': self.age,
            'address': self.address,
            'education': self.education,
            'degrees': self.degrees,
            'start_date': self.start_date,
            'photo_url': self.photo_url,
            'extra_activities': self.extra_activities,
            'total_presences': self.total_presences,
            'last_presence_date': self.last_presence_date,
            'history_presences': self.history_presences,
            'presences_for_next_degree': self.calculate_presences_for_next_degree(),
            'next_belt': self.get_next_belt()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Student':
        """
        Cria um objeto Student a partir de um dicionário
        """
        if not data:
            logger.warning("Dados vazios fornecidos para from_dict")
            return None
            
        try:
            student = cls(
                uid=data.get('uid', ''),
                name=data.get('name', ''),
                email=data.get('email', ''),
                belt=data.get('belt', ''),
                age=data.get('age', 0),
                address=data.get('address', ''),
                education=data.get('education', ''),
                degrees=data.get('degrees', 0),
                start_date=data.get('start_date'),
                photo_url=data.get('photo_url', ''),
                extra_activities=data.get('extra_activities', 0)
            )
            student.total_presences = data.get('total_presences', 0)
            student.last_presence_date = data.get('last_presence_date')
            student.history_presences = data.get('history_presences', [])
            return student
        except Exception as e:
            logger.error(f"Erro ao criar Student a partir de dados: {e}")
            return None
    
    def get_belt_requirements(self) -> Dict:
        """
        Retorna os requisitos de presenças para cada faixa baseado nas regras de negócio
        """
        requirements = {
            'branca': {'normal': 50, 'with_activity': 45},
            'azul': {'normal': 90, 'with_activity': 85},
            'roxa': {'normal': 70, 'with_activity': 65},
            'marrom': {'normal': 80, 'with_activity': 70},
            'preta': {'type': 'time_based'}  # Faixa preta é baseada em tempo
        }
        return requirements.get(self.belt, {'normal': 50, 'with_activity': 45})
    
    def get_next_belt(self) -> str:
        """
        Retorna a próxima faixa baseada na faixa atual
        """
        belt_progression = {
            'branca': 'azul',
            'azul': 'roxa',
            'roxa': 'marrom',
            'marrom': 'preta',
            'preta': 'preta'  # Faixa preta não muda
        }
        return belt_progression.get(self.belt, 'azul')
    
    def calculate_presences_for_next_degree(self) -> int:
        """
        Calcula quantas presenças faltam para o próximo grau
        baseado nas novas regras de graduação com atividades extras
        """
        try:
            # Para faixa preta, usar regras de tempo
            if self.belt == 'preta':
                return 0  # Faixa preta é baseada em tempo, não presenças
            
            # Obter requisitos da faixa atual
            requirements = self.get_belt_requirements()
            
            # Calcular presenças necessárias para o próximo grau
            if self.extra_activities > self.degrees:
                # Aluno fez atividade extra para este grau
                presences_needed = requirements['with_activity']
            else:
                # Aluno não fez atividade extra para este grau
                presences_needed = requirements['normal']
            
            # Calcular presenças acumuladas necessárias até o grau atual
            total_presences_needed = 0
            for degree in range(self.degrees + 1):
                if self.extra_activities > degree:
                    total_presences_needed += requirements['with_activity']
                else:
                    total_presences_needed += requirements['normal']
            
            # Retornar quantas presenças faltam
            return max(0, total_presences_needed - self.total_presences)
            
        except Exception as e:
            logger.error(f"Erro ao calcular presenças para próximo grau: {e}")
            return 0
    
    def is_ready_for_next_belt(self) -> bool:
        """
        Verifica se o aluno está pronto para a próxima faixa (completou 4 graus)
        """
        return self.degrees >= 4 and self.calculate_presences_for_next_degree() == 0
    
    def can_graduate_with_activity(self) -> bool:
        """
        Verifica se o aluno pode se graduar fazendo uma atividade extra
        """
        if self.belt == 'preta':
            return False  # Faixa preta não usa atividades extras
        
        requirements = self.get_belt_requirements()
        
        # Calcular presenças necessárias se fizer atividade extra
        total_with_activity = 0
        for degree in range(self.degrees + 1):
            if degree <= self.extra_activities:  # Já fez atividade para este grau
                total_with_activity += requirements['with_activity']
            else:  # Faria atividade para este grau
                total_with_activity += requirements['with_activity']
        
        # Calcular presenças necessárias sem atividade extra
        total_without_activity = requirements['normal'] * (self.degrees + 1)
        
        # Pode se graduar com atividade se tem presenças suficientes para o caminho com atividade
        # mas não tem para o caminho sem atividade
        return (self.total_presences >= total_with_activity and 
                self.total_presences < total_without_activity)
    
    def add_extra_activity(self) -> bool:
        """
        Adiciona uma atividade extra para o estudante
        """
        try:
            self.extra_activities += 1
            return self.save()
        except Exception as e:
            logger.error(f"Erro ao adicionar atividade extra para {self.uid}: {e}")
            return False
    
    def add_presence(self, date: datetime = None) -> bool:
        """
        Adiciona uma presença para o estudante
        """
        if date is None:
            date = datetime.now()
        
        try:
            db = get_db()
            if db is None:
                logger.error("Falha ao conectar com o banco de dados")
                return False
            
            # Atualizar dados do estudante
            self.total_presences += 1
            self.last_presence_date = date.isoformat() if isinstance(date, datetime) else date
            self.history_presences.append(date.isoformat() if isinstance(date, datetime) else date)
            
            # Verificar se pode avançar de grau
            if self.calculate_presences_for_next_degree() == 0 and self.degrees < 4:
                self.degrees += 1
                logger.info(f"Estudante {self.uid} avançou para o grau {self.degrees}")
            
            # Salvar no Firestore
            student_ref = db.collection('students').document(self.uid)
            student_ref.set(self.to_dict(), merge=True)
            
            logger.info(f"Presença adicionada para estudante {self.uid}")
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar presença para {self.uid}: {e}")
            return False
    
    def save(self) -> bool:
        """
        Salva o estudante no Firestore
        """
        try:
            db = get_db()
            if db is None:
                logger.error("Falha ao conectar com o banco de dados")
                return False
            
            # Salvar na coleção users
            user_ref = db.collection('users').document(self.uid)
            user_data = {
                'uid': self.uid,
                'email': self.email,
                'role': 'aluno',
                'name': self.name,
                'belt': self.belt,
                'age': self.age,
                'address': self.address,
                'education': self.education,
                'degrees': self.degrees,
                'start_date': self.start_date,
                'photo_url': self.photo_url,
                'extra_activities': self.extra_activities
            }
            user_ref.set(user_data, merge=True)
            
            # Salvar na coleção students
            student_ref = db.collection('students').document(self.uid)
            student_ref.set(self.to_dict(), merge=True)
            
            logger.info(f"Estudante {self.uid} salvo com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar estudante {self.uid}: {e}")
            return False
    
    @classmethod
    def get_by_uid(cls, uid: str) -> Optional["Student"]:
        """
        Busca um estudante pelo UID
        """
        if not uid:
            logger.warning("UID vazio fornecido para get_by_uid")
            return None
            
        try:
            db = get_db()
            if db is None:
                logger.error("Falha ao conectar com o banco de dados")
                return None
                
            logger.debug(f"Buscando estudante com UID: {uid}")
            
            # Primeiro, tentar buscar na coleção 'students'
            student_data_ref = db.collection("students").document(uid)
            student_data_doc = student_data_ref.get()
            
            if student_data_doc.exists:
                logger.debug("Dados completos do aluno encontrados na coleção 'students'")
                return cls.from_dict(student_data_doc.to_dict())
            else:
                logger.warning(f"Dados completos do aluno {uid} não encontrados na coleção 'students'. Tentando coleção 'users'.")
                # Se não encontrar em 'students', tentar buscar na coleção 'users'
                user_ref = db.collection("users").document(uid)
                user_doc = user_ref.get()
                
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    if user_data.get("role") == "aluno":
                        logger.debug(f"Aluno encontrado na coleção 'users', criando entrada na coleção 'students'.")
                        # Criar dados básicos na coleção students se não existir
                        basic_student_data = {
                            'uid': uid,
                            'name': user_data.get('name', ''),
                            'email': user_data.get('email', ''),
                            'belt': user_data.get('belt', 'branca'),
                            'age': user_data.get('age', 0),
                            'address': user_data.get('address', ''),
                            'education': user_data.get('education', ''),
                            'degrees': user_data.get('degrees', 0),
                            'start_date': user_data.get('start_date', datetime.now().strftime("%Y-%m-%d")),
                            'photo_url': user_data.get('photo_url', ''),
                            'extra_activities': user_data.get('extra_activities', 0),
                            'total_presences': 0,
                            'last_presence_date': None,
                            'history_presences': []
                        }
                        student_data_ref.set(basic_student_data)
                        return cls.from_dict(basic_student_data)
                    else:
                        logger.debug(f"Usuário {uid} na coleção 'users' não é um aluno (role: {user_data.get('role')}).")
                else:
                    logger.debug(f"Documento para UID {uid} NÃO encontrado em nenhuma coleção.")
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar estudante com UID {uid}: {e}")
            return None
    
    @classmethod
    def get_all(cls) -> List['Student']:
        """
        Retorna todos os estudantes
        """
        try:
            db = get_db()
            if db is None:
                logger.error("Falha ao conectar com o banco de dados")
                return []
                
            students_ref = db.collection('students')
            docs = students_ref.stream()
            
            students = []
            for doc in docs:
                student = cls.from_dict(doc.to_dict())
                if student:
                    students.append(student)
            
            logger.info(f"Encontrados {len(students)} estudantes")
            return students
        except Exception as e:
            logger.error(f"Erro ao buscar estudantes: {e}")
            return []
    
    @classmethod
    def get_students_close_to_graduation(cls, max_presences: int = 10) -> List['Student']:
        """
        Retorna estudantes que estão próximos da graduação (10 presenças ou menos)
        """
        try:
            students = cls.get_all()
            close_to_graduation = []
            
            for student in students:
                presences_needed = student.calculate_presences_for_next_degree()
                if 0 < presences_needed <= max_presences:
                    close_to_graduation.append(student)
            
            logger.info(f"Encontrados {len(close_to_graduation)} estudantes próximos da graduação")
            return close_to_graduation
        except Exception as e:
            logger.error(f"Erro ao buscar estudantes próximos da graduação: {e}")
            return []

