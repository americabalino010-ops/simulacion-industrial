import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# --- CONFIGURACIÓN RETRO ---
st.set_page_config(page_title="Pixel Factory 8-Bit", layout="wide")

# Estilo CSS para que se vea más como videojuego (fuente y colores)
st.markdown("""
    <style>
    @import url('https://googleapis.com');
    .pixel-font { font-family: 'Press+Start+2P', cursive; color: #33ff33; }
    .stApp { background-color: #000000; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="pixel-font">🏭 PIXEL FACTORY V15</h1>', unsafe_allow_html=True)

# --- CONTROLES ---
st.sidebar.markdown('<p class="pixel-font" style="font-size:12px;">CONTROLES</p>', unsafe_allow_html=True)
pos_supervisor = st.sidebar.slider("🕹️ MOVER SUPERVISOR", 0, 10, 5)
lote = st.sidebar.number_input("PIEZAS", 5, 20, 10)

# --- RENDERIZADO PIXEL ART ---
def generar_pixel_factory(pos_pieza, pos_ing, estado_pz, id_pz):
    fig = go.Figure()

    # 1. EL SUELO (Piso de rejilla tipo Pacman)
    fig.add_shape(type="rect", x0=0, y0=0, x1=10, y1=6, fillcolor="#1a1a1a", line_color="#333")

    # 2. LAS MÁQUINAS (Sprites con Emojis)
    # Estación Corte
    fig.add_annotation(x=1, y=3, text="💾", font_size=50, showarrow=False)
    fig.add_annotation(x=1, y=1, text="CORTE", font_size=12, font_color="cyan", showarrow=False)

    # Estación Ensamble
    fig.add_annotation(x=9, y=3, text="🤖", font_size=50, showarrow=False)
    fig.add_annotation(x=9, y=1, text="ENSAMBLE", font_size=12, font_color="orange", showarrow=False)

    # 3. LA BANDA (Camino de puntos)
    for dot in range(2, 9):
        fig.add_annotation(x=dot, y=3, text=".", font_size=20, font_color="white", showarrow=False)

    # 4. LA PIEZA (Sprite dinámico)
    # Cambia de emoji según el estado
    sprite_pz = "📦" if estado_pz == "PROCESO" else ("⭐" if estado_pz == "OK" else "💀")
    fig.add_trace(go.Scatter(
        x=[pos_pieza], y=[3],
        mode='text',
        text=[sprite_pz],
        textfont=dict(size=40),
        name="Pieza"
    ))

    # 5. EL INGENIERO (Mario / Supervisor)
    fig.add_trace(go.Scatter(
        x=[pos_ing], y=[5],
        mode='text',
        text=["👷"],
        textfont=dict(size=45),
        name="Supervisor"
    ))

    # Ajustes de pantalla de juego
    fig.update_xaxes(range=[0, 10], showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(range=[0, 6], showgrid=False, zeroline=False, visible=False)
    fig.update_layout(
        height=400, 
        paper_bgcolor="black", 
        plot_bgcolor="black",
        margin=dict(l=0, r=0, b=0, t=0),
        showlegend=False
    )
    return fig

# --- LOOP DE JUEGO ---
if st.sidebar.button("▶️ START GAME"):
    viz = st.empty()
    col1, col2, col3 = st.columns(3)
    score_n = col1.empty()
    score_m = col2.empty()
    score_y = col3.empty()

    ganado, perdido, fallos = 0, 0, 0
    # Creamos un contador para generar IDs únicos
    step_id = 0

    for i in range(1, lote + 1):
        nombre = f"P{i}"
        
        # MOVIMIENTO CORTE -> ENSAMBLE
        pasos = np.linspace(1, 9, 8)
        for p in pasos:
            step_id += 1
            # Agregamos 'key' para que Streamlit no se confunda
            viz.plotly_chart(
                generar_pixel_factory(p, pos_supervisor, "PROCESO", nombre), 
                use_container_width=True, 
                key=f"anim_{step_id}"
            )
            time.sleep(0.05)

        # LÓGICA DE AZAR
        suerte = np.random.random()
        step_id += 1 # Aumentamos el ID para el resultado final
        
        if suerte < 0.15:
            res = "RECHAZADA"
            perdido += 50
            fallos += 1
            viz.plotly_chart(generar_pixel_factory(9, pos_supervisor, "RECHAZADA", nombre), use_container_width=True, key=f"res_{step_id}")
        else:
            res = "OK"
            ganado += 100
            viz.plotly_chart(generar_pixel_factory(9, pos_supervisor, "OK", nombre), use_container_width=True, key=f"res_{step_id}")

        # ACTUALIZAR MARCADOR
        score_n.metric("CASH", f"${ganado - perdido}")
        score_m.metric("LOSS", f"${perdido}")
        score_y.metric("YIELD", f"{round(((i-fallos)/i)*100, 1)}%")
        
        time.sleep(0.3)

    st.balloons()

