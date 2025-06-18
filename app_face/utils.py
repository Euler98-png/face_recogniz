import numpy as np
from keras_facenet import FaceNet
from mtcnn import MTCNN
import cv2

# Initialisation
embedder = FaceNet()
detector = MTCNN()

def extract_face(image):
    # Assure-toi que l’image est bien au format RGB
    if image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
    else:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    results = detector.detect_faces(image)
    if results:
        x, y, width, height = results[0]['box']
        x, y = abs(x), abs(y)
        face = image[y:y+height, x:x+width]
        face = cv2.resize(face, (160, 160))
        return face, (x, y, width, height)

    return None,None

def get_embedding(face_image):
    if face_image is None:
        return None
    # Embedding retourne une liste de dictionnaires avec une clé 'embedding'
    result = embedder.embeddings([face_image])
    print("Résultat embedder.embeddings :", result)
    print("Type :", type(result), "Shape :", getattr(result, 'shape', None))
    if isinstance(result[0], dict) and 'embedding' in result[0]:
        return result[0]['embedding']
    else:
        return result[0]

def is_match(known_embedding, candidate_embedding, threshold=0.5):
    distance = np.linalg.norm(known_embedding - candidate_embedding)
    return distance < threshold