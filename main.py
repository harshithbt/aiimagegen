from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from together import Together
from PIL import Image
from io import BytesIO
import base64
import requests

app = Flask(__name__)
CORS(app)

FREE_API_URL = "https://apiimagestrax.vercel.app/api/genimage"

@app.route('/freeapi', methods=['GET'])
def expose_get_free():
    try:
        POST_PAYLOAD = {
            "prompt": request.args.get('prompt'),
        }
        response = requests.post(FREE_API_URL, json=POST_PAYLOAD)
        response.raise_for_status()
        width = request.args.get('width') or 480
        if width is None:
            width = 480
        else:
            width = int(width)
        height = request.args.get('height') or 480
        if height is None:
            height = 480
        else:
            height = int(height)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        compressed_img = img.resize((width, height))
        output = BytesIO()
        compressed_img.save(output, format='PNG', quality=30, optimize=True)
        output.seek(0)
        return send_file(output, mimetype='image/png', as_attachment=False)
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/apistatus', methods=['GET'])
def expose_get_test():
    return jsonify({"message": "alive"})

@app.route('/aioption', methods=['GET'])
def expose_get_aioption():
    modelOption = [
        {
            "apiKeyStr": null,
            "apiPath": "freeapi",
            "apiUrl": "https://apiimagestrax.vercel.app/api/genimage",
            "defaultModel": null,
            "key": false,
            "modelStr": null,
            "name": "Free",
            "refLink": null,
            "value": "free"
        },
        {
            "apiKeyStr": "aimpressTogetherKey",
            "apiPath": "togetherapi",
            "apiUrl": null,
            "defaultModel": "black-forest-labs/FLUX.1-schnell-Free",
            "key": true,
            "modelStr": "aimpressTogetherModel",
            "name": "Together AI",
            "refLink": "https://api.together.ai/",
            "value": "together"
        }
    ]
    try:
        return jsonify(modelOption), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/togetherapi', methods=['GET'])
def expose_get_together():
    try:
        prompt = request.args.get('prompt')
        apiKey = request.args.get('apiKey')
        model = request.args.get('model')
        width = request.args.get('width') or 480
        if width is None:
            width = 480
        else:
            width = int(width)
        height = request.args.get('height') or 480
        if height is None:
            height = 480
        else:
            height = int(height)
        client = Together(api_key=apiKey)
        response = client.images.generate(
            prompt=prompt,
            model=model,
            width=width,
            height=height,
            steps=2,
            n=1,
            seed=10000,
            response_format="b64_json",
            stop=[]
        )
        image_data = base64.b64decode(response.data[0].b64_json)
        if not image_data:
            return jsonify({"error": "No image data found"}), 500
        return send_file(
            BytesIO(image_data),
            mimetype='image/png',
            as_attachment=False
        )
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
