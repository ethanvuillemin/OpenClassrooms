from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import io
import logging
import os

os.environ["SM_FRAMEWORK"] = "tf.keras"

# Importer nos fonctions utilitaires
from utils import load_segmentation_model, preprocess_image, postprocess_prediction

# Configuration du logging
logging.basicConfig(level=logging.INFO)

# Création de l'application FastAPI
app = FastAPI(
    title="Future Vision Transport - API de Segmentation",
    description="Une API pour prédire les masques de segmentation d'images de conduite.",
    version="1.0.0"
)


@app.on_event("startup")
def startup_event():
    logging.info("Démarrage de l'application et chargement du modèle...")
    app.state.model = load_segmentation_model()
    logging.info("Modèle chargé et prêt à recevoir des requêtes.")



@app.get("/", tags=["General"])
def read_root():
    """Endpoint racine pour vérifier si l'API est en ligne."""
    return {"message": "Bienvenue sur l'API de segmentation de Future Vision Transport"}

@app.post("/predict", tags=["Segmentation"])
async def predict(file: UploadFile = File(...)):
    """
    Prend une image en entrée et retourne le masque de segmentation prédit.
    
    - **Input**: Une image (format PNG, JPG, etc.).
    - **Output**: Un JSON contenant le masque prédit sous forme de liste 2D d'entiers.
    """
    logging.info(f"Requête de prédiction reçue pour le fichier : {file.filename}")

    # Vérifier que le fichier est bien une image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier envoyé n'est pas une image.")

    try:
        # Lire le contenu du fichier uploadé
        contents = await file.read()
        
        # Ouvrir l'image avec Pillow
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # 1. Prétraiter l'image
        input_tensor = preprocess_image(image)
        
        # 2. Faire la prédiction avec le modèle chargé
        prediction = app.state.model.predict(input_tensor)
        
        # 3. Post-traiter la prédiction pour obtenir le masque final
        predicted_mask = postprocess_prediction(prediction)
        
        logging.info(f"Prédiction réussie pour le fichier : {file.filename}")
        
        # Renvoyer le masque au format JSON
        return JSONResponse(content={"predicted_mask": predicted_mask})

    except Exception as e:
        logging.error(f"Erreur lors de la prédiction : {e}")
        raise HTTPException(status_code=500, detail=f"Une erreur interne est survenue : {e}")