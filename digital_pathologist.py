# digital_pathologist.py
# FINAL CORRECTED VERSION: This version has the exact list of 39 classes
# from your trained model, which will fix the loading error.

import logging
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import os

# --- Model Configuration ---
MODEL_PATH = "crop_disease_model.pth"
# --- FIX: The number of classes is 39 ---
NUM_CLASSES = 39 

# --- FIX: Using the exact list of 39 class names from your dataset ---
CLASS_NAMES = [
    'Apple___Apple_scab',
    'Apple___Black_rot',
    'Apple___Cedar_apple_rust',
    'Apple___healthy',
    'Background_without_leaves',
    'Blueberry___healthy',
    'Cherry___Powdery_mildew',
    'Cherry___healthy',
    'Corn___Cercospora_leaf_spot Gray_leaf_spot',
    'Corn___Common_rust',
    'Corn___Northern_Leaf_Blight',
    'Corn___healthy',
    'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)',
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)',
    'Peach___Bacterial_spot',
    'Peach___healthy',
    'Pepper,_bell___Bacterial_spot',
    'Pepper,_bell___healthy',
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch',
    'Strawberry___healthy',
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy',
]
# --- END OF FIX ---


# --- Model Loading ---
model = None
if not os.path.exists(MODEL_PATH):
    logging.error(f"Model file not found at {MODEL_PATH}. The disease diagnosis agent will not work.")
else:
    try:
        model = models.resnet50(weights=None)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, NUM_CLASSES)
        model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
        model.eval()
        logging.info(f"Successfully loaded trained model from {MODEL_PATH}")
    except Exception as e:
        logging.error(f"Failed to load model. This is likely due to a mismatch in NUM_CLASSES. Error: {e}")
        model = None

# --- Image Transformations (Unchanged) ---
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def predict_image(image_bytes):
    if model is None:
        raise RuntimeError("Model is not loaded. Cannot perform prediction.")
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    image_tensor = transform(image).unsqueeze(0) 
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted_idx = torch.max(probabilities, 1)
    predicted_class = CLASS_NAMES[predicted_idx.item()]
    confidence_score = confidence.item()
    return predicted_class, confidence_score


def diagnose_crop_health(image_file_name: str, image_bytes: bytes):
    logging.info(f"Digital Pathologist received image: {image_file_name} for real diagnosis.")
    if model is None:
        return {"status": "error", "message": "The disease diagnosis model is not available. Please check the server logs."}
    try:
        predicted_class, confidence = predict_image(image_bytes)
        
        # Improved logic to handle special class names like 'Background_without_leaves'
        parts = predicted_class.split('___')
        if len(parts) > 1:
            crop = parts[0].replace('_', ' ')
            disease = parts[1].replace('_', ' ')
        else:
            crop = "N/A"
            disease = predicted_class.replace('_', ' ')

        return {
            "status": "success",
            "data": {
                "crop": crop,
                "disease_name": disease,
                "confidence_score": confidence,
                "recommendation": f"Diagnosis complete. The model is {confidence*100:.2f}% confident that the issue is {disease}. Please consult a local agricultural expert to confirm and for treatment options."
            }
        }
    except Exception as e:
        logging.error(f"An error occurred during real diagnosis: {e}")
        return {"status": "error", "message": "An unexpected error occurred during image analysis."}
