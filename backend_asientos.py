from flask import Flask, request, jsonify
import pdfplumber
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permitir solicitudes desde el frontend

def extraer_transacciones(pdf_path):
    """Extrae texto del PDF y lo procesa para generar asientos contables"""
    asientos = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()
            if texto:
                lineas = texto.split("\n")
                for linea in lineas:
                    match = re.search(r'([\w\s]+) por \$ ([\d,]+\.\d{2})', linea)
                    if match:
                        cuenta = match.group(1).strip()
                        monto = float(match.group(2).replace(',', ''))
                        asientos.append({"Asiento": 1, "Cuenta": cuenta, "Debe": monto, "Haber": None})
    return asientos

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Archivo no válido"}), 400
    
    file_path = f"/tmp/{file.filename}"
    file.save(file_path)
    asientos = extraer_transacciones(file_path)
    
    return jsonify(asientos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
