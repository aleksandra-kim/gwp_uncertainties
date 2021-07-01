from gwp_uncertainties.gwp_computations import compute_delta_std_multiplier

def test_delta_gwp():
    time_horizons = [20, 100]

    # Following data is taken from Table 8.SM.14
    table_data_delta_gwp = {
        "Methane": {
            20: 30,
            100: 39,
        },
        "Methane, fossil": {
            20: 30,
            100: 39,
        },
        "Methane, from soil or biomass stock": {
            20: 30,
            100: 39,
        },
        "Methane, non-fossil": {
            20: 30,
            100: 39,
        },
        "Dinitrogen monoxide": {
            20: 21,
            100: 29,
        },
        "Methane, trichlorofluoro-, CFC-11": {
            20: 21,
            100: 33,
        },
        "Methane, dichlorodifluoro-, CFC-12": {
            20: 20,
            100: 31,
        },
        "Ethane, 1,1,1,2-tetrafluoro-, HFC-134a": {
            20: 23,
            100: 33,
        },
    }

    for substance_name, data in table_data_delta_gwp.items():
        for time_horizon in time_horizons:
            delta_from_table = data[time_horizon]
            delta_computed, _  =  compute_delta_std_multiplier(substance_name, time_horizon, verbose=False)
            assert delta_from_table == round(delta_computed*100)