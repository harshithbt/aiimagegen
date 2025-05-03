from flask import Flask, jsonify, request, send_file
from PIL import Image
from io import BytesIO
import requests

app = Flask(__name__)

POST_API_URL = "https://apiimagestrax.vercel.app/api/genimage"

@app.route('/aigenimage', methods=['GET'])
def expose_get():
    try:
        print(request.args.get('prompt'))
        POST_PAYLOAD = {
            "prompt": request.args.get('prompt'),
        }
        response = requests.post(POST_API_URL, json=POST_PAYLOAD)
        response.raise_for_status()  # raises error for bad status codes
        img = Image.open(BytesIO(response.content))
        compressed_img = img.resize((350, 350))
        output = BytesIO()
        compressed_img.save(output, format='PNG', optimize=True)
        output.seek(0)
        return send_file(output, mimetype='image/png', as_attachment=False)
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)