import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Simulador Industrial V7", layout="wide")
st.title("🏭 Panel de Control: Línea de Producción")

# --- PANEL LATERAL (INPUTS) ---
st.sidebar.header("Configuración de la Fábrica")
velocidad_corte = st.sidebar.slider("Tiempo de Corte (seg)", 1, 10, 3)
velocidad_ensamble = st.sidebar.slider("Tiempo de Ensamble (seg)", 1, 10, 4)
total_piezas = st.sidebar.number_input("Cantidad de piezas a simular", 1, 50, 5)

if st.sidebar.button("▶️ Iniciar Simulación"):
    # Contenedores para la visualización
    col1, col2 = st.columns([2, 1])
    
    with col1:
        status_text = st.empty()
        # Creamos una escena 3D vacía con Plotly
        fig_placeholder = st.empty()
        
    with col2:
        st.subheader("Reporte en Vivo")
        tabla_placeholder = st.empty()

    datos = []
    
    # --- PROCESO DE SIMULACIÓN ---
    for i in range(1, total_piezas + 1):
        inicio = time.time()
        
        # Etapa 1: Corte
        status_text.warning(f"Pieza {i}: En proceso de CORTE...")
        time.sleep(velocidad_corte / 10) # Simulación rápida
        
        # Etapa 2: Ensamble
        status_text.error(f"Pieza {i}: En proceso de ENSAMBLE...")
        time.sleep(velocidad_ensamble / 10)
        
        fin = time.time()
        duracion = round(fin - inicio, 2)
        
        # Guardar datos
        datos.append({"Pieza": f"P-{i}", "Segundos": duracion, "Estado": "Completado"})
        
        # --- ACTUALIZAR GRÁFICO 3D ---
        # Representamos las piezas como puntos en un espacio 3D
        df_temp = pd.DataFrame(datos)
        fig = go.Figure(data=[go.Scatter3d(
            x=df_temp.index, y=[1]*len(df_temp), z=df_temp["Segundos"],
            mode='markers+lines',
            marker=dict(size=10, color=df_temp["Segundos"], colorscale='Viridis')
        )])
        fig.update_layout(title="Flujo de Producción (Tiempo vs Pieza)", margin=dict(l=0, r=0, b=0, t=30))
        fig_placeholder.plotly_chart(fig, use_container_width=True)
        
        # Actualizar Tabla
        tabla_placeholder.table(df_temp.tail(5))

    status_text.success("✅ Simulación finalizada")
    
    # --- BOTÓN DE DESCARGA ---
    csv = df_temp.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Reporte Excel (CSV)", csv, "reporte.csv", "text/csv")
