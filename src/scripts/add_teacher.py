from src.config import get_db

db = get_db()
# Substitua pelo UID real do professor cadastrado no Firebase Auth
uid = "yRJbS1nVC7TevLI61ehxaVeTcDR2"
db.collection("teachers").document(uid).set({
    "uid": uid,
    "name": "Jonatas Lopes",
    "email": "Jonataslopesnene@gmail.com"
})
