import pandas as pd
import plotly.express as px
import streamlit as st

from utils import fetch_assets, format_currency, load_asset_classes


st.set_page_config(
    page_title="Diversify - Simple portfolio management app",
)

st.title("Diversify - 🏠 Home")
st.write("*Simple portfolio management app*")

with open("/app/css/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


assets = fetch_assets()


def show_assets(assets: list[dict]):
    n_assets = len(assets)
    for k in range(0, n_assets, 4):
        cols = st.columns(4)
        for i in range(4):
            try:
                asset = assets[k + i]
                with cols[i]:
                    st.write(f"{asset.get('name')}")
                    st.write(f"**{format_currency(asset.get('value'))}**")
            except IndexError:
                pass


def show_all_assets(assets: list[dict]):
    asset_classes = load_asset_classes()
    for asset_class in asset_classes:
        st.subheader(asset_class)
        class_assets = [
            asset for asset in assets if asset.get("class_name") == asset_class
        ]
        show_assets(class_assets)


def show_classes_allocation(assets: list[dict]):
    df = pd.DataFrame(assets)
    pie = px.pie(
        df,
        values="value",
        names="class_name",
        title="Asset classes allocation",
        color_discrete_sequence=px.colors.sequential.dense,
    )
    st.plotly_chart(pie)


def show_assets_allocation(assets: list[dict]):
    asset_classes = load_asset_classes()
    df = pd.DataFrame(assets)
    cols = st.columns(len(asset_classes))
    for col, asset_class in zip(cols, asset_classes):
        with col:
            with st.container():
                df_asset_class = df[df["class_name"] == asset_class]
                if df_asset_class.empty:
                    st.write(f"**{asset_class}**")
                    st.write("No asset")
                else:
                    pie = px.pie(
                        df_asset_class,
                        values="value",
                        names="name",
                        title=asset_class,
                        color_discrete_sequence=px.colors.sequential.dense,
                    )
                    st.plotly_chart(
                        pie,
                        use_container_width=True,
                        use_container_height=True,
                    )


st.header("How to use this app ❓")

st.write(
    "1️⃣ First, add your assets by clicking on the <a href='/Manage_your_assets' target='_self'>**Manage your assets**</a> tab",
    unsafe_allow_html=True,
)

st.write(
    "2️⃣ Then, specify the diversification you want for your assets by clicking on the <a href='/Diversify_your_assets' target='_self'>**Diversify your assets**</a> tab",
    unsafe_allow_html=True,
)

st.write(
    "3️⃣ Finally, you can see the next transactions you need to perform to reach your diversification by clicking on the <a href='/Compute_your_transfers'>**Compute your transfers**</a> tab",
    unsafe_allow_html=True,
)

if assets:
    st.header("Your current assets")
    show_all_assets(assets)

    st.header("Curent asset allocation")
    show_classes_allocation(assets)

    show_assets_allocation(assets)
else:
    st.warning(
        "You don't have any asset yet. Add some by clicking on the **Manage your assets** tab"
    )
