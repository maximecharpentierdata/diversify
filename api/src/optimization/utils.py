import numpy as np
from scipy.optimize import LinearConstraint, OptimizeResult, minimize


def find_allocation_statement(
    object_name: str, allocation: list[dict]
) -> dict | None:
    for statement in allocation:
        if statement["object_name"] == object_name:
            return statement


def compute_asset_rate(
    transfer: np.array, assets: list[dict], index: int
) -> float:
    asset = assets[index]
    asset_class = asset["class_name"]
    total_class = np.sum(
        [
            asset["value"] + transfer[i]
            for i, asset in enumerate(assets)
            if asset["class_name"] == asset_class
        ]
    )

    rate = (asset["value"] + transfer[index]) / total_class
    return rate


def compute_asset_class_rate(
    transfer: np.array, assets: list[dict], asset_class: str
) -> float:
    total = np.sum(
        [asset["value"] + transfer[i] for i, asset in enumerate(assets)]
    )
    total_class = np.sum(
        [
            asset["value"] + transfer[i]
            for i, asset in enumerate(assets)
            if asset["class_name"] == asset_class
        ]
    )
    return total_class / total


def compute_assets_score(
    transfer: np.array, assets: list[dict], allocation: list[dict]
) -> float:
    assets_score = 0
    for k in range(len(assets)):
        actual_rate = compute_asset_rate(transfer, assets, k)
        target_rate = find_allocation_statement(assets[k]["name"], allocation)[
            "rate"
        ]
        assets_score += (actual_rate - target_rate) ** 2
    return assets_score


def compute_asset_classes_score(
    transfer: np.array, assets: list[dict], allocation: list[dict]
) -> float:
    asset_classes = set([asset["class_name"] for asset in assets])
    asset_classes_score = 0
    for asset_class in asset_classes:
        actual_rate = compute_asset_class_rate(transfer, assets, asset_class)
        target_rate = find_allocation_statement(asset_class, allocation)[
            "rate"
        ]
        asset_classes_score += (actual_rate - target_rate) ** 2
    return asset_classes_score


def score_function(
    transfer: np.array, assets: list[dict], allocation: list[dict]
) -> float:
    assets_score = compute_assets_score(transfer, assets, allocation)
    asset_classes_score = compute_asset_classes_score(
        transfer, assets, allocation
    )
    return 1000 * (assets_score + asset_classes_score)


def get_asset_index(asset_name: str, assets: list[dict]) -> int | None:
    for i, asset in enumerate(assets):
        if asset["name"] == asset_name:
            return i


def create_optimization_constraints(
    constraints: list[dict], assets: list[dict]
) -> list[LinearConstraint]:
    optimization_constraints = []
    for constraint in constraints:
        matrix = np.zeros((1, len(assets)))
        for asset in constraint["assets"]:
            matrix[0, get_asset_index(asset["asset_name"], assets)] = asset[
                "coef"
            ]

        if constraint["operator"] == "eq":
            optimization_constraints.append(
                LinearConstraint(
                    matrix,
                    lb=constraint["value"],
                    ub=constraint["value"],
                )
            )
        if constraint["operator"] == "leq":
            optimization_constraints.append(
                LinearConstraint(
                    matrix,
                    ub=constraint["value"],
                )
            )
        if constraint["operator"] == "geq":
            optimization_constraints.append(
                LinearConstraint(
                    matrix,
                    lb=constraint["value"],
                )
            )
    return optimization_constraints


def make_amount_constraint(
    total_amount: int, assets: list[dict]
) -> LinearConstraint:
    return LinearConstraint(
        np.ones((1, len(assets))),
        lb=total_amount,
        ub=total_amount,
    )


def make_positive_constraint(assets: list[dict]) -> LinearConstraint:
    return LinearConstraint(
        np.eye(len(assets)),
        lb=0,
    )


def run_optimization(
    assets: list[dict],
    allocation: list[dict],
    constraints: list[dict],
    total_amount: float,
) -> OptimizeResult:
    initial_transfer = np.zeros(len(assets))
    optimization_constraints = create_optimization_constraints(
        constraints, assets
    )
    optimization_constraints.append(
        make_amount_constraint(total_amount, assets)
    )
    optimization_constraints.append(make_positive_constraint(assets))

    res = minimize(
        score_function,
        initial_transfer,
        args=(assets, allocation),
        constraints=optimization_constraints,
    )
    return res


def format_result(
    transfer: np.array, assets: list[dict], allocation: list[dict]
) -> dict:
    asset_transfers = [
        {
            "asset_name": asset["name"],
            "initial_value": asset["value"],
            "transfer_value": transfer[i],
            "new_value": int(asset["value"] + transfer[i]),
            "initial_rate": compute_asset_rate(
                np.zeros(len(assets)), assets, i
            ),
            "new_rate": compute_asset_rate(transfer, assets, i),
            "target_rate": find_allocation_statement(
                asset["name"], allocation
            )["rate"],
        }
        for i, asset in enumerate(assets)
    ]
    unique_classes = set([asset["class_name"] for asset in assets])
    class_rates = [
        {
            "class_name": asset_class,
            "initial_rate": compute_asset_class_rate(
                np.zeros(len(assets)), assets, asset_class
            ),
            "new_rate": compute_asset_class_rate(
                transfer, assets, asset_class
            ),
            "target_rate": find_allocation_statement(asset_class, allocation)[
                "rate"
            ],
        }
        for asset_class in unique_classes
    ]
    return {
        "asset_transfers": asset_transfers,
        "class_rates": class_rates,
    }
