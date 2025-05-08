from flask import Flask, jsonify, request, send_file
from PIL import Image
from io import BytesIO
import requests

app = Flask(__name__)

POST_API_URL = "https://apiimagestrax.vercel.app/api/genimage"

@app.route('/aigenimage', methods=['GET'])
def expose_get():
    try:
        POST_PAYLOAD = {
            "prompt": request.args.get('prompt') or 'enter prompt text',
        }
        response = requests.post(POST_API_URL, json=POST_PAYLOAD)
        response.raise_for_status()
        width = request.args.get('width') or 488
        if width is None:
            width = 488
        else:
            width = int(width)
        height = request.args.get('height') or 488
        if height is None:
            height = 488
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

if __name__ == '__main__':
    app.run(debug=True)
