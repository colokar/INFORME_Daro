import json
import os
from app import app, db, Registro

def populate_db():
    """
    Script para poblar la base de datos con datos de datos.json
    """
    # Cargar datos desde datos.json
    datos_path = os.path.join(os.path.dirname(__file__), 'INFORME', 'datos.json')
    with open(datos_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    registros = data.get('registros', [])

    with app.app_context():
        # Limpiar tabla existente
        db.session.query(Registro).delete()
        db.session.commit()

        # Insertar registros
        for reg in registros:
            nuevo_registro = Registro(
                fecha=reg.get('fecha', ''),
                hora=reg.get('hora', ''),
                regional=reg.get('regional', ''),
                lugar=reg.get('lugar', ''),
                dominios=json.dumps(reg.get('dominios', [])),
                transporte=reg.get('transporte', ''),
                items=reg.get('items', ''),
                articulo=reg.get('articulo', ''),
                retiene=reg.get('retiene', ''),
                incidencia=reg.get('incidencia'),
                lat=reg.get('lat'),
                lon=reg.get('lon')
            )
            db.session.add(nuevo_registro)

        db.session.commit()
        print(f"Se insertaron {len(registros)} registros en la base de datos.")

if __name__ == '__main__':
    populate_db()