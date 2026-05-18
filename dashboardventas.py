import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np # Often useful for numerical operations

# --- Page Configuration ---
st.set_page_config(
    page_title="AFILIACIÓN Y VIGENCIA YUCATÁN SUB DELEGACION 33 LA CEIBA",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Data ---
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel('datos/PATRONES FINAL.xlsx')
        # Ensure 'Registro Patronal' is treated as string for consistent search
        if 'Registro Patronal' in df.columns:
            df['Registro Patronal'] = df['Registro Patronal'].astype(str)
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please ensure it's in the correct directory.")
        return pd.DataFrame()

# --- IMPORTANT: Update this path if your Excel file is located elsewhere ---
file_path = 'datos/PATRONES FINAL.xlsx'
df = load_data(file_path)

# --- Title ---
st.title("🏢 AFILIACIÓN Y VIGENCIA YUCATÁN SUB DELEGACION 33 LA CEIBA 🏢")
st.markdown("--- ")

# --- Search Bar ---
st.header("Buscador de Registros Patronales")
search_registro = st.text_input("Ingresa el Registro Patronal para buscar:", "").strip()

if not df.empty:
    if search_registro:
        filtered_df = df[df['Registro Patronal'].str.contains(search_registro, case=False, na=False)]
        
        if not filtered_df.empty:
            st.subheader(f"Resultados para Registro Patronal: {search_registro}")
            st.write("**Información del Expediente:**")
            
            display_columns = [
                'NOMBRE O RAZÓN SOCIAL',
                'DOMICILIO',
                'Ubicación Expediente' # Assuming this is the correct column name based on user request
            ]

            for col in display_columns:
                if col in filtered_df.columns:
                    st.write(f"**{col}:** {filtered_df.iloc[0][col]}")
                else:
                    st.warning(f"Columna '{col}' no encontrada en el archivo Excel.")

        else:
            st.warning(f"No se encontraron resultados para el Registro Patronal '{search_registro}'.")
    else:
        st.info("Por favor, ingresa un Registro Patronal para buscar.")

    st.markdown("--- ")

    # --- Data Preprocessing for Visualizations ---
    # Make sure these column names match your Excel file exactly
    # You might need to adjust them based on your actual data

    # Convert date columns to datetime objects
    if 'Fecha Ultimo Movimiento' in df.columns:
        df['Fecha Ultimo Movimiento'] = pd.to_datetime(df['Fecha Ultimo Movimiento'], errors='coerce')

    # Convert numeric columns to numeric types
    if 'Numero de Trabajadores' in df.columns:
        df['Numero de Trabajadores'] = pd.to_numeric(df['Numero de Trabajadores'], errors='coerce')

    if 'Prima Riesgo Anterior' in df.columns:
        df['Prima Riesgo Anterior'] = pd.to_numeric(df['Prima Riesgo Anterior'], errors='coerce')
    if 'Prima Riesgo Actual' in df.columns:
        df['Prima Riesgo Actual'] = pd.to_numeric(df['Prima Riesgo Actual'], errors='coerce')


    # --- Visualizations and Tables ---
    st.header("Análisis y Visualizaciones")

    # 1. Actividad económica: Tabla dinámica con porcentajes
    st.subheader("📊 Actividad Económica - Distribución")
    if 'Actividad Económica' in df.columns:
        actividad_economica_counts = df['Actividad Económica'].value_counts(normalize=True).reset_index()
        actividad_economica_counts.columns = ['Actividad Económica', 'Porcentaje']
        actividad_economica_counts['Porcentaje'] = (actividad_economica_counts['Porcentaje'] * 100).round(2).astype(str) + '%'
        st.dataframe(actividad_economica_counts, use_container_width=True)
    else:
        st.warning("Columna 'Actividad Económica' no encontrada para el análisis. Por favor, verifica el nombre de la columna.")

    st.markdown("--- ")

    # 2. Número de trabajadores: Gráfica de dispersión (scatter plot)
    st.subheader("📈 Número de Trabajadores vs. Frecuencia de Trámites")
    if 'Numero de Trabajadores' in df.columns and 'Registro Patronal' in df.columns:
        tramite_frequency = df['Registro Patronal'].value_counts().reset_index()
        tramite_frequency.columns = ['Registro Patronal', 'Frecuencia de Trámites']
        
        workers_and_frequency = df.groupby('Registro Patronal')['Numero de Trabajadores'].mean().reset_index()
        workers_and_frequency = pd.merge(workers_and_frequency, tramite_frequency, on='Registro Patronal', how='left')
        
        workers_and_frequency.dropna(subset=['Numero de Trabajadores', 'Frecuencia de Trámites'], inplace=True)

        if not workers_and_frequency.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.scatterplot(
                x='Numero de Trabajadores', 
                y='Frecuencia de Trámites', 
                data=workers_and_frequency,
                hue='Frecuencia de Trámites', 
                size='Numero de Trabajadores', 
                sizes=(20, 400),
                palette='viridis',
                alpha=0.7,
                ax=ax
            )
            ax.set_title('Número de Trabajadores vs. Frecuencia de Trámites')
            ax.set_xlabel('Número de Trabajadores')
            ax.set_ylabel('Frecuencia de Trámites (por Registro Patronal)')
            st.pyplot(fig)
        else:
            st.info("No hay datos suficientes para generar la gráfica de dispersión de trabajadores y trámites.")
    else:
        st.warning("Columnas 'Numero de Trabajadores' o 'Registro Patronal' no encontradas para el análisis. Por favor, verifica los nombres de las columnas.")

    st.markdown("--- ")

    # 3. Primas de riesgo: Comparar prima anterior vs actual
    st.subheader("📈 Comparación de Primas de Riesgo (Anterior vs Actual)")
    if 'Prima Riesgo Anterior' in df.columns and 'Prima Riesgo Actual' in df.columns and 'Registro Patronal' in df.columns:
        prima_data = df[['Registro Patronal', 'Prima Riesgo Anterior', 'Prima Riesgo Actual']].dropna()
        
        if not prima_data.empty:
            if len(prima_data) > 50: 
                sample_prima_data = prima_data.sample(n=50, random_state=42).reset_index(drop=True)
            else:
                sample_prima_data = prima_data

            prima_melted = sample_prima_data.melt(
                id_vars='Registro Patronal',
                value_vars=['Prima Riesgo Anterior', 'Prima Riesgo Actual'],
                var_name='Tipo de Prima',
                value_name='Valor de Prima'
            )

            fig, ax = plt.subplots(figsize=(12, 7))
            sns.barplot(
                x='Registro Patronal', 
                y='Valor de Prima', 
                hue='Tipo de Prima', 
                data=prima_melted,
                palette={'Prima Riesgo Anterior': 'skyblue', 'Prima Riesgo Actual': 'salmon'},
                ax=ax
            )
            ax.set_title('Primas de Riesgo: Anterior vs Actual por Registro Patronal (Muestra)')
            ax.set_xlabel('Registro Patronal')
            ax.set_ylabel('Valor de Prima')
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("No hay datos de primas de riesgo para comparar.")
    else:
        st.warning("Columnas 'Prima Riesgo Anterior', 'Prima Riesgo Actual' o 'Registro Patronal' no encontradas para el análisis. Por favor, verifica los nombres de las columnas.")

    st.markdown("--- ")

    # 4. Tipo de movimiento: Gráfica de barras apiladas
    st.subheader("📊 Tipos de Movimiento")
    if 'Tipo de Movimiento' in df.columns:
        movimiento_counts = df['Tipo de Movimiento'].value_counts().reset_index()
        movimiento_counts.columns = ['Tipo de Movimiento', 'Conteo']

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x='Tipo de Movimiento', y='Conteo', data=movimiento_counts, palette='pastel', ax=ax)
        ax.set_title('Frecuencia de Tipos de Movimiento')
        ax.set_xlabel('Tipo de Movimiento')
        ax.set_ylabel('Número de Movimientos')
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("Columna 'Tipo de Movimiento' no encontrada para el análisis. Por favor, verifica el nombre de la columna.")

    st.markdown("--- ")

    # 5. Último movimiento: Gráfica de líneas con eje temporal
    st.subheader("📅 Frecuencia de Últimos Movimientos por Fecha")
    if 'Fecha Ultimo Movimiento' in df.columns:
        movements_by_date = df.dropna(subset=['Fecha Ultimo Movimiento'])
        movements_by_date = movements_by_date.groupby(pd.Grouper(key='Fecha Ultimo Movimiento', freq='D')).size().reset_index(name='Conteo')

        if not movements_by_date.empty:
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.lineplot(x='Fecha Ultimo Movimiento', y='Conteo', data=movements_by_date, marker='o', color='green', ax=ax)
            ax.set_title('Frecuencia Diaria de Últimos Movimientos')
            ax.set_xlabel('Fecha')
            ax.set_ylabel('Número de Movimientos')
            ax.grid(True, linestyle='--', alpha=0.6)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("No hay datos de 'Fecha Ultimo Movimiento' válidos para graficar.")
    else:
        st.warning("Columna 'Fecha Ultimo Movimiento' no encontrada para el análisis. Por favor, verifica el nombre de la columna.")

    st.markdown("--- ")

    # 6. Canal de trámite: Gráfica de columnas o pastel
    st.subheader("🌐 Canal de Trámite")
    if 'Canal de Trámite' in df.columns:
        canal_counts = df['Canal de Trámite'].value_counts().reset_index()
        canal_counts.columns = ['Canal de Trámite', 'Conteo']

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(
            canal_counts['Conteo'], 
            labels=canal_counts['Canal de Trámite'], 
            autopct='%1.1f%%', 
            startangle=90, 
            colors=sns.color_palette('viridis', len(canal_counts))
        )
        ax.set_title('Distribución de Canales de Trámite')
        ax.axis('equal') 
        st.pyplot(fig)
    else:
        st.warning("Columna 'Canal de Trámite' no encontrada para el análisis. Por favor, verifica el nombre de la columna.")

else:
    st.error("No se pudo cargar el archivo de datos o está vacío. Por favor, verifica la ruta y el formato del archivo PATRONES.xlsx.")

