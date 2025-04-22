import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

st.set_page_config(page_title="IT Architecture to Financial Mapping", layout="wide")
st.title("\U0001F5FA\ufe0f IT Architecture - Financial Impact Mapper")

# --- Data Model (Simplified) ---
st.sidebar.header("\U0001F4C8 Define Components")

with st.sidebar.expander("+ Add IT Component"):
    if "components" not in st.session_state:
        st.session_state.components = []

    name = st.text_input("Component Name")
    category = st.selectbox("Category", ["Hardware", "Software", "Personnel", "Maintenance", "Telecom", "Cybersecurity", "BC/DR"])
    spend = st.number_input("Annual Spend ($K)", min_value=0, value=100, step=10)
    revenue_support = st.slider("% Revenue Supported", 0, 100, 20)
    risk_score = st.slider("Risk if Fails (0 = none, 100 = catastrophic)", 0, 100, 50)

    if st.button("Add Component"):
        st.session_state.components.append({
            "Name": name,
            "Category": category,
            "Spend": spend * 1000,
            "Revenue Impact %": revenue_support,
            "Risk Score": risk_score
        })

# Convert to DataFrame
if st.session_state.components:
    df = pd.DataFrame(st.session_state.components)
    st.subheader("\U0001F4CA Component Mapping Table")
    st.dataframe(df)
else:
    st.info("Add components using the sidebar to get started.")

# --- Architecture Diagram using NetworkX + Plotly ---
if st.session_state.components:
    G = nx.Graph()
    for i, row in df.iterrows():
        G.add_node(row['Name'], category=row['Category'], spend=row['Spend'], revenue=row['Revenue Impact %'], risk=row['Risk Score'])

    # Simple linking: create edges between adjacent components
    names = df['Name'].tolist()
    for i in range(len(names)-1):
        G.add_edge(names[i], names[i+1])

    pos = nx.spring_layout(G, seed=42)

    node_x = []
    node_y = []
    node_text = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        attr = G.nodes[node]
        text = f"{node}<br>Category: {attr['category']}<br>Spend: ${attr['spend']:,}<br>Revenue Support: {attr['revenue']}%<br>Risk: {attr['risk']}"
        node_text.append(text)

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='gray'),
        hoverinfo='none', mode='lines'))

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        textposition="top center",
        marker=dict(
            size=20,
            color=df['Risk Score'],
            colorscale='YlOrRd',
            showscale=True,
            colorbar=dict(title="Risk")
        ),
        text=df['Name'],
        hovertext=node_text,
        hoverinfo='text'))

    fig.update_layout(
        title="\U0001F4D0 Architecture Dependency Map",
        showlegend=False,
        height=600,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.subheader("\U0001F5FA️ Architecture Diagram")
    st.plotly_chart(fig, use_container_width=True)

    # Totals
    st.subheader("\U0001F4B0 Financial Summary")
    total_spend = df['Spend'].sum()
    avg_revenue_supported = df['Revenue Impact %'].mean()
    avg_risk = df['Risk Score'].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total IT Spend", f"${total_spend:,.0f}")
    col2.metric("Avg. Revenue Supported", f"{avg_revenue_supported:.1f}%")
    col3.metric("Avg. Risk Score", f"{avg_risk:.1f}")
