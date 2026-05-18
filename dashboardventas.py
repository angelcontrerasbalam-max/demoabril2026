import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuración de la página de Streamlit ---
st.set_page_config(layout="wide", page_title="DEPARTAMENTO DE AFILIACIÓN Y VIGENCIA LA CEIBA IMSS")

# --- Título principal de la aplicación ---
st.title("DEPARTAMENTO DE AFILIACIÓN Y VIGENCIA LA CEIBA IMSS")

# --- Carga de datos con caché para eficiencia ---
@st.cache_data
def load_data():
    # !!! IMPORTANTE: Asegúrate de que 'PATRONES.xlsx' esté en el mismo directorio
    # que tu aplicación Streamlit, o ajusta esta ruta de archivo para tu despliegue.
    file_path = 'datos/PATRONES FINAL.xlsx'
    try:
        df = pd.read_excel(file_path)
        
        # Limpieza y preparación de datos
        df.columns = df.columns.str.strip().str.replace(' ', '_').str.upper() # Limpiar nombres de columnas
        df['FECHA_ULTIMO_MOV'] = pd.to_datetime(df['FECHA_ULTIMO_MOV'], errors='coerce')
        
        numeric_cols = ['TRABAJADORES', 'PRIMA_DE_RIESGO_ANTERIOR', 'PRIMA_DE_RIESGO_ACTUAL']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        return df
    except FileNotFoundError:
        st.error(f"Error: Archivo no encontrado en '{file_path}'. Por favor, asegúrese de que el archivo Excel esté en el mismo directorio que la aplicación Streamlit o ajuste la ruta del archivo.")
        st.stop()
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        st.stop()

df = load_data()

if df is not None:
    # --- Barra de búsqueda para REGISTRO PATRONAL ---
    st.header("Búsqueda de Patrones por Registro Patronal")
    registro_patronal_input = st.text_input("Ingrese REGISTRO PATRONAL para buscar:", "")

    if registro_patronal_input:
        # Filtrar el DataFrame buscando el registro patronal (case-insensitive y permite búsqueda parcial)
        filtered_df = df[df['REGISTRO_PATRONAL'].astype(str).str.contains(registro_patronal_input, case=False, na=False)]
        if not filtered_df.empty:
            st.dataframe(filtered_df)
        else:
            st.write("No se encontraron registros con ese REGISTRO PATRONAL.")
    else:
        st.write("Ingrese un REGISTRO PATRONAL para ver los detalles.")

    # --- Sección de Análisis Gráfico ---
    st.header("Análisis Gráfico de la Información")

    # Uso de pestañas para organizar las visualizaciones como subpáginas
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "Canal de Trámite", "Delegaciones", "Actividad Económica",
        "Número de Trabajadores", "Primas de Riesgo", "Tipo de Movimiento",
        "Frecuencia por Fecha", "Medio vs Tipo de Movimiento"
    ])

    with tab1:
        st.subheader("Canal de Trámite (Internet vs Ventanilla)")
        if 'MEDIO' in df.columns:
            medio_counts = df['MEDIO'].value_counts().reset_index()
            medio_counts.columns = ['Medio', 'Cantidad']
            fig1, ax1 = plt.subplots()
            ax1.pie(medio_counts['Cantidad'], labels=medio_counts['Medio'], autopct='%1.1f%%', startangle=90, colors=sns.color_palette("pastel"))
            ax1.axis('equal') # Asegura que el pastel se dibuje como un círculo
            st.pyplot(fig1)
            st.dataframe(medio_counts)
        else:
            st.write("Columna 'MEDIO' no encontrada para el análisis.")

    with tab2:
        st.subheader("Volumen de Trámites por Delegación")
        if 'DELEGACION' in df.columns:
            delegacion_counts = df['DELEGACION'].value_counts().sort_values(ascending=True)
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            sns.barplot(x=delegacion_counts.values, y=delegacion_counts.index.astype(str), ax=ax2, palette="viridis") # Convert index to string for plotting
            ax2.set_xlabel("Número de Trámites")
            ax2.set_ylabel("Delegación")
            st.pyplot(fig2)
            st.dataframe(delegacion_counts.reset_index(name='Cantidad').rename(columns={'index': 'Delegación'}))
        else:
            st.write("Columna 'DELEGACION' no encontrada para el análisis.")

    with tab3:
        st.subheader("Actividad Económica y Movimientos")
        if 'ACTIVIDAD' in df.columns:
            actividad_counts = df['ACTIVIDAD'].value_counts(normalize=True).mul(100).round(2).reset_index()
            actividad_counts.columns = ['Actividad', 'Porcentaje']
            st.markdown("**Empresas por Actividad Económica (porcentaje de movimientos):**")
            st.dataframe(actividad_counts.sort_values(by='Porcentaje', ascending=False))
            fig3, ax3 = plt.subplots(figsize=(12, 7))
            sns.barplot(x='Porcentaje', y='Actividad', data=actividad_counts.sort_values(by='Porcentaje', ascending=False), palette='magma')
            ax3.set_xlabel("Porcentaje (%)")
            ax3.set_ylabel("Actividad Económica")
            st.pyplot(fig3)
        else:
            st.write("Columna 'ACTIVIDAD' no encontrada para el análisis.")

    with tab4:
        st.subheader("Relación entre Número de Trabajadores y Frecuencia de Trámites")
        if 'TRABAJADORES' in df.columns and 'REGISTRO_PATRONAL' in df.columns:
            movement_frequency = df['REGISTRO_PATRONAL'].value_counts().reset_index()
            movement_frequency.columns = ['REGISTRO_PATRONAL', 'Frecuencia_Movimientos']
            
            df_workers_freq = df.groupby('REGISTRO_PATRONAL')['TRABAJADORES'].mean().reset_index()
            df_workers_freq = pd.merge(df_workers_freq, movement_frequency, on='REGISTRO_PATRONAL')

            fig4, ax4 = plt.subplots(figsize=(10, 6))
            sns.scatterplot(x='TRABAJADORES', y='Frecuencia_Movimientos', data=df_workers_freq, ax=ax4)
            ax4.set_xlabel("Número de Trabajadores")
            ax4.set_ylabel("Frecuencia de Movimientos")
            ax4.set_title("Número de Trabajadores vs. Frecuencia de Movimientos")
            st.pyplot(fig4)
            st.dataframe(df_workers_freq.sort_values(by='Frecuencia_Movimientos', ascending=False))
        else:
            st.write("Columnas 'TRABAJADORES' o 'REGISTRO_PATRONAL' no encontradas para el análisis.")

    with tab5:
        st.subheader("Comparación de Primas de Riesgo (Anterior vs Actual)")
        if 'PRIMA_DE_RIESGO_ANTERIOR' in df.columns and 'PRIMA_DE_RIESGO_ACTUAL' in df.columns and 'REGISTRO_PATRONAL' in df.columns:
            df['CAMBIO_PRIMA'] = df['PRIMA_DE_RIESGO_ACTUAL'] - df['PRIMA_DE_RIESGO_ANTERIOR']
            
            st.markdown("**Top 10 Patrones con mayor incremento en Prima de Riesgo:**")
            st.dataframe(df.nlargest(10, 'CAMBIO_PRIMA')[['REGISTRO_PATRONAL', 'PRIMA_DE_RIESGO_ANTERIOR', 'PRIMA_DE_RIESGO_ACTUAL', 'CAMBIO_PRIMA']])

            st.markdown("**Top 10 Patrones con mayor decremento en Prima de Riesgo:**")
            st.dataframe(df.nsmallest(10, 'CAMBIO_PRIMA')[['REGISTRO_PATRONAL', 'PRIMA_DE_RIESGO_ANTERIOR', 'PRIMA_DE_RIESGO_ACTUAL', 'CAMBIO_PRIMA']])
            
            fig5, (ax5a, ax5b) = plt.subplots(1, 2, figsize=(14, 6))
            sns.histplot(df['PRIMA_DE_RIESGO_ANTERIOR'].dropna(), kde=True, ax=ax5a, color='skyblue')
            ax5a.set_title('Distribución Prima de Riesgo ANTERIOR')
            ax5a.set_xlabel('Prima de Riesgo')
            sns.histplot(df['PRIMA_DE_RIESGO_ACTUAL'].dropna(), kde=True, ax=ax5b, color='salmon')
            ax5b.set_title('Distribución Prima de Riesgo ACTUAL')
            ax5b.set_xlabel('Prima de Riesgo')
            plt.tight_layout()
            st.pyplot(fig5)
            
            fig5b, ax5c = plt.subplots(figsize=(10, 6))
            sns.histplot(df['CAMBIO_PRIMA'].dropna(), kde=True, ax=ax5c, color='purple')
            ax5c.set_title('Distribución del Cambio en Prima de Riesgo (Actual - Anterior)')
            ax5c.set_xlabel('Cambio en Prima de Riesgo')
            st.pyplot(fig5b)
        else:
            st.write("Columnas de Prima de Riesgo o 'REGISTRO_PATRONAL' no encontradas para el análisis.")

    with tab6:
        st.subheader("Tipos de Movimiento")
        if 'ULTIMO_MOVIMIENTO' in df.columns:
            movimiento_counts = df['ULTIMO_MOVIMIENTO'].value_counts().sort_values(ascending=True)
            fig6, ax6 = plt.subplots(figsize=(10, 6))
            sns.barplot(x=movimiento_counts.values, y=movimiento_counts.index, ax=ax6, palette="cubehelix")
            ax6.set_xlabel("Cantidad")
            ax6.set_ylabel("Tipo de Movimiento")
            st.pyplot(fig6)
            st.dataframe(movimiento_counts.reset_index(name='Cantidad').rename(columns={'index': 'Tipo de Movimiento'}))
        else:
            st.write("Columna 'ULTIMO_MOVIMIENTO' no encontrada para el análisis.")

    with tab7:
        st.subheader("Frecuencia de Últimos Movimientos por Fecha")
        if 'FECHA_ULTIMO_MOV' in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df['FECHA_ULTIMO_MOV']):
                daily_movements = df.groupby(df['FECHA_ULTIMO_MOV'].dt.date).size().reset_index(name='Conteo')
                daily_movements.columns = ['Fecha', 'Conteo']
                
                if not daily_movements.empty:
                    fig7, ax7 = plt.subplots(figsize=(12, 6))
                    sns.lineplot(x='Fecha', y='Conteo', data=daily_movements, ax=ax7, marker='o')
                    ax7.set_title("Frecuencia de Últimos Movimientos por Fecha")
                    ax7.set_xlabel("Fecha")
                    ax7.set_ylabel("Número de Movimientos")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig7)
                    st.dataframe(daily_movements.sort_values(by='Fecha'))
                else:
                    st.write("No hay datos de fecha válidos para graficar.")
            else:
                st.write("La columna 'FECHA_ULTIMO_MOV' no es de tipo fecha. Por favor, revise el formato de los datos.")
        else:
            st.write("Columna 'FECHA_ULTIMO_MOV' no encontrada para el análisis.")

    with tab8:
        st.subheader("Medio del Trámite vs Tipo de Movimiento")
        if 'MEDIO' in df.columns and 'ULTIMO_MOVIMIENTO' in df.columns:
            st.markdown("**Tabla Cruzada:**")
            crosstab_medio_movimiento = pd.crosstab(df['MEDIO'], df['ULTIMO_MOVIMIENTO'])
            st.dataframe(crosstab_medio_movimiento)

            st.markdown("**Gráfico de Barras Agrupadas:**")
            fig8, ax8 = plt.subplots(figsize=(14, 7))
            crosstab_medio_movimiento.plot(kind='bar', stacked=False, ax=ax8)
            ax8.set_title("Medio del Trámite por Tipo de Movimiento")
            ax8.set_xlabel("Medio del Trámite")
            ax8.set_ylabel("Número de Movimientos")
            plt.xticks(rotation=45, ha='right')
            plt.legend(title="Tipo de Movimiento")
            plt.tight_layout()
            st.pyplot(fig8)
        else:
            st.write("Columnas 'MEDIO' o 'ULTIMO_MOVIMIENTO' no encontradas para el análisis.")
