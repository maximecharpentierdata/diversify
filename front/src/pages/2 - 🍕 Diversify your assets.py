import requests
import streamlit as st

from utils import fetch_assets, load_asset_classes, make_request


st.title("Diversify - 🍕 Diversify your assets")
st.write("*Simple portfolio management app*")


def get_rate(object_name: str) -> float | None:
    endpoint = f"allocation/find/{object_name}"

    r = make_request(endpoint, method="GET").json()

    if r:
        return r["rate"]


def save_rate(allocation: dict):
    url = "allocation/"
    data = {"allocation": allocation}

    r = make_request(url, method="POST", data=data)

    if r.ok:
        st.success("Allocation saved", icon="✅")
    else:
        st.error(f"Error saving allocation: {allocation, r.json()}", icon="❌")


def make_classes_allocation():
    classes = load_asset_classes()

    st.subheader("Set your asset classes")

    new_allocation = []

    cols = st.columns(len(classes))
    for i in range(len(cols)):
        with cols[i]:
            asset_class = classes[i]
            st.write(f"**{asset_class}**")
            current_rate = get_rate(asset_class)
            if current_rate is not None:
                st.write(
                    f"*Current target allocation*: {current_rate*100:.0f} %"
                )
            new_rate = (
                st.slider(
                    "Allocation",
                    min_value=0,
                    max_value=100,
                    step=1,
                    key=f"{asset_class}_rate",
                )
                / 100
            )
            new_allocation.append(
                {
                    "object_type": "asset_class",
                    "object_name": asset_class,
                    "rate": new_rate,
                }
            )

    if sum([statement["rate"] for statement in new_allocation]) != 1:
        st.error("Allocation must sum to 1")
    else:
        st.success("Allocation is valid")
        st.button(
            "Save allocation",
            on_click=save_rate,
            args=(new_allocation,),
        )


def make_assets_allocation():
    st.subheader("Set your assets")

    assets = fetch_assets()

    if not assets:
        st.warning("No assets found")
    else:
        classes = load_asset_classes()

        all_good = []

        for asset_class in classes:
            st.write(f"**{asset_class}**")
            class_assets = [
                asset for asset in assets if asset["class_name"] == asset_class
            ]
            if class_assets:
                cols = st.columns(len(class_assets))
                for i in range(len(cols)):
                    with cols[i]:
                        asset = class_assets[i]
                        st.write(f"**{asset['name']}**")
                        current_rate = get_rate(asset["name"])
                        if current_rate is not None:
                            st.write(
                                f"*Current allocation*: {current_rate*100:.0f} %"
                            )

                        if not "rate" in asset:
                            if current_rate is not None:
                                asset["rate"] = current_rate
                            else:
                                asset["rate"] = 0

                        new_rate = (
                            st.slider(
                                "Allocation",
                                min_value=0,
                                max_value=100,
                                step=1,
                                key=f"{asset_class}_{asset['name']}_rate",
                            )
                            / 100
                        )
                        asset["rate"] = new_rate
                allocation = [
                    {
                        "object_type": "asset",
                        "object_name": asset["name"],
                        "rate": asset["rate"],
                    }
                    for asset in class_assets
                ]
                if sum([statement["rate"] for statement in allocation]) != 1:
                    st.error("Allocation must sum to 1")
                    all_good.append(False)
                else:
                    st.success("Allocation is valid")
                    st.button(
                        "Save allocation",
                        on_click=save_rate,
                        args=(allocation,),
                        key=f"{asset_class}_save",
                    )
                    all_good.append(True)

        if all(all_good):
            allocation = [
                {
                    "object_type": "asset",
                    "object_name": asset["name"],
                    "rate": asset["rate"],
                }
                for asset in assets
            ]

            st.button(
                "Save all allocations",
                on_click=save_rate,
                args=(allocation,),
                key="save_all",
            )


with st.expander("Manage your asset classes"):
    make_classes_allocation()


with st.expander("Manage your assets"):
    make_assets_allocation()
