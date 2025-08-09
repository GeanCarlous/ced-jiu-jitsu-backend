from datetime import datetime
from typing import Dict, List, Optional
from src.config import get_db

class Student:
    """
    Modelo para representar um estudante de jiu-jitsu
    """
    
    def __init__(self, uid: str, name: str, email: str, belt: str, age: int, 
                 address: str = "", education: str = "", degrees: int = 0):
        self.uid = uid
        self.name = name
        self.email = email
        self.belt = belt
        self.age = age
        self.address = address
        self.education = education
        self.degrees = degrees
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
            'total_presences': self.total_presences,
            'last_presence_date': self.last_presence_date,
            'history_presences': self.history_presences
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Student':
        """
        Cria um objeto Student a partir de um dicionário
        """
        student = cls(
            uid=data.get('uid', ''),
            name=data.get('name', ''),
            email=data.get('email', ''),
            belt=data.get('belt', ''),
            age=data.get('age', 0),
            address=data.get('address', ''),
            education=data.get('education', ''),
            degrees=data.get('degrees', 0)
        )
        student.total_presences = data.get('total_presences', 0)
        student.last_presence_date = data.get('last_presence_date')
        student.history_presences = data.get('history_presences', [])
        return student
    
    def calculate_presences_for_next_degree(self) -> int:
        """
        Calcula quantas presenças faltam para o próximo grau
        baseado nas regras de graduação
        """
        # Regras de graduação
        if self.age <= 6:  # KIDS (1.5 a 6 anos)
            if self.degrees == 0:
                return max(0, 10 - self.total_presences)
            elif self.degrees == 1:
                return max(0, 15 - self.total_presences)
            elif self.degrees == 2:
                return max(0, 15 - self.total_presences)
            elif self.degrees == 3:
                return max(0, 20 - self.total_presences)
            else:
                return 0  # Já pode pegar faixa cinza/branca
        
        elif self.age <= 13:  # Faixa branca e colorida até 13 anos
            presences_needed = (self.degrees + 1) * 25
            return max(0, presences_needed - self.total_presences)
        
        else:  # 14 anos ou mais
            if self.belt == 'branca':
                return max(0, 50 - self.total_presences)  # Para pegar azul
            elif self.belt in ['colorida', 'cinza', 'amarela', 'laranja', 'verde']:
                return max(0, 35 - self.total_presences)  # Para pegar azul
            else:
                # Para outras faixas, assumir 50 presenças por grau
                presences_needed = (self.degrees + 1) * 50
                return max(0, presences_needed - self.total_presences)
    
    def add_presence(self, date: datetime = None) -> bool:
        """
        Adiciona uma presença para o estudante
        """
        if date is None:
            date = datetime.now()
        
        try:
            db = get_db()
            
            # Atualizar dados do estudante
            self.total_presences += 1
            self.last_presence_date = date
            self.history_presences.append(date)
            
            # Salvar no Firestore
            student_ref = db.collection('students').document(self.uid)
            student_ref.set(self.to_dict(), merge=True)
            
            return True
        except Exception as e:
            print(f"Erro ao adicionar presença: {e}")
            return False
    
    def save(self) -> bool:
        """
        Salva o estudante no Firestore
        """
        try:
            db = get_db()
            
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
                'degrees': self.degrees
            }
            user_ref.set(user_data, merge=True)
            
            # Salvar na coleção students
            student_ref = db.collection('students').document(self.uid)
            student_ref.set(self.to_dict(), merge=True)
            
            return True
        except Exception as e:
            print(f"Erro ao salvar estudante: {e}")
            return False
    
    @classmethod
    def get_by_uid(cls, uid: str) -> Optional['Student']:
        """
        Busca um estudante pelo UID
        """
        try:
            db = get_db()
            student_ref = db.collection('students').document(uid)
            doc = student_ref.get()
            
            if doc.exists:
                return cls.from_dict(doc.to_dict())
            return None
        except Exception as e:
            print(f"Erro ao buscar estudante: {e}")
            return None
    
    @classmethod
    def get_all(cls) -> List['Student']:
        """
        Retorna todos os estudantes
        """
        try:
            db = get_db()
            students_ref = db.collection('students')
            docs = students_ref.stream()
            
            students = []
            for doc in docs:
                students.append(cls.from_dict(doc.to_dict()))
            
            return students
        except Exception as e:
            print(f"Erro ao buscar estudantes: {e}")
            return []
    
    @classmethod
    def get_students_close_to_graduation(cls, max_presences: int = 10) -> List['Student']:
        """
        Retorna estudantes que estão próximos da graduação (10 presenças ou menos)
        """
        students = cls.get_all()
        close_to_graduation = []
        
        for student in students:
            presences_needed = student.calculate_presences_for_next_degree()
            if 0 < presences_needed <= max_presences:
                close_to_graduation.append(student)
        
        return close_to_graduation

