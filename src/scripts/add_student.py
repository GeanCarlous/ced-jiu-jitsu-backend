from src.config import get_db

db = get_db()
# Substitua pelo UID real do aluno cadastrado no Firebase Auth
uid = "gpI7cq2U3JRSREIUFU6iCuM0iGA3"
db.collection("students").document(uid).set({
    "uid": uid,
    "name": "Gean Carlos",
    "email": "cgean3385@gmail.com",
    "belt": "branca",
    "age": 21,
    # Adicione outros campos se necessário
})
