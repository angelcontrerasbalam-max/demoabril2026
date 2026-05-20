import streamlit as st
import pandas as pd

def main():
    # Set page configuration for a formal, executive style
    st.set_page_config(
        page_title="DEPARTAMENTO DE AFILIACIÓN Y VIGENCIA SUB DELEGACIÓN 33 LA CEIBA",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for formal and executive style
    st.markdown(
        """
        <style>
        .reportview-container {
            background: #f0f2f6; /* Light gray background */
        }
        .sidebar .sidebar-content {
            background: #ffffff; /* White sidebar */
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50; /* Dark blue-gray for headers */
        }
        .stButton>button {
            background-color: #3498db; /* Blue button */
            color: white;
        }
        .stTextInput>div>div>input {
            border-radius: 5px;
            border: 1px solid #ccc;
            padding: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("DEPARTAMENTO DE AFILIACIÓN Y VIGENCIA SUB DELEGACIÓN 33 LA CEIBA")

    # Load the data
    file_path = 'datos/PATRONES PROYECTO FINAL.xlsx'
    df = pd.read_excel(file_path)

    st.write("---  \n### Búsqueda de Patrones \n---")
    search_term = st.text_input("Introduce el Registro Patronal para buscar:")

    if search_term:
        # Filter DataFrame based on search term
        filtered_df = df[df['REGISTRO PATRONAL'].str.contains(search_term, case=False, na=False)]
        
        if not filtered_df.empty:
            st.write(f"Resultados para Registro Patronal: **{search_term}**")
            for index, row in filtered_df.iterrows():
                st.json(row.to_dict())
                st.write(f"**Ubicación del Archivo:** {row['UBICACIÓN DE ARCHIVO']}")
                st.write("---")
        else:
            st.warning(f"No se encontraron resultados para el Registro Patronal: {search_term}")

    # Placeholder for the tabs section
    st.markdown("\n---  \n## Gráficos Ilustrativos \n---")
    st.write("Aquí se mostrarán las gráficas en diferentes pestañas.")

    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Estatus Patronal", 
        "Motivos de Baja", 
        "Actividades Económicas", 
        "Primas de Riesgo", 
        "Trabajadores por Actividad", 
        "Movimientos Afiliatorios"
    ])

    with tab1:
        st.header("ESTATUS PATRONAL SECCIÓN NORTE")
        st.write("Contenido de la gráfica de estatus patronal.")

    with tab2:
        st.header("PRINCIPALES MOTIVOS DE BAJA PATRONAL")
        st.write("Contenido de la gráfica de motivos de baja.")

    with tab3:
        st.header("PRINCIPALES ACTIVIDADES ECONOMICAS DE PATRONES EN LA DELEGACIÓN NORTE")
        st.write("Contenido de la gráfica de actividades económicas.")

    with tab4:
        st.header("PRIMAS DE RIESGO PATRONALES")
        st.write("Contenido del análisis de primas de riesgo.")

    with tab5:
        st.header("TRABAJADORES POR ACTIVIDAD")
        st.write("Contenido del análisis de trabajadores por actividad.")

    with tab6:
        st.header("MOVIMIENTOS AFILIATORIOS")
        st.write("Contenido del análisis de movimientos afiliatorios.")

if __name__ == '__main__':
    main()
