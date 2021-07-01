import numpy as np

from gwp_uncertainties.gwp_computations import compute_substance_agwp_gwp
from gwp_uncertainties.constants import substances_data

def test_delta_gwp():
    table_values, computed_values = [], []
    for substance_name, data in substances_data.items():
        # Extract table values
        agwp20_from_table  = data["AGWP 20"]
        gwp20_from_table   = data["GWP 20"]
        agwp100_from_table = data["AGWP 100"]
        gwp100_from_table  = data["GWP 100"]
        current_table_values = [agwp20_from_table, gwp20_from_table, agwp100_from_table, gwp100_from_table]
        table_values.append(current_table_values)
        # Compute values
        agwp20_computed, gwp20_computed = compute_substance_agwp_gwp(substance_name, time_horizon=20)
        agwp100_computed, gwp100_computed = compute_substance_agwp_gwp(substance_name, time_horizon=100)
        current_computed_values = [agwp20_computed, gwp20_computed, agwp100_computed, gwp100_computed]
        computed_values.append(current_computed_values)

        current_ratio = np.array(current_table_values) / np.array(current_computed_values)
        max_diff = np.max(np.abs(1 - current_ratio))
        if substance_name == "Dinitrogen monoxide":
            assert max_diff < 0.17
        elif substance_name == "Ethane, 1,2-dichloro-":
            assert max_diff < 0.27
        elif substance_name == "Methane, bromo-, Halon 1001":
            assert max_diff < 0.19
        else:
            assert max_diff < 0.06