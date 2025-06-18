import numpy as np
from keras_facenet import FaceNet
# Charger le modèle FaceNet
model = FaceNet()

def get_embedding(face_pixels):
    face_pixels = face_pixels.astype('float32')
    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels - mean) / std

    results = model.extract(face_pixels, threshold=0.95)

    if results and len(results) > 0:
        # retourner le premier embedding détecté (128 dims)
        embedding = results[0]['embedding']
        return np.array(embedding)
    else:
        return None