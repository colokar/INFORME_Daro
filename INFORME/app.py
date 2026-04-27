from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text
import json
import os

app = Flask(__name__)

# Configuración de la base de datos SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'fiscalizacion.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de la base de datos para registros de fiscalización
class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(10), nullable=False)
    hora = db.Column(db.String(8), nullable=False)
    regional = db.Column(db.String(50), nullable=False)
    lugar = db.Column(db.String(100), nullable=False)
    dominios = db.Column(db.Text, nullable=False)  # JSON string con lista de dominios
    transporte = db.Column(db.String(2), nullable=False)  # 'CA' o 'PA'
    items = db.Column(db.String(200), nullable=True)
    articulo = db.Column(db.String(10), nullable=True)
    retiene = db.Column(db.String(2), nullable=False)  # 'SI' o 'NO'
    incidencia = db.Column(db.String(20), nullable=True)
    lat = db.Column(db.Float, nullable=True)
    lon = db.Column(db.Float, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'fecha': self.fecha,
            'hora': self.hora,
            'regional': self.regional,
            'lugar': self.lugar,
            'dominios': json.loads(self.dominios),
            'transporte': self.transporte,
            'items': self.items,
            'articulo': self.articulo,
            'retiene': self.retiene,
            'incidencia': self.incidencia,
            'lat': self.lat,
            'lon': self.lon
        }

# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()

@app.route('/registros', methods=['GET'])
def get_registros():
    """
    Endpoint para obtener todos los registros de fiscalización.
    Devuelve una lista de registros en formato JSON.
    """
    try:
        registros = Registro.query.all()
        return jsonify([registro.to_dict() for registro in registros]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/resumen', methods=['GET'])
def get_resumen():
    """
    Endpoint para obtener un resumen general de las métricas.
    Devuelve totales de cargas, pasajeros, retenciones y actas.
    """
    try:
        # Calcular totales usando consultas SQL
        total_cargas = db.session.query(func.count(Registro.id)).filter(Registro.transporte == 'CA').scalar()
        total_pasajeros = db.session.query(func.count(Registro.id)).filter(Registro.transporte == 'PA').scalar()
        total_retenciones = db.session.query(func.count(Registro.id)).filter(Registro.retiene == 'SI').scalar()
        total_actas = db.session.query(func.count(Registro.id)).filter(Registro.articulo.isnot(None), Registro.articulo != '').scalar()

        resumen = {
            'total_cargas': total_cargas,
            'total_pasajeros': total_pasajeros,
            'total_retenciones': total_retenciones,
            'total_actas': total_actas
        }
        return jsonify(resumen), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/regiones', methods=['GET'])
def get_regiones():
    """
    Endpoint para obtener métricas agrupadas por región.
    Devuelve un diccionario con métricas por región para cargas, pasajeros y totales.
    """
    try:
        # Lista de regiones válidas
        regiones_validas = ['AMBA', 'CEN', 'NOA', 'NEA', 'CUY', 'PAT', 'COSTA']

        # Inicializar estructura de respuesta
        resultado = {}
        for region in regiones_validas:
            resultado[region] = {
                'cargas': {'vc': 0, 'actas': 0, 'ret': 0},
                'pasajeros': {'vc': 0, 'actas': 0, 'ret': 0},
                'total': {'vc': 0, 'actas': 0, 'ret': 0}
            }

        # Consultar datos agrupados por región y transporte
        query = db.session.query(
            Registro.regional,
            Registro.transporte,
            func.count(Registro.id).label('vc'),
            func.sum(db.case((Registro.articulo.isnot(None) & (Registro.articulo != ''), 1), else_=0)).label('actas'),
            func.sum(db.case((Registro.retiene == 'SI', 1), else_=0)).label('ret')
        ).group_by(Registro.regional, Registro.transporte).all()

        for regional, transporte, vc, actas, ret in query:
            if regional not in resultado:
                continue  # Solo procesar regiones válidas

            tipo = 'cargas' if transporte == 'CA' else 'pasajeros' if transporte == 'PA' else None
            if tipo:
                resultado[regional][tipo]['vc'] = vc
                resultado[regional][tipo]['actas'] = int(actas) if actas else 0
                resultado[regional][tipo]['ret'] = int(ret) if ret else 0

                # Actualizar totales
                resultado[regional]['total']['vc'] += vc
                resultado[regional]['total']['actas'] += int(actas) if actas else 0
                resultado[regional]['total']['ret'] += int(ret) if ret else 0

        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/registros', methods=['POST'])
def create_registro():
    """
    Endpoint para insertar un nuevo registro de fiscalización.
    Espera un JSON con los campos del registro.
    """
    try:
        data = request.get_json()

        # Validar campos requeridos
        required_fields = ['fecha', 'hora', 'regional', 'lugar', 'dominios', 'transporte', 'retiene']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido faltante: {field}'}), 400

        # Validar transporte
        if data['transporte'] not in ['CA', 'PA']:
            return jsonify({'error': 'transporte debe ser "CA" o "PA"'}), 400

        # Validar retiene
        if data['retiene'] not in ['SI', 'NO']:
            return jsonify({'error': 'retiene debe ser "SI" o "NO"'}), 400

        # Crear nuevo registro
        nuevo_registro = Registro(
            fecha=data['fecha'],
            hora=data['hora'],
            regional=data['regional'],
            lugar=data['lugar'],
            dominios=json.dumps(data['dominios']),
            transporte=data['transporte'],
            items=data.get('items', ''),
            articulo=data.get('articulo', ''),
            retiene=data['retiene'],
            incidencia=data.get('incidencia'),
            lat=data.get('lat'),
            lon=data.get('lon')
        )

        db.session.add(nuevo_registro)
        db.session.commit()

        return jsonify({'message': 'Registro creado exitosamente', 'id': nuevo_registro.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)