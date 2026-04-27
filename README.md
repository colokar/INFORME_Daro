# Dashboard de Fiscalización - CNRT 🚍🚛

Proyecto desarrollado para la visualización dinámica y el análisis de datos operativos de transporte, enfocado en el seguimiento de métricas de control en las categorías de Cargas y Pasajeros.

## 📊 Funcionalidades
- **Monitoreo de Retenciones:** Reporte detallado de retenciones por alcoholemia positiva y consumo de sustancias.
- **Métricas Regionales:** Visualización de actas labradas y vehículos controlados distribuidos por región.
- **Interfaz Dinámica:** Dashboard interactivo con actualización de datos en tiempo real mediante JavaScript y procesamiento backend en Python.
- **Estética Profesional:** Integración de recursos visuales oficiales para reportes más legibles y dinámicos.

## 🚀 Instalación y Configuración

Seguí estos pasos para configurar el entorno de desarrollo localmente:

### 1. Clonar el repositorio
```bash
git clone [https://github.com/colokar/INFORME_Daro.git](https://github.com/colokar/INFORME_Daro.git)
cd INFORME_Daro

2. Gestión del Entorno Virtual
Es fundamental usar un entorno virtual para mantener las dependencias aisladas:

Bash
# Crear el entorno
python -m venv .venv

# Activar el entorno (Windows)
.venv\Scripts\activate

# Activar el entorno (Linux/Mac)
source .venv/bin/activate

3. Instalación de Dependencias (Requerimientos)
Una vez activado el entorno virtual, instalá todos los paquetes necesarios para el procesamiento de datos y el servidor web:

Bash
pip install --upgrade pip
pip install -r requirements.txt
4. Ejecución del Proyecto
Para iniciar el servidor local y visualizar el dashboard:

Bash
python app.py
Luego, abrí tu navegador en: http://127.0.0.1:5000

📂 Estructura del Proyecto
INFORME/: Núcleo del frontend (contiene index.html, STYLE.css y la lógica de actualizar_tabla_regiones.js).

IMAGENES/: Repositorio de recursos visuales y logos oficiales.

app.py: Servidor Flask y rutas de la API.

gestor_fiscalizacion.py: Lógica de procesamiento y filtrado de datos de transporte.

fiscalizacion.db: Base de datos local (SQLite) para el almacenamiento de registros.

.gitignore: Configuración para evitar la subida de entornos virtuales y archivos temporales.

Desarrollado para optimizar la gestión de datos en el Departamento Operativo.


### Pasos para actualizarlo en tu repo:
1. Abrí el archivo `README.md` en VS Code.
2. Borrá todo lo anterior y pegá este bloque.
3. En la terminal tirá estos tres comandos para subirlo:
   ```bash
   git add README.md
   git commit -m "📝 README actualizado con instrucciones de instalación completas"
   git push
