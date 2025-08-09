from datetime import datetime
from typing import Dict, List, Optional
from src.config import get_db

class ClassSession:
    """
    Modelo para representar uma aula de jiu-jitsu
    """
    
    def __init__(self, class_id: str = None, date: datetime = None, 
                 instructor_uid: str = "", attended_students: List[str] = None):
        self.class_id = class_id or self._generate_class_id()
        self.date = date or datetime.now()
        self.instructor_uid = instructor_uid
        self.attended_students = attended_students or []
    
    def _generate_class_id(self) -> str:
        """
        Gera um ID único para a aula
        """
        return f"class_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def to_dict(self) -> Dict:
        """
        Converte o objeto ClassSession para um dicionário
        """
        return {
            'class_id': self.class_id,
            'date': self.date,
            'instructor_uid': self.instructor_uid,
            'attended_students': self.attended_students
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ClassSession':
        """
        Cria um objeto ClassSession a partir de um dicionário
        """
        return cls(
            class_id=data.get('class_id', ''),
            date=data.get('date'),
            instructor_uid=data.get('instructor_uid', ''),
            attended_students=data.get('attended_students', [])
        )
    
    def add_student(self, student_uid: str) -> bool:
        """
        Adiciona um estudante à lista de presentes
        """
        if student_uid not in self.attended_students:
            self.attended_students.append(student_uid)
            return True
        return False
    
    def remove_student(self, student_uid: str) -> bool:
        """
        Remove um estudante da lista de presentes
        """
        if student_uid in self.attended_students:
            self.attended_students.remove(student_uid)
            return True
        return False
    
    def save(self) -> bool:
        """
        Salva a aula no Firestore
        """
        try:
            db = get_db()
            class_ref = db.collection('classes').document(self.class_id)
            class_ref.set(self.to_dict(), merge=True)
            return True
        except Exception as e:
            print(f"Erro ao salvar aula: {e}")
            return False
    
    @classmethod
    def get_by_id(cls, class_id: str) -> Optional['ClassSession']:
        """
        Busca uma aula pelo ID
        """
        try:
            db = get_db()
            class_ref = db.collection('classes').document(class_id)
            doc = class_ref.get()
            
            if doc.exists:
                return cls.from_dict(doc.to_dict())
            return None
        except Exception as e:
            print(f"Erro ao buscar aula: {e}")
            return None
    
    @classmethod
    def get_by_date_range(cls, start_date: datetime, end_date: datetime) -> List['ClassSession']:
        """
        Busca aulas em um intervalo de datas
        """
        try:
            db = get_db()
            classes_ref = db.collection('classes')
            query = classes_ref.where('date', '>=', start_date).where('date', '<=', end_date)
            docs = query.stream()
            
            classes = []
            for doc in docs:
                classes.append(cls.from_dict(doc.to_dict()))
            
            return classes
        except Exception as e:
            print(f"Erro ao buscar aulas: {e}")
            return []

