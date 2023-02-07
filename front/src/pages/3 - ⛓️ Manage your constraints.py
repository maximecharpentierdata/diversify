import time

import streamlit as st

from utils import (
    fetch_assets,
    get_class_assets,
    load_asset_classes,
    make_request,
)


st.title("Diversify - ⛓️ Manage your constraints")
st.write("*Simple portfolio management app*")


def show_constraint(constraint: dict):
    out_string = show_constrainted_assets(constraint["assets"])
    if constraint["operator"] == "eq":
        operator = "$=$"
    else:
        operator = f"$\{constraint['operator']}$"
    st.write(out_string + f"{operator} {constraint['value']}")


def delete_constraint(constraint_id: dict):
    endpoint = f"constraints/{constraint_id['$oid']}"

    r = make_request(endpoint, method="DELETE")

    if r.ok:
        st.success("Constraint deleted", icon="✅")
    else:
        st.error("Error deleting constraint", icon="❌")


def show_constraints():
    endpoint = "constraints/"

    r = make_request(endpoint, method="GET")

    constraints = r.json()

    if constraints:
        for constraint in constraints:
            col1, col2 = st.columns([3, 1])
            with col1:
                show_constraint(constraint)
            with col2:
                st.button(
                    "Delete constraint",
                    key=f"delete_{constraint['_id']}",
                    on_click=delete_constraint,
                    args=(constraint["_id"],),
                )
    else:
        st.warning("No constraints added yet")


def upload_constraint(constraint: dict):
    endpoint = "constraints/"

    data = constraint

    r = make_request(endpoint, method="PUT", data=data)

    if r.ok:
        st.success("Constraint saved", icon="✅")
    else:
        st.error(f"Error saving constraint: {r.json()}", icon="❌")

    time.sleep(2)
    st.session_state["constrainted_assets"] = []
    st.session_state["finished"] = False


def show_constrainted_assets(constrainted_assets: list[dict]) -> str:
    if not constrainted_assets:
        st.warning("No assets added yet")
    else:
        out_string = " - "
        for asset in constrainted_assets:
            if asset["coef"] > 0:
                out_string += rf"\+ **{abs(asset['coef'])}** $\times$ *({asset['asset_name']})* &nbsp;"

            else:
                out_string += rf"\- **{abs(asset['coef'])}** $\times$ *({asset['asset_name']})* &nbsp;"
        return out_string


def add_constrainted_asset(
    constrainted_assets: list[dict], classes: list[str], index: int
):
    st.write("Choose your asset class")
    asset_class = st.selectbox(
        "Asset class",
        classes,
        key=f"asset_class_{index}",
    )
    class_assets = get_class_assets(asset_class)
    asset = st.selectbox(
        "Asset",
        class_assets,
        key=f"asset_{index}",
        format_func=lambda x: x["name"],
    )
    coef = st.number_input(
        "Coefficient",
        key=f"coef_{index}",
    )
    if coef == 0:
        st.warning("Coefficient cannot be 0")
    else:
        if st.button(
            "Add asset",
            key=f"add_asset_{index}",
        ):
            constrainted_asset = {
                "asset_name": asset["name"],
                "coef": coef,
            }
            constrainted_assets.append(constrainted_asset)
            st.success("Asset added")
            index += 1


def finish():
    st.session_state["finished"] = True


def add_constraint_module():
    assets = fetch_assets()
    classes = load_asset_classes()

    if not assets:
        st.warning("No assets found, please add some first")
    else:
        index = 0
        if "constrainted_assets" not in st.session_state:
            st.session_state["constrainted_assets"] = []

        if "finished" not in st.session_state:
            st.session_state["finished"] = False

        if (
            not st.session_state["constrainted_assets"]
            or not st.session_state["finished"]
        ):
            add_constrainted_asset(
                st.session_state["constrainted_assets"], classes, index
            )
            st.button("Done", on_click=finish)
        else:
            st.write(
                show_constrainted_assets(
                    st.session_state["constrainted_assets"]
                )
            )
            operators = {
                "Less than or equal to": "leq",
                "Greater than or equal to": "geq",
                "Equal to": "eq",
            }
            operator = st.selectbox("Operator", operators.keys())
            value = st.number_input("Value")

            constraint = {
                "assets": st.session_state["constrainted_assets"],
                "operator": operators[operator],
                "value": value,
            }

            st.write("Your final constraint")
            show_constraint(constraint)

            st.button(
                "Save constraint",
                on_click=upload_constraint,
                args=(constraint,),
            )


st.subheader("Your constraints")
show_constraints()

st.subheader("Add a new constraint")
add_constraint_module()
