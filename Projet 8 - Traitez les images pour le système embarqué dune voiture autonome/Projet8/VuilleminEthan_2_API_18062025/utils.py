import tensorflow as tf
import segmentation_models as sm
import numpy as np
from PIL import Image



FINAL_MODEL_BACKBONE = "efficientnetb0" 
MODEL_PATH = "model/final_best_model.keras"
IMG_HEIGHT = 288
IMG_WIDTH = 528

def load_segmentation_model():
    """
    Charge le modèle de segmentation en mémoire.
    Gère les objets personnalisés nécessaires pour la perte et les métriques.
    """
    # On ne compile pas le modèle pour l'inférence, c'est plus rapide.
    # On doit quand même fournir les objets personnalisés pour que Keras puisse charger le modèle.
    def combined_dice_focal_loss(y_true, y_pred):
        dice_loss = sm.losses.DiceLoss()(y_true, y_pred)
        focal_loss = sm.losses.CategoricalFocalLoss()(y_true, y_pred)
        return dice_loss + (1 * focal_loss)

    custom_objects = {
        'combined_dice_focal_loss': combined_dice_focal_loss,
        'iou_score': sm.metrics.IOUScore(),
        'f1-score': sm.metrics.FScore()
    }
    model = tf.keras.models.load_model(MODEL_PATH, custom_objects=custom_objects, compile=False)
    print(f"Modèle chargé depuis {MODEL_PATH}")
    return model


def preprocess_image(image: Image.Image):
    """
    Prétraite une image PIL pour l'inférence du modèle.
    1. Redimensionne l'image.
    2. Applique le pré-traitement spécifique au backbone.
    3. Ajoute une dimension de batch.
    """
    # Redimensionner l'image
    image = image.resize((IMG_WIDTH, IMG_HEIGHT))
    image_np = np.array(image)

    # Obtenir la fonction de pré-traitement du backbone
    preprocess_input = sm.get_preprocessing(FINAL_MODEL_BACKBONE)
    
    # Appliquer le pré-traitement
    preprocessed_image = preprocess_input(image_np)
    
    # Ajouter la dimension du batch
    input_tensor = np.expand_dims(preprocessed_image, axis=0)
    
    return input_tensor


def postprocess_prediction(prediction_tensor):
    """
    Convertit la sortie brute du modèle (tensor) en un masque 2D.
    """
    # Appliquer argmax pour obtenir les ID de classe pour chaque pixel
    mask = np.argmax(prediction_tensor[0], axis=-1)
    
    # Convertir en liste pour la sérialisation JSON
    return mask.tolist()