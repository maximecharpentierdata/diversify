import streamlit as st

from utils import (
    make_request,
    update_asset_value,
    load_asset_classes,
    get_class_assets,
)

st.title("Diversify - ➡️ Optimize your transfers")
st.write("*Simple portfolio management app*")


with open("/app/css/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def optimize_transfer(total_amount: int) -> dict | None:
    endpoint = "optimization/"

    params = {"total_amount": total_amount}

    resp = make_request(endpoint, method="GET", data=params)

    if resp.ok:
        st.success("Transfers computed", icon="✅")
        return resp.json()
    else:
        st.error(f"Error computing transfers: {resp.json()}", icon="❌")


def choose_amount_module() -> int:
    total_amount = int(
        st.number_input("Amount to invest", min_value=0.0, value=0.0, step=1.0)
    )
    return total_amount


def show_class_rate(class_rate: dict):
    st.write(f"{class_rate['class_name']}")
    st.write(
        f"{class_rate['initial_rate']*100:.0f} % → "
        f"**{class_rate['new_rate']*100:.0f} %** &nbsp; (🎯 {class_rate['target_rate']*100:.0f} %)",
    )


def show_class_rates(class_rates: list[dict]):
    cols = st.columns(len(class_rates))

    for n, col in enumerate(cols):
        with col:
            show_class_rate(class_rates[n])


def show_asset_transfer(asset_transfer: dict):
    st.write(f"{asset_transfer.get('asset_name')}")
    st.write(
        f"{asset_transfer.get('initial_value')} + <span class='transfer'>"
        f"{asset_transfer.get('transfer_value')}</span> → **{asset_transfer.get('new_value')} €**",
        unsafe_allow_html=True,
    )
    st.write(
        f"{asset_transfer['initial_rate']*100:.0f} % → **{asset_transfer['new_rate']*100:.0f}"
        f" %** &nbsp; (🎯 {asset_transfer['target_rate']*100:.0f} %)",
    )


def show_asset_transfers(asset_transfers: list[dict]):
    n_assets = len(asset_transfers)
    for k in range(0, n_assets, 3):
        cols = st.columns(3)
        for i in range(4):
            try:
                asset_transfer = asset_transfers[k + i]
                with cols[i]:
                    show_asset_transfer(asset_transfer)
            except IndexError:
                pass


def show_transfers(transfers: dict):
    asset_transfers = transfers["asset_transfers"]
    class_rates = transfers["class_rates"]

    st.header("Class final rates")
    show_class_rates(class_rates)

    st.header("Asset transfers")
    for asset_class in load_asset_classes():
        class_assets = [
            asset["name"] for asset in get_class_assets(asset_class)
        ]
        class_asset_transfers = [
            asset_transfer
            for asset_transfer in asset_transfers
            if asset_transfer["asset_name"] in class_assets
        ]
        st.subheader(asset_class)
        show_asset_transfers(class_asset_transfers)


def update_values(asset_transfers: list[dict]):
    for asset in asset_transfers:
        update_asset_value(asset["asset_name"], asset["new_value"])
    st.success("Assets values updated", icon="✅")


total_amount = choose_amount_module()

if st.button("Compute transfers"):
    transfers = optimize_transfer(total_amount)["results"]
    show_transfers(transfers)

    st.button(
        "Update all asset values",
        on_click=update_values,
        args=(transfers["asset_transfers"],),
    )
