from flask import Flask, request, jsonify
import pdfplumber
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def extraer_transacciones(pdf_path, asiento_numero):
    """Extrae texto del PDF y genera asientos contables"""
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
                        
                        # Lógica para asignar cuentas contables
                        if "luz" in cuenta.lower():
                            asientos.append({"Asiento": asiento_numero, "Cuenta": "Gastos de Energía", "Debe": monto, "Haber": None})
                            asientos.append({"Asiento": asiento_numero, "Cuenta": "Bancos", "Debe": None, "Haber": monto})
                        elif "nómina" in cuenta.lower():
                            asientos.append({"Asiento": asiento_numero, "Cuenta": "Sueldos y Salarios", "Debe": monto, "Haber": None})
                            asientos.append({"Asiento": asiento_numero, "Cuenta": "Bancos", "Debe": None, "Haber": monto})
                        else:
                            asientos.append({"Asiento": asiento_numero, "Cuenta": cuenta, "Debe": monto, "Haber": None})
    return asientos

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Archivo no válido"}), 400
    
    asiento_numero = int(request.form.get("asiento_numero", 1))
    file_path = f"/tmp/{file.filename}"
    file.save(file_path)
    
    asientos = extraer_transacciones(file_path, asiento_numero)
    return jsonify(asientos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
