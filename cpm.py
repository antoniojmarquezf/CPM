import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

st.title("Juego CPM - Ruta Crítica")

# ----------- FASE 1: Construcción del grafo -----------
st.header("1️⃣ Construye el grafo del proyecto")

edges_input = st.text_area(
    "Escribe las relaciones (Actividad -> Sucesora), una por línea",
    "A,B\nC,D\nB,E\nD,F,G\nF,H"
)

edges = []
if edges_input:
    for line in edges_input.splitlines():
        parts = line.split(",")
        origen = parts[0].strip()
        sucesores = [p.strip() for p in parts[1:]]
        for suc in sucesores:
            edges.append((origen, suc))

# Crear grafo
G = nx.DiGraph()
G.add_edges_from(edges)

# Dibujar grafo
fig, ax = plt.subplots()
nx.draw(G, with_labels=True, node_color="lightblue", node_size=1500, arrowsize=20, ax=ax)
st.pyplot(fig)

# ----------- FASE 2: Asignación de duraciones -----------
st.header("2️⃣ Asigna duraciones a cada actividad")

nodes = list(G.nodes())
durations_df = pd.DataFrame({"Actividad": nodes, "Duración": [0]*len(nodes)})
durations = st.data_editor(durations_df, num_rows="dynamic")

# ----------- FASE 3: Cálculo CPM -----------
if st.button("Calcular CPM"):
    # Guardar duraciones en dict
    dur_dict = dict(zip(durations["Actividad"], durations["Duración"]))

    # Calcular forward pass (simplificado)
    ES, EF = {}, {}
    for node in nx.topological_sort(G):
        if not list(G.predecessors(node)):
            ES[node] = 0
        else:
            ES[node] = max(EF[p] for p in G.predecessors(node))
        EF[node] = ES[node] + dur_dict[node]

    # Calcular backward pass
    LS, LF = {}, {}
    end_time = max(EF.values())
    for node in reversed(list(nx.topological_sort(G))):
        if not list(G.successors(node)):
            LF[node] = end_time
        else:
            LF[node] = min(LS[s] for s in G.successors(node))
        LS[node] = LF[node] - dur_dict[node]

    # Holgura
    Slack = {n: LS[n] - ES[n] for n in G.nodes()}

    result = pd.DataFrame({
        "Actividad": list(G.nodes()),
        "Duración": [dur_dict[n] for n in G.nodes()],
        "ES": [ES[n] for n in G.nodes()],
        "EF": [EF[n] for n in G.nodes()],
        "LS": [LS[n] for n in G.nodes()],
        "LF": [LF[n] for n in G.nodes()],
        "Holgura": [Slack[n] for n in G.nodes()],
    })

    st.subheader("📊 Resultados CPM")
    st.dataframe(result)

    critical_path = [n for n in G.nodes() if Slack[n] == 0]
    st.success(f"Ruta Crítica: {' -> '.join(critical_path)}")
