from flask import Flask, request, send_file, jsonify
import boto3
import json
import base64
from PIL import Image
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

def create_bedrock_client():
    # Configure your AWS credentials and client here
    aws_access_key_id = 'YOUR_AWS_ACCESS_KEY_ID'
    aws_secret_access_key = 'YOUR_AWS_SECRET_ACCESS_KEY'
    return boto3.client(
        service_name="bedrock-runtime",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name='us-west-2'
    )

@app.route('/generate-image', methods=['POST'])
def generate_images():
    content = request.json
    text = content.get('text', 'Default text if none provided')
    number_of_images = content.get('numberOfImages', 1)
    quality = content.get('quality', 'premium')
    height = content.get('height', 768)
    width = content.get('width', 1280)
    cfg_scale = content.get('cfgScale', 7.5)
    seed = content.get('seed', 42)

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
        for index, img in enumerate(images):
            img_filename = f"generated_image_{index + 1}.jpeg"
            img.save(img_filename, 'JPEG')
        return jsonify({'message': 'Images generated successfully', 'filenames': [f"generated_image_{i + 1}.jpeg" for i in range(len(images))]})
    except Exception as e:
        logging.error("Failed to generate images: %s", e)
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)