# face_recogniz — Installation et démarrage (mode dev)

Guide court pour installer et lancer l'application en développement sous Windows. Méthode recommandée : conda (Miniconda/Anaconda).

## Prérequis
- Windows (ou WSL)
- Miniconda/Anaconda (recommandé) — https://docs.conda.io/
- Git (optionnel)
- VS Code (optionnel)

## 1) Récupérer le projet
```powershell
cd /d D:\   # ou dossier souhaité
git clone <repo-url> face_recogniz
cd D:\face_recogniz
```

## 2) Créer l'environnement (conda — recommandé)
```powershell
# depuis Anaconda Prompt ou PowerShell (avec conda disponible)
conda env create -f requirements.yml
conda activate tf
```
Si l'environnement existe déjà :
```powershell
conda env update -f requirements.yml --prune
conda activate tf
```

## 3) Vérifications rapides
```powershell
python -V
python -m pip --version
python -c "import numpy as np; print('numpy', np.__version__)"
python -c "import tensorflow as tf; print('tensorflow', tf.__version__)"  # si TF installé
```

## 4) Migrer la base et lancer le serveur
```powershell
python manage.py migrate
python manage.py createsuperuser   # optionnel
python manage.py runserver
```
Accéder à http://127.0.0.1:8000

## Alternative sans TensorFlow (facenet-pytorch)
Si installation de TensorFlow problématique, utiliser facenet-pytorch :
```powershell
# venv Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

python -m pip install --upgrade pip setuptools wheel
python -m pip install Django numpy opencv-python PyMySQL
python -m pip install --index-url https://download.pytorch.org/whl/cpu torch
python -m pip install facenet-pytorch
# adapter app_face/utils.py pour facenet-pytorch (voir code du projet)
python manage.py migrate
python manage.py runserver
```

## VS Code — choisir l'interpréteur
- Ctrl+Shift+P → "Python: Select Interpreter" → choisir l'environnement `tf` (conda) ou le `venv` créé.
- Ouvrir un terminal intégré (PowerShell) et s'assurer de voir `(tf)` ou `(venv)`.

## Problèmes fréquents & solutions
- `conda` introuvable dans le terminal VSCode : exécuter `conda init powershell` dans Anaconda Prompt, redémarrer VSCode.
- Timeout lors du téléchargement de TensorFlow via pip : préférez `conda install -c conda-forge tensorflow` ou télécharger les wheels manuellement.
- Erreur NumPy (module compilé pour NumPy 1.x) : s'assurer d'utiliser numpy `< 2` (le `requirements.yml` fourni pinne `numpy==1.26.4`) :
  ```powershell
  conda activate tf
  conda install -c conda-forge "numpy<2" -y
  ```
- Modules manquants (ex. numpy, cv2, keras_facenet) : installer dans l'env actif :
  ```powershell
  python -m pip install numpy opencv-python keras-facenet
  ```
  ou utiliser conda quand possible.

## Sauvegarder l'environnement
- Conda :
```powershell
conda env export > environment.yml
```
- Pip :
```powershell
python -m pip freeze > requirements.txt
```

## Remarques
- N'activez pas simultanément un `venv` Windows et un env `conda` dans le même terminal.
- Pour stabilité sur Windows, conda (conda-forge) est recommandé pour TensorFlow et dépendances compilées.

Pour aide supplémentaire (erreurs précises, adaptation utils.py pour facenet-pytorch, ou création d'un requirements.txt), fournir la sortie d'erreur complète ou demander le fichier à générer.
