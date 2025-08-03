# train_model.py
# This is the latest version of the script to train the crop disease model
# using a local NVIDIA GPU. It is configured to work with your manually downloaded dataset.

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, models, transforms
import os
from tqdm import tqdm
import time

# --- 1. Configuration ---
# The script will look for a folder with this name in your project directory.
DATASET_DIR = "PlantVillage"
MODEL_SAVE_PATH = "crop_disease_model.pth"

# Hyperparameters
BATCH_SIZE = 32
NUM_EPOCHS = 10
LEARNING_RATE = 0.001

# --- 2. Setup Device ---
if not torch.cuda.is_available():
    print("!!! WARNING: CUDA is not available, training will be very slow. !!!")
    print("Please check your NVIDIA driver, CUDA Toolkit, and cuDNN installation.")
    device = torch.device("cpu")
else:
    device = torch.device("cuda:0")
print(f"Using device: {device}")


# --- 3. Prepare Data Loaders ---
# This section assumes the 'PlantVillage' directory exists.
if not os.path.exists(DATASET_DIR):
    print(f"!!! ERROR: Dataset directory '{DATASET_DIR}' not found. !!!")
    print("Please make sure you have downloaded, unzipped, and placed the dataset folder in your project directory.")
    exit() # Stop the script if the data isn't there

data_transforms = {
    'train': transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'val': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
}

# --- IMPORTANT CHANGE FOR YOUR DATASET ---
# We point directly to the DATASET_DIR because your version doesn't have a 'train' subfolder.
full_dataset = datasets.ImageFolder(DATASET_DIR)
# --- END OF CHANGE ---

# Split the dataset into training and validation sets (80% train, 20% val)
train_size = int(0.8 * len(full_dataset))
val_size = len(full_dataset) - train_size
train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

# Apply the respective transforms to the split datasets
train_dataset.dataset.transform = data_transforms['train']
val_dataset.dataset.transform = data_transforms['val']

# Create data loaders to feed the data to the model in batches
dataloaders = {
    'train': DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4),
    'val': DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=4)
}

class_names = full_dataset.classes
num_classes = len(class_names)
print(f"Found {num_classes} classes. Example: {class_names[0]}")


# --- 4. Define and Configure the Model ---
model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
# Freeze all the pre-trained layers
for param in model.parameters():
    param.requires_grad = False
# Replace the final layer for our specific number of classes
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, num_classes)
model = model.to(device) # Move the model to the GPU
# Define the loss function and the optimizer (which only updates the new final layer)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.fc.parameters(), lr=LEARNING_RATE)


# --- 5. Training Loop ---
def train_model():
    """The main function to train the model."""
    start_time = time.time()
    print("\n--- Starting Model Training ---")
    for epoch in range(NUM_EPOCHS):
        print(f'\nEpoch {epoch+1}/{NUM_EPOCHS}')
        print('-' * 10)

        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()  # Set model to training mode
            else:
                model.eval()   # Set model to evaluate mode

            running_loss = 0.0
            running_corrects = 0

            # Iterate over data.
            for inputs, labels in tqdm(dataloaders[phase], desc=f"{phase.capitalize()} Phase"):
                inputs = inputs.to(device)
                labels = labels.to(device)
                optimizer.zero_grad()
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / len(dataloaders[phase].dataset)
            epoch_acc = running_corrects.double() / len(dataloaders[phase].dataset)
            print(f'--> {phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')

    time_elapsed = time.time() - start_time
    print(f'\nTraining complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')
    
    # Save the trained model
    torch.save(model.state_dict(), MODEL_SAVE_PATH)
    print(f"Model saved to {MODEL_SAVE_PATH}")

# This block ensures the training only runs when the script is executed directly
if __name__ == '__main__':
    train_model()
