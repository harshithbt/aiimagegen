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
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/"

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
            "name": "Free",
            "value": "free",
            "key": False,
            "apiPath": "freeapi",
        },
        {
            "name": "Together AI",
            "value": "together",
            "key": True,
            "apiPath": "togetherapi",
            "apiKeyStr": "genaiTogetherKey",
            "modelStr": "genaiTogetherModel",
            "defaultModel": "black-forest-labs/FLUX.1-schnell-Free",
            "refLink": "https://api.together.ai/"
        },
        {
            "name": "Google(Gemini)",
            "value": "gemini",
            "key": True,
            "apiPath": "geminiapi",
            "apiKeyStr": "genaiGeminiKey",
            "modelStr": "genaiGeminiModel",
            "defaultModel": "imagen-3.0-generate-002",
            "refLink": "https://console.cloud.google.com/"
        }
    ]
    return jsonify(modelOption)

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
    
@app.route('/geminiapi', methods=['GET'])
def expose_get_gemini():
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
        GEMINI_PAYLOAD = {
            "prompt": request.args.get('prompt'),
        }
        headers = {
            'Content-Type': 'application/json'
        }
        FINAL_URL = GEMINI_API_URL+model+':predict?key='+apiKey
        response = requests.post(FINAL_URL, json=GEMINI_PAYLOAD, headers=headers)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
        compressed_img = img.resize((width, height))
        output = BytesIO()
        compressed_img.save(output, format='PNG', quality=30, optimize=True)
        output.seek(0)
        return send_file(output, mimetype='image/png', as_attachment=False)
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
