import streamlit as st
import pandas as pd

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
        df = pd.read_excel(file_path)
        # Ensure 'Registro Patronal' is treated as string for consistent search
        if 'Registro Patronal' in df.columns:
            df['Registro Patronal'] = df['Registro Patronal'].astype(str)
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please ensure it's in the correct directory.")
        return pd.DataFrame()

file_path = '/datos/PATRONES FINAL'
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
            # Display important information for the first match
            st.write("**Información del Expediente:**")
            
            # Identify and display key columns if they exist
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

            # You can also display the full row if needed
            # st.dataframe(filtered_df.head(1).T, use_container_width=True)

        else:
            st.warning(f"No se encontraron resultados para el Registro Patronal '{search_registro}'.")
    else:
        st.info("Por favor, ingresa un Registro Patronal para buscar.")

    st.markdown("--- ")

    # --- Placeholder for Visualizations and Tables ---
    st.header("Análisis y Visualizaciones")
    st.write("Aquí se agregarán las tablas dinámicas y gráficos solicitados.")

    # Example: Display a sample of the data (can be removed later)
    st.subheader("Vista previa de los datos:")
    st.dataframe(df.head())
else:
    st.error("No se pudo cargar el archivo de datos. Por favor, verifica la ruta y el formato del archivo.")
