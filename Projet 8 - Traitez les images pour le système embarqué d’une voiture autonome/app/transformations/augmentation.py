import cv2
import numpy as np
import albumentations as A

def apply_augmentation(image, augmentation_type):
    # Convertir l'image en RGB si nécessaire
    if isinstance(image, np.ndarray):
        image = image.astype(np.uint8)
    else:
        image = np.array(image).astype(np.uint8)

    transform = None

    if augmentation_type == "Horizontal Flip":
        transform = A.HorizontalFlip(p=1.0)
    elif augmentation_type == "Vertical Flip":
        transform = A.VerticalFlip(p=1.0)
    elif augmentation_type == "Random Brightness":
        transform = A.RandomBrightness(limit=0.2, p=1.0)
    elif augmentation_type == "Rotation":
        transform = A.Rotate(limit=45, p=1.0)
    elif augmentation_type == "Zoom":
        transform = A.RandomScale(scale_limit=0.2, p=1.0)
    elif augmentation_type == "Gaussian Noise":
        transform = A.GaussNoise(var_limit=(10.0, 50.0), p=1.0)
    
    if transform:
        augmented = transform(image=image)['image']
        return augmented
    else:
        return image