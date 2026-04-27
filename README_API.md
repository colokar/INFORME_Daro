# API REST de Fiscalización CNRT

Esta API REST reemplaza el uso de `datos.json` y proporciona una interfaz backend para el sistema de informes de fiscalización de CNRT.

## Tecnologías

- **Flask**: Framework web para Python
- **SQLAlchemy**: ORM para la base de datos
- **SQLite**: Base de datos (fácil migración a MongoDB)

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Poblar la base de datos con datos existentes:
```bash
python populate_db.py
```

3. Ejecutar la API:
```bash
python app.py
```

La API estará disponible en `http://127.0.0.1:5000`

## Endpoints

### GET /registros
Devuelve todos los registros de fiscalización.

**Respuesta:**
```json
[
  {
    "id": 1,
    "fecha": "2026-04-06",
    "hora": "00:00:00",
    "regional": "CEN",
    "lugar": "ETO SF",
    "dominios": ["AA202BV"],
    "transporte": "PA",
    "items": "",
    "articulo": "",
    "retiene": "NO",
    "incidencia": null,
    "lat": -31.643333,
    "lon": -60.7
  }
]
```

### GET /resumen
Devuelve métricas generales del sistema.

**Respuesta:**
```json
{
  "total_cargas": 9741,
  "total_pasajeros": 8626,
  "total_retenciones": 56,
  "total_actas": 93
}
```

### GET /regiones
Devuelve métricas agrupadas por región.

**Respuesta:**
```json
{
  "AMBA": {
    "cargas": {
      "vc": 2745,
      "actas": 13,
      "ret": 7
    },
    "pasajeros": {
      "vc": 3182,
      "actas": 2,
      "ret": 8
    },
    "total": {
      "vc": 5927,
      "actas": 15,
      "ret": 15
    }
  }
}
```

### POST /registros
Inserta un nuevo registro de fiscalización.

**Cuerpo de la petición:**
```json
{
  "fecha": "2024-04-20",
  "hora": "10:00:00",
  "regional": "AMBA",
  "lugar": "Test Location",
  "dominios": ["ABC123"],
  "transporte": "CA",
  "retiene": "NO",
  "items": "",
  "articulo": "",
  "incidencia": null,
  "lat": null,
  "lon": null
}
```

**Campos requeridos:** `fecha`, `hora`, `regional`, `lugar`, `dominios`, `transporte`, `retiene`

**Respuesta exitosa:**
```json
{
  "message": "Registro creado exitosamente",
  "id": 18367
}
```

## Migración a MongoDB

Para migrar a MongoDB, cambiar la configuración en `app.py`:

```python
# Cambiar esta línea:
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fiscalizacion.db'

# Por esta:
app.config['SQLALCHEMY_DATABASE_URI'] = 'mongodb://localhost:27017/fiscalizacion'
```

Y actualizar las dependencias en `requirements.txt` para incluir el driver de MongoDB.

## Uso en Frontend

Reemplazar las llamadas a `datos.json` por fetch a la API:

```javascript
// En lugar de:
fetch('datos.json')
  .then(response => response.json())
  .then(data => {
    // Procesar datos
  });

// Usar:
fetch('/resumen')
  .then(response => response.json())
  .then(data => {
    console.log('Total cargas:', data.total_cargas);
  });
```

## Manejo de Errores

La API devuelve códigos HTTP apropiados:
- `200`: Éxito
- `201`: Recurso creado
- `400`: Datos inválidos
- `500`: Error del servidor

Los errores incluyen un mensaje descriptivo en el campo `error`.