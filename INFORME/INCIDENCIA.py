# Procesamiento de datos de incidencias de conducción /////

from turtle import pd


archivo_excel = pd.read_excel("Excel.xls")
print(archivo_excel.head())

df = pd.read_excel("Excel.xls")
df["Actaslabradas"] = (
    df["Actas Labradas"]
    .astype(str)
    .str.upper()
)
df["Incidencia Conduccion"] = (
    df["Actas labradas"].str.contains(
        "LICENCIA|DESCANSO|SUSTANCIA|ALCOHOL",
        regex=True,
        na=False
    ).astype(int)
)
actas_incidencia = (
    df
    .groupby("Acta")
    ["Incidencia Conduccion"]
    .sum()
    .rename(columns={"Incidencia Conduccion": "TotalIncidencias"})
)
actas_filtradas = actas_incidencia[
    actas_incidencia["TotalIncidencias"] > 0
]
def tipo_incidencia(texto):
    if "LICENCIA" in texto:
        return "LICENCIA"
    if "DESCANSO" in texto:
        return "DESCANSO"
    if "SUSTANCIA" in texto:
        return "SUSTANCIA"
    if "ALCOHOLIMETRO" in texto:
        return "ALCOHOLIMETRO"
    return None

df["Tipo Incidencia"] = df["Actaslabradas"].apply(tipo_incidencia)
resultado = (
    df[df["Incidencia Conduccion"] == 1]
    .groupby("Tipo Incidencia")
    .size()
    .reset_index(name="Cantidad Incidencias")
)
resultado = resultado.sort_values("Tipo Incidencia")
print(resultado)
resultado.to_excel("incidencias_conduccion_resumen.xlsx", index=False)

def crear_grafico_excel(nombre_archivo):
    libro = workbook.Workbook()
    hoja = libro.active
    hoja.title = "Incidencias Conducción"

    datos = [
        ["Tipo Incidencia", "Cantidad Incidencias"],
        ["Licencia", 45],
        ["Descanso", 30],
        ["Sustancias", 15],
        ["Alcoholímetro", 10],
    ]

    for fila in datos:
        hoja.append(fila)

    chart = BarChart()
    chart.title = "Incidencias de Conducción por Tipo"
    chart.x_axis.title = "Tipo Incidencia"
    chart.y_axis.title = "Cantidad Incidencias"

    data = Reference(hoja, min_col=2, min_row=1, max_row=len(datos))
    categorias = Reference(hoja, min_col=1, min_row=2, max_row=len(datos))
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(categorias)

    hoja.add_chart(chart, "E5")

    libro.save(nombre_archivo)