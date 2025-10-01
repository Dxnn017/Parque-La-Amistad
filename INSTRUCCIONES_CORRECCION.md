# Instrucciones para Corregir el Error de Fechas

## Problema
Error: "Invalid comparison between dtype=datetime64[ns] and date"

Este error ocurre porque pandas lee las fechas del CSV como `datetime64[ns]`, pero el código intenta compararlas con objetos `date` de Python.

## Solución Rápida

### Opción 1: Reemplazar Funciones Manualmente

1. Abre tu `streamlit_app.py` en GitHub o en tu editor local

2. Busca la función `cargar_datos_residuos()` y reemplázala con:

\`\`\`python
def cargar_datos_residuos():
    """Carga datos de residuos con manejo correcto de fechas"""
    try:
        if not os.path.exists("dataset/residuos_parque.csv"):
            df = pd.DataFrame(columns=[
                'ID', 'Zona', 'Ubicación (GPS)', 'Tipo de residuo',
                'Peso estimado (kg)', 'Fecha de registro', 'Observaciones', 'Evidencia'
            ])
            df.to_csv("dataset/residuos_parque.csv", index=False, encoding='utf-8')
            return df
        
        df = pd.read_csv("dataset/residuos_parque.csv", encoding='utf-8')
        
        # CORRECCIÓN: Convertir columna de fecha correctamente
        if 'Fecha de registro' in df.columns:
            df['Fecha de registro'] = pd.to_datetime(df['Fecha de registro'], errors='coerce')
        
        return df
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        return pd.DataFrame(columns=[
            'ID', 'Zona', 'Ubicación (GPS)', 'Tipo de residuo',
            'Peso estimado (kg)', 'Fecha de registro', 'Observaciones', 'Evidencia'
        ])
\`\`\`

3. Busca la función `filtrar_datos_residuos()` y reemplaza la sección de filtrado por fechas:

\`\`\`python
# Dentro de filtrar_datos_residuos(), reemplaza el bloque de filtrado por fechas:
if fecha_inicio is not None or fecha_fin is not None:
    if 'Fecha de registro' in df_filtrado.columns:
        df_filtrado['Fecha de registro'] = pd.to_datetime(
            df_filtrado['Fecha de registro'], 
            errors='coerce'
        )
        
        if fecha_inicio is not None:
            fecha_inicio_dt = pd.to_datetime(fecha_inicio)
            df_filtrado = df_filtrado[df_filtrado['Fecha de registro'] >= fecha_inicio_dt]
        
        if fecha_fin is not None:
            fecha_fin_dt = pd.to_datetime(fecha_fin)
            df_filtrado = df_filtrado[df_filtrado['Fecha de registro'] <= fecha_fin_dt]
\`\`\`

4. En las funciones `guardar_registro_residuo()` y `actualizar_registro_residuo()`, asegúrate de convertir la fecha a string:

\`\`\`python
# Convertir fecha a string en formato ISO
fecha_str = fecha.strftime('%Y-%m-%d') if isinstance(fecha, date) else str(fecha)

# Luego usa fecha_str en lugar de fecha al guardar:
'Fecha de registro': fecha_str,
\`\`\`

### Opción 2: Agregar Función Helper

Agrega esta función helper al inicio de tu archivo (después de los imports):

\`\`\`python
def normalizar_fecha_para_comparacion(fecha_input):
    """Convierte cualquier tipo de fecha a datetime64 para comparaciones"""
    if fecha_input is None:
        return None
    return pd.to_datetime(fecha_input)
\`\`\`

Y úsala en todas las comparaciones de fechas:

\`\`\`python
# Antes:
if df['Fecha de registro'] >= fecha_inicio:

# Después:
if df['Fecha de registro'] >= normalizar_fecha_para_comparacion(fecha_inicio):
\`\`\`

## Verificación

Después de aplicar los cambios:

1. Guarda el archivo
2. Haz commit y push a GitHub:
   \`\`\`bash
   git add streamlit_app.py
   git commit -m "Fix: Corregido error de comparación de fechas"
   git push origin main
   \`\`\`
3. Espera que Streamlit Cloud se actualice (1-2 minutos)
4. Prueba registrar un nuevo residuo

## Si el Error Persiste

Si después de aplicar estos cambios el error continúa, comparte:
1. El mensaje de error completo
2. La línea específica donde ocurre el error
3. Un pantallazo del error en Streamlit
