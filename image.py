import boto3
import json
import base64
from PIL import Image
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Hardcoded AWS credentials (not recommended for production)
aws_access_key_id = ''
aws_secret_access_key = ''

def create_bedrock_client():
    """Create and return a Bedrock Runtime client."""
    return boto3.client(
        service_name="bedrock-runtime",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name='us-west-2'  # Specify the appropriate region
    )

def generate_images(text, number_of_images=2, quality='premium', height=768, width=1280, cfg_scale=7.5, seed=42):
    """
    Generates images based on the provided text description using AWS Bedrock.
    
    Parameters:
    - text (str): Description of the image to generate.
    - number_of_images (int): Number of images to generate.
    - quality (str): 'standard' or 'premium'
    - height (int): Height of the output images.
    - width (int): Width of the output images.
    - cfg_scale (float): Scale for classifier-free guidance.
    - seed (int): Seed for reproducibility.
    
    Returns:
    - list of PIL Images
    """
    client = create_bedrock_client()
    body = json.dumps({
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": text},
        "imageGenerationConfig": {
            "numberOfImages": number_of_images,
            "quality": quality,
            "height": height,
            "width": width,
            "cfgScale": cfg_scale,
            "seed": seed
        }
    })

    try:
        response = client.invoke_model(
            body=body,
            modelId="amazon.titan-image-generator-v1",
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response.get("body").read())
        images = [Image.open(BytesIO(base64.b64decode(img))) for img in response_body.get("images")]
        return images
    except Exception as e:
        logging.error("Failed to generate images: %s", e)
        return []

def save_images(images, base_filename='generated_image'):
    """Save list of images to files."""
    for index, img in enumerate(images):
        file_path = f"{base_filename}_{index + 1}.jpeg"
        img.save(file_path, 'JPEG')
        logging.info(f"Image saved to {file_path}")

if __name__ == "__main__":
    description = "Kyiv cake, roshen"
    images = generate_images(description)
    if images:
        save_images(images)
    else:
        logging.info("No images to display.")