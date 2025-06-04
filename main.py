from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from together import Together
from PIL import Image
from io import BytesIO
from supabase import create_client, Client
import base64
import requests

app = Flask(__name__)
CORS(app)

FREE_API_URL = "https://apiimagestrax.vercel.app/api/genimage"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/"

SUPABASE_URL = "https://ckwjyqhmyqydxjswvers.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNrd2p5cWhteXF5ZHhqc3d2ZXJzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkwMTExNDMsImV4cCI6MjA2NDU4NzE0M30.fAtUgnqk3JLddYOWV0B_lk3C9s8NB3PW9sitAYF-DO8"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/freeapi', methods=['GET'])
def expose_get_free():
    try:
        POST_PAYLOAD = {
            "prompt": request.args.get('prompt'),
        }
        sresponse = supabase.table("aimpressoption").select("apiUrl").eq("value", "free").limit(1).execute()
        if sresponse.data and sresponse.data[0].get("apiLink"):
            url_value = sresponse.data[0]["apiLink"]
        else:
            url_value = FREE_API_URL
        response = requests.post(url_value, json=POST_PAYLOAD)
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
        }
    ]
    try:
        response = supabase.table("aimpressoption").select("*").execute()
        data = response.data
        if not data:
            return jsonify(modelOption), 200
        return jsonify(data), 200
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
        sresponse = supabase.table("aimpressoption").select("apiUrl").eq("value", "gemini").limit(1).execute()
        if sresponse.data and sresponse.data[0].get("apiLink"):
            url_value = sresponse.data[0]["apiLink"]
        else:
            url_value = GEMINI_API_URL
        FINAL_URL = url_value+model+':predict?key='+apiKey
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
