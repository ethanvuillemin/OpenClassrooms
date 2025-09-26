import requests
import numpy as np
from PIL import Image
import io
from skimage.transform import resize

def call_api_and_overlay_mask(image):
    # Convertir l'image en bytes pour l'envoyer via l'API
    img_pil = Image.fromarray(image)
    img_byte_arr = io.BytesIO()
    img_pil.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # Appeler l'API
    url = "http://cityhand.fr:8000/predict"
    headers = {
        'accept': 'application/json',
    }
    files = {'file': ('image.png', img_byte_arr, 'image/png')}
    response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        # Récupérer le masque prédit
        predicted_mask = response.json()["predicted_mask"]

        # Convertir le masque en un tableau numpy
        mask_array = np.array(predicted_mask)

        # Redimensionner le masque pour qu'il corresponde aux dimensions de l'image
        mask_array_resized = resize(mask_array, (image.shape[0], image.shape[1]), order=0, preserve_range=True, anti_aliasing=False)

        # Convertir le masque redimensionné en un tableau d'entiers
        mask_array_resized = mask_array_resized.astype(int)

        # Définir les couleurs pour chaque classe
        class_colors = {
            0: (0, 0, 0),      # Void: Noir
            1: (128, 0, 128),  # Flat: Violet
            2: (128, 128, 128),# Construction: Gris
            3: (0, 255, 0),    # Object: Vert
            4: (0, 128, 0),    # Nature: Vert foncé
            5: (0, 0, 255),    # Sky: Bleu
            6: (255, 0, 0),    # Human: Rouge
            7: (0, 255, 255)   # Vehicle: Cyan
        }

        # Créer une nouvelle image avec opacité pour le masque
        overlayed_image = image.copy().astype(float)

        for class_id, color in class_colors.items():
            # Appliquer l'opacité de 0.65
            overlay_color = np.array(color) * 0.55
            overlayed_image[mask_array_resized == class_id] = overlay_color

        # Convertir le tableau numpy en une image PIL
        overlayed_image_pil = Image.fromarray(overlayed_image.astype('uint8'))

        return overlayed_image_pil
    else:
        raise Exception(f"Error calling API: {response.status_code}")
