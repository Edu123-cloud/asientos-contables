import pdfplumber
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def extraer_datos_contables(pdf_path):
    """Extrae datos contables de un archivo PDF."""

    datos =

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()
            if texto:
                lineas = texto.split("\n")
                for linea in lineas:
                    # 1. Saldos iniciales
                    if "Saldos iniciales" in linea:
                        indice_linea = lineas.index(linea) + 1
                        if indice_linea < len(lineas):
                            datos_saldos = lineas[indice_linea].split("\n")
                            for saldo in datos_saldos:
                                match = re.search(r'(\w+) \$ ([\d,]+\.\d{2})', saldo)
                                if match:
                                    cuenta = match.group(1).strip()
                                    monto = float(match.group(2).replace(",", ""))
                                    datos.append({
                                        "tipo": "saldo_inicial",
                                        "cuenta": cuenta,
                                        "monto": monto,
                                        "movimiento": "Debe"  # Asumimos que los saldos iniciales son Debe
                                    })

                    # 2. Pago de luz
                    if "Se paga el recibo de luz" in linea:
                        match = re.search(r'por \$ ([\d,]+\.\d{2})', linea)
                        if match:
                            monto_base = float(match.group(1).replace(",", ""))
                            iva = monto_base * 0.16
                            monto_total = monto_base + iva
                            distribucion =
                            # Extraer distribución (esto es más complejo y puede necesitar ajustes)
                            try:
                                indice_distribucion = lineas.index(linea) + 1
                                while indice_distribucion < len(lineas) and any(kw in lineas[indice_distribucion] for kw in ["oficinas", "ventas", "publicidad", "producción"]):
                                    match_distribucion = re.search(r'(\d+) kw del área de (\w+)', lineas[indice_distribucion])
                                    if match_distribucion:
                                        kw = int(match_distribucion.group(1))
                                        area = match_distribucion.group(2)
                                        distribucion.append({"area": area, "kw": kw})
                                    indice_distribucion += 1
                            except ValueError:
                                pass  # Manejar el error si no se encuentra la línea siguiente

                            datos.append({
                                "tipo": "pago",
                                "concepto": "Recibo de luz",
                                "monto_base": monto_base,
                                "iva": iva,
                                "monto_total": monto_total,
                                "distribucion": distribucion
                            })

                    # 3. Compra de maquinaria
                    if "compra de maquinaria" in linea:
                        match = re.search(r'por \$ ([\d,]+\.\d{2})', linea)
                        if match:
                            monto_base = float(match.group(1).replace(",", ""))
                            iva_match = re.search(r'más IVA', linea)
                            iva = monto_base * 0.16 if iva_match else 0
                            datos.append({
                                "tipo": "compra",
                                "concepto": "Maquinaria",
                                "monto_base": monto_base,
                                "iva": iva
                            })

                    # ... (Agregar lógica para otras transacciones: ventas, compras, etc.) ...

    return datos

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Archivo no válido"}), 400

    file_path = f"/tmp/{file.filename}"
    file.save(file_path)
    datos = extraer_datos_contables(file_path)

    return jsonify(datos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
