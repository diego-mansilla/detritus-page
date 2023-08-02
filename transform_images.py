import os
import tensorflow as tf
from tensorflow.keras.preprocessing import image_dataset_from_directory
import numpy as np
from PIL import Image

# Load the dataset
def load_dataset(data_dir, image_size=(160, 160), batch_size=32):
    return image_dataset_from_directory(
        data_dir,
        image_size=image_size,
        batch_size=batch_size,
        labels=None,
        shuffle=False  # Important to keep file names in order
    )

# Save images from dataset to the new directory
def save_images_from_dataset(dataset, target_dir, original_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Get a sorted list of image files from the directory
    image_files = sorted([f for _, _, files in os.walk(original_dir) for f in files if f.endswith(('.jpg', '.png'))])

    i = 0
    for batch in dataset:
        for img in batch:
            # Convert tensor image to PIL Image
            img = Image.fromarray((img.numpy()).astype(np.uint8))
            img.save(os.path.join(target_dir, image_files[i]))
            i += 1

if __name__ == "__main__":
    # Define paths
    source_dir = 'app/static/images'  # Example: '/path/to/images'
    new_dir = 'app/static/images_resized'  # Example: '/path/to/new_images'

    dataset = load_dataset(source_dir)

    save_images_from_dataset(dataset, new_dir, source_dir)
