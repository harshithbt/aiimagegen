from flask import Flask, jsonify, request, send_file
from together import Together
from PIL import Image
from io import BytesIO
import base64
import requests

app = Flask(__name__)

POST_API_URL = "https://apiimagestrax.vercel.app/api/genimage"

@app.route('/aigenimage', methods=['GET'])
def expose_get_aigenimage():
    try:
        POST_PAYLOAD = {
            "prompt": request.args.get('prompt'),
        }
        response = requests.post(POST_API_URL, json=POST_PAYLOAD)
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
        img = Image.open(BytesIO(response.content))
        compressed_img = img.resize((width, height))
        output = BytesIO()
        compressed_img.save(output, format='PNG', optimize=True)
        output.seek(0)
        return send_file(output, mimetype='image/png', as_attachment=False)
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/apistatus', methods=['GET'])
def expose_get_test():
    return jsonify({"message": "alive"})

@app.route('/aimpress', methods=['GET'])
def expose_get_impress():
    try:
        prompt = request.args.get('prompt')
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
        client = Together(api_key="651ec5eabc61f4b01645e86900f5f22abcd1b45ad100488f983d599b80998290")
        response = client.images.generate(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-schnell-Free",
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
