import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from pathlib import Path

# Instacart brand palette
INSTACART_GREEN = "#0AAD05"
INSTACART_ORANGE = "#FF7009"
INSTACART_DARK_GREEN = "#003D29"
INSTACART_WHITE = "#FFFFFF"

# Sequence used for categorical charts (department, user segment, etc.)
INSTACART_SEQUENCE = [INSTACART_GREEN, INSTACART_ORANGE, INSTACART_DARK_GREEN]

# Continuous scale used for heatmaps / gradient bars
INSTACART_CONTINUOUS = [INSTACART_WHITE, INSTACART_GREEN, INSTACART_DARK_GREEN]

# Resolve logo path relative to this file — works regardless of run directory
LOGO_PATH = Path(__file__).parent / "instacart-logo.png"
FAVICON_PATH = Path(__file__).parent / "favicon.png"

# Page config
st.set_page_config(
    page_title="Instacart Lakehouse Dashboard",
    page_icon=str(FAVICON_PATH) if FAVICON_PATH.exists() else "🛒",
    layout="wide"
)

# Brand styling
st.markdown(f"""
<style>
    .main {{
        background-color: {INSTACART_WHITE};
    }}
    section[data-testid="stSidebar"] .stRadio label {{
        color: {INSTACART_WHITE} !important;
    }}
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {{
        color: {INSTACART_GREEN} !important;
    }}
    h1, h2, h3 {{
        color: {INSTACART_DARK_GREEN};
    }}
    div[data-testid="stMetricValue"] {{
        color: {INSTACART_GREEN};
    }}
    div[data-testid="stMetricLabel"] {{
        color: {INSTACART_DARK_GREEN};
    }}
    .stButton>button {{
        background-color: {INSTACART_GREEN};
        color: {INSTACART_WHITE};
        border: none;
    }}
    .stButton>button:hover {{
        background-color: {INSTACART_ORANGE};
    }}
</style>
""", unsafe_allow_html=True)

# Header
logo_col1, logo_col2, logo_col3 = st.columns([1, 1, 1])
with logo_col2:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)
    else:
        st.markdown(f"<h1 style='text-align:center; color:{INSTACART_GREEN}'>🛒 Instacart Lakehouse</h1>", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_engine():
    return create_engine(
        "postgresql+psycopg2://dwh_user:dwh_password@localhost:5434/instacart_dwh"
    )

@st.cache_data(ttl=300)
def query(sql):
    return pd.read_sql(sql, get_engine())

# Sidebar
st.sidebar.title("Instacart Analytics")
page = st.sidebar.radio("View", [
    "Product Popularity",
    "Department Summary",
    "Order Time Analysis",
    "Aisle Reorder Analysis",
    "User Behaviour"
])

# Pages

if page == "Product Popularity":
    st.title("Product Popularity")
    df = query('SELECT * FROM dev_marts.mart_product_popularity ORDER BY reorder_rate DESC LIMIT 50')

    dept = st.selectbox("Filter by department", ["All"] + sorted(df["department"].unique().tolist()))
    if dept != "All":
        df = df[df["department"] == dept]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Products", len(df))
    col2.metric("Avg Reorder Rate", f"{df['reorder_rate'].mean():.2%}")
    col3.metric("Total Orders", f"{df['times_ordered'].sum():,}")

    fig = px.bar(df.head(20), x="product_name", y="reorder_rate",
                 color="department", color_discrete_sequence=INSTACART_SEQUENCE,
                 title="Top 20 Products by Reorder Rate",
                 labels={"reorder_rate": "Reorder Rate", "product_name": "Product"})
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df[["product_name", "department", "times_ordered", "times_reordered", "reorder_rate", "rank_in_department"]], use_container_width=True)


elif page == "Department Summary":
    st.title("Department Summary")
    df = query('SELECT * FROM dev_marts.mart_department_summary ORDER BY reorder_rate DESC')

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(df, x="department", y="total_orders", color="reorder_performance",
                     title="Total Orders by Department",
                     color_discrete_map={"High": INSTACART_GREEN, "Medium": INSTACART_ORANGE, "Low": INSTACART_DARK_GREEN})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(df, names="department", values="total_orders",
                     color_discrete_sequence=INSTACART_SEQUENCE,
                     title="Order Share by Department")
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)


elif page == "Order Time Analysis":
    st.title("Order Time Analysis")
    df = query('SELECT * FROM dev_marts.mart_order_time_analysis ORDER BY order_dow, hour_of_day')

    fig = px.density_heatmap(df, x="hour_of_day", y="day_of_week", z="total_orders",
                              color_continuous_scale=INSTACART_CONTINUOUS,
                              title="Order Heatmap — Day of Week vs Hour of Day",
                              labels={"hour_of_day": "Hour", "day_of_week": "Day", "total_orders": "Orders"})
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.bar(df.groupby("traffic_category")["total_orders"].sum().reset_index(),
                  x="traffic_category", y="total_orders", color="traffic_category",
                  title="Orders by Traffic Category",
                  color_discrete_map={"Peak": INSTACART_ORANGE, "High": INSTACART_GREEN,
                                       "Moderate": INSTACART_DARK_GREEN, "Low": "rgba(10,173,5,0.4)"})
    st.plotly_chart(fig2, use_container_width=True)


elif page == "Aisle Reorder Analysis":
    st.title("Aisle Reorder Analysis")
    df = query('SELECT * FROM dev_marts.mart_aisle_reorder_analysis ORDER BY reorder_rank LIMIT 30')

    fig = px.bar(df, x="aisle", y="reorder_rate", color="reorder_rate",
                 color_continuous_scale=INSTACART_CONTINUOUS,
                 title="Top 30 Aisles by Reorder Rate")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)


elif page == "User Behaviour":
    st.title("User Order Behaviour")
    df = query('SELECT * FROM dev_marts.mart_user_order_behaviour')

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Users", f"{len(df):,}")
    col2.metric("Avg Orders/User", f"{df['total_orders'].mean():.1f}")
    col3.metric("Avg Basket Size", f"{df['avg_basket_size'].mean():.1f}")

    seg_counts = df["user_segment"].value_counts().reset_index()
    seg_counts.columns = ["segment", "count"]
    fig = px.pie(seg_counts, names="segment", values="count",
                 title="User Segments",
                 color="segment",
                 color_discrete_map={"High Value": INSTACART_GREEN, "Regular": INSTACART_ORANGE, "Occasional": INSTACART_DARK_GREEN})
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.scatter(df.sample(min(5000, len(df))), x="total_orders", y="avg_basket_size",
                      color="user_segment", color_discrete_sequence=INSTACART_SEQUENCE, opacity=0.5,
                      title="Orders vs Basket Size by User Segment")
    st.plotly_chart(fig2, use_container_width=True)