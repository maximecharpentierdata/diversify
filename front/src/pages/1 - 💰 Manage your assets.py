import streamlit as st

from utils import (
    delete_asset,
    format_currency,
    get_class_assets,
    load_asset_classes,
    save_asset,
    update_asset_value,
)


st.title("Diversify - 💰 Manage your assets")
st.write("*Simple portfolio management app*")


def add_asset_page():
    st.write("Specify the asset details below:")
    asset_class = st.selectbox(
        "Asset class", load_asset_classes(), key="add-class"
    )
    asset_name = st.text_input("Asset name", key="add-name")
    asset_value = st.number_input(
        "Asset value", min_value=0.0, value=0.0, key="add-value"
    )

    st.button(
        "Save asset",
        on_click=save_asset,
        args=(asset_class, asset_name, asset_value),
    )


def update_asset_value_page():
    st.write("Specify the asset details below:")
    asset_class = st.selectbox(
        "Asset class", load_asset_classes(), key="update-class"
    )

    assets = get_class_assets(asset_class)

    if not assets:
        st.warning("No assets found for this class")
    else:
        asset = st.selectbox(
            "Asset name",
            assets,
            key="update-name",
            format_func=lambda x: x["name"],
        )

        if asset_class and asset:
            st.success(
                f"Current asset value: **{format_currency(asset.get('value'))}**"
            )

        st.write("Specify the new asset value below:")
        asset_value = st.number_input(
            "New Asset value", min_value=0.0, value=0.0, key="update-value"
        )

        st.button(
            "Update asset value",
            on_click=update_asset_value,
            args=(asset["name"], asset_value),
        )


def delete_asset_page():
    st.write("Specify the asset details below:")
    asset_class = st.selectbox(
        "Asset class", load_asset_classes(), key="delete-class"
    )
    assets = get_class_assets(asset_class)

    if not assets:
        st.warning("No assets found for this class")
    else:
        asset = st.selectbox(
            "Asset name",
            assets,
            key="delete-name",
            format_func=lambda x: x["name"],
        )

        st.button(
            "Delete asset",
            on_click=delete_asset,
            args=(asset["name"],),
        )


with st.expander("Add asset"):
    add_asset_page()

with st.expander("Update asset value"):
    update_asset_value_page()

with st.expander("Delete asset"):
    delete_asset_page()
