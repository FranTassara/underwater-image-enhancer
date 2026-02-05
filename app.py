"""
Servidor Flask para la aplicación de mejoramiento de imágenes subacuáticas.
"""

import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from enhance import enhance_waternet, enhance_opencv

app = Flask(__name__)

# Configuración
UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tiff", "webp"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    # Validar que se envió un archivo
    if "file" not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No se seleccionó ningún archivo"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Formato no soportado. Usá JPG, PNG, BMP, TIFF o WebP"}), 400

    # Obtener método de mejoramiento
    method = request.form.get("method", "opencv")

    # Generar nombres únicos para evitar colisiones
    file_id = uuid.uuid4().hex[:8]
    ext = file.filename.rsplit(".", 1)[1].lower()
    original_name = f"{file_id}_original.{ext}"
    enhanced_name = f"{file_id}_enhanced.{ext}"

    original_path = os.path.join(UPLOAD_FOLDER, original_name)
    enhanced_path = os.path.join(UPLOAD_FOLDER, enhanced_name)

    # Guardar archivo original
    file.save(original_path)

    # Procesar imagen
    if method == "waternet":
        result = enhance_waternet(original_path, enhanced_path)
    else:
        result = enhance_opencv(original_path, enhanced_path)

    if result is None:
        # Limpiar archivo original si falló el procesamiento
        if os.path.exists(original_path):
            os.remove(original_path)
        return jsonify({"error": "Error al procesar la imagen. Probá con otro archivo."}), 500

    return jsonify({
        "original": f"/static/uploads/{original_name}",
        "enhanced": f"/static/uploads/{enhanced_name}",
        "method": method,
    })


if __name__ == "__main__":
    print("=== Underwater Image Enhancer ===")
    print("Abrí http://localhost:5000 en tu navegador")
    print("Presioná Ctrl+C para detener el servidor")
    app.run(debug=True, port=5000)
