import bw2data as bd
import numpy  as  np
from scipy.stats import norm
import stats_arrays as sa


# Local files
from .constants import air_molecular_weight, atmosphere_total_mass, substances_data


def get_uncertain_flows(time_horizon=100):
    method = ('IPCC 2013', 'climate change', 'GWP {}a'.format(time_horizon))
    bw_method = bd.Method(method)

    act_names = {
        bd.get_activity(flow[0])['name'] for flow in bw_method.load()
        if "Carbon dioxide" not in bd.get_activity(flow[0])['name']
           and "Carbon monoxide" not in bd.get_activity(flow[0])['name']
    }

    delta_std_multiplier_dict = {}
    for i,act_name in enumerate(act_names):
        _, delta_std_multiplier_dict[act_name] = compute_delta_std_multiplier(act_name, time_horizon, i + 1)

    flows_list = []
    for flow in bw_method.load():
        act = bd.get_activity(flow[0])
        if 'Carbon dioxide' in act['name']:
            flows_list.append(flow)
        elif 'Carbon monoxide' in act['name']:
            if ', fossil' or ', from soil or biomass stock' in act['name']:
                oxidation = 1.5714
            elif ', non-fossil' in act['name']:
                oxidation = 0
            gwp_nominal = flow[1]
            min_ = 2 + oxidation
            max_ = 3.3 + oxidation
            flow_uncertain = (
                flow[0],  # flow key = (database, code)
                {
                    'amount': gwp_nominal,
                    'minimum': min_,
                    'maximum': max_,
                    'uncertainty type': sa.UniformUncertainty.id,  # assumption from the ipcc report
                }
            )
            flows_list.append(flow_uncertain)
        else:
            try:
                gwp_nominal = flow[1]
                ghg_std = gwp_nominal * delta_std_multiplier_dict[act['name']]
                flow_uncertain = (
                    flow[0],  # flow key = (database, code)
                    {
                        'amount': gwp_nominal,  # static value of gwp
                        'uncertainty type': sa.NormalUncertainty.id,  # assumption from the ipcc report
                        'loc': gwp_nominal,  # mean value that is equal to the static one
                        'scale': ghg_std,  # standard deviation
                    }
                )
                flows_list.append(flow_uncertain)
            except:
                flows_list.append(flow)

    return flows_list


# Conversion from ppbv (part per billion), page 8SM-15
ppbv_to_kg = lambda x_molecular_weight: (air_molecular_weight/x_molecular_weight*1e9/atmosphere_total_mass)


# Compute function f uncertainty given derivatives d = partial_df/partial_dx*delta_x, and normalize
compute_delta_f = lambda nominal_value, *d: np.sqrt(np.sum(np.power(d,2))) / nominal_value


# General expression for AGWP, equation 8.SM.9
#   A    - radiative efficiency, [W/m2/ppb]
#   tau  - lifetime, [yr]
#   H    - time horizon, [yr]
#   mult - multiplier specific to each substance, in many cases is equal to 1
compute_agwp_general  = lambda tau, A, H, mult: A*tau*(1-np.exp(-H/tau)) * mult


# Print computed +-delta_x uncertainty values as percentage of the expected value \bar{x}
# for a 90% confidence interval and its standard deviation
def print_uncertainties(i, x_name, x_delta, x_std):
    if not np.isnan(x_delta):
        print(
            "{:3} {}\n      delta = {:6.3f}%, std = {:5.3f}*mean".format(i, x_name, x_delta*100, x_std)
        )
    else:
        print(
            "{:3} {}\n      NO DATA".format(i, x_name)
        )


# Compute standard deviation x_std given +-delta_x values for confidence interval with a certain confidence level
conf_interval_to_std = lambda conf_level, conf_interval: conf_interval / norm.ppf(0.5 + conf_level / 2)


def compute_co2_agwp(time_horizon):
    # 1. Carbon dioxide, AGWP expression is not general, instead taken from equation 8.SM.23
    # Constants are from Joos et al, 2013, https://doi.org/10.5194/acp-13-2793-2013
    # time_horizon is given in years
    M_co2 = 44.01
    A_co2 = 1.37e-5 * ppbv_to_kg(M_co2)
    delta_A_co2 = 0.1
    if time_horizon==20:
        I_co2 = 14.2
        delta_I_co2 = (16.3-12.2)/2/I_co2
    elif time_horizon==100:
        I_co2 = 52.4
        delta_I_co2 = (65.2-39.5)/2/I_co2
    elif time_horizon==500:
        I_co2 = 184
        delta_I_co2 = (235-132)/2/I_co2
    else:
        print('Choose time horizon of 20, 100 or 500 years')
        return
    co2_agwp     = A_co2*I_co2
    co2_ddelta_A = I_co2*delta_A_co2*A_co2
    co2_ddelta_I = A_co2*delta_I_co2*I_co2
    co2_delta_agwp = compute_delta_f(co2_agwp, co2_ddelta_A, co2_ddelta_I)
    conf_level = 0.9
    co2_std_agwp = conf_interval_to_std(conf_level, co2_delta_agwp)
    return co2_delta_agwp, co2_std_agwp, co2_agwp


# Uncertainty values for AGWP, chapter 8.SM.12, equation 8.SM.24
# delta values for A and tau are taken from table 8.SM.12
compute_gwp          = lambda x_agwp, co2_agwp: x_agwp/co2_agwp
compute_dgwp_dA      = lambda tau, A, H, mult, co2_agwp, delta_A: \
    mult * tau / co2_agwp    * (1 - np.exp(-H/tau)) * delta_A*A
compute_dgwp_dtau    = lambda tau, A, H, mult, co2_agwp, delta_tau: \
    mult *   A / co2_agwp    * (1 - np.exp(-H/tau) - H/tau*np.exp(-H/tau) ) * delta_tau*tau
compute_dgwp_dgwpco2 = lambda x_agwp, co2_agwp, co2_delta_agwp: \
    1 / co2_agwp**2 * x_agwp * co2_delta_agwp*co2_agwp


def compute_delta_std_gwp(tau, A, H, delta_A, delta_tau, mult=1, *dgwp_dy):
    co2_delta_agwp, co2_std_agwp, co2_agwp = compute_co2_agwp(H)
    x_agwp         = compute_agwp_general (tau, A, H, mult)
    x_gwp          = compute_gwp(x_agwp, co2_agwp)
    x_dgwp_dA      = compute_dgwp_dA  (tau, A, H, mult, co2_agwp, delta_A)
    x_dgwp_dtau    = compute_dgwp_dtau(tau, A, H, mult, co2_agwp, delta_tau)
    x_dgwp_dgwpco2 = compute_dgwp_dgwpco2(x_agwp, co2_agwp, co2_delta_agwp)
    x_delta_gwp = compute_delta_f(
        x_gwp,
        x_dgwp_dA,
        x_dgwp_dtau,
        x_dgwp_dgwpco2,
        *dgwp_dy,
    )
    conf_level = 0.9
    x_std_multiplier_gwp = conf_interval_to_std(conf_level, x_delta_gwp)
    return x_delta_gwp, x_std_multiplier_gwp

def get_substance_data(substance_name, time_horizon):
    if substance_name in ["Methane", "Methane, fossil", 'Methane, from soil or biomass stock']:
        # Assume that fossil methane and methane from soil or biomass stock are the same
        # see Bourgault G (2020). Implementation of impact assessment methods in the ecoinvent database version 3.7.1.
        dict_ = substances_data['Methane']
    else:
        dict_ = substances_data[substance_name]
    M = dict_.get("Molecular weight")
    tau = dict_.get("Lifetime")
    A = dict_.get("Radiative efficiency") * ppbv_to_kg(M)
    if substance_name in ['Methane', "Methane, fossil", 'Methane, from soil or biomass stock', "Methane, non-fossil"]:
        # For all CH4 flows
        f1 = dict_.get("f1")  # due to effects on ozone
        f2 = dict_.get("f2")  # due to stratospheric H2O
        mult = 1 + f1 + f2
    elif substance_name=="Dinitrogen monoxide":
        f1 = dict_.get("f1")  # due to effects on ozone
        f2 = dict_.get("f2")  # due to stratospheric H2O
        dict_methane = substances_data["Methane"] # TODO or non-fossil??
        M_ch4 = dict_methane.get("Molecular weight")
        A_ch4 = dict_methane.get("Radiative efficiency") * ppbv_to_kg(M_ch4)
        _, _, co2_agwp = compute_co2_agwp(time_horizon)
        mult = 1 - 0.36 * (1 + f1 + f2) * A_ch4 / A
    else:
        mult = 1
    return tau, A, mult

def compute_substance_agwp_gwp(substance_name, time_horizon):
    co2_delta_agwp, co2_std_agwp, co2_agwp = compute_co2_agwp(time_horizon)
    tau, A, mult = get_substance_data(substance_name, time_horizon)
    x_agwp = compute_agwp_general(tau, A, time_horizon, mult)
    x_gwp = compute_gwp(x_agwp, co2_agwp)
    return x_agwp, x_gwp

def compute_delta_std_multiplier(substance_name, time_horizon, verbose=True, i='-->'):
    try:
        tau, A, mult = get_substance_data(substance_name, time_horizon)
        if substance_name in ["Methane", "Methane, fossil", 'Methane, from soil or biomass stock']:
            # Assume that fossil methane and methane from soil or biomass stock are the same
            # see Bourgault G (2020). Implementation of impact assessment methods in the ecoinvent database version 3.7.1.
            dict_ = substances_data['Methane']
        else:
            dict_ = substances_data[substance_name]
        delta_tau = dict_.get("Lifetime delta", 0.2)
        delta_A = dict_.get("Radiative efficiency delta", 0.1)
        if substance_name in ['Methane', "Methane, fossil", 'Methane, from soil or biomass stock', "Methane, non-fossil"]:
            # For all CH4 flows
            f1 = dict_.get("f1")  # due to effects on ozone
            f2 = dict_.get("f2")  # due to stratospheric H2O
            delta_f1 = dict_.get("delta_f1")
            delta_f2 = dict_.get("delta_f2")
            _, _, co2_agwp = compute_co2_agwp(time_horizon)
            ch4_dgwp_df1 = A * tau / co2_agwp * (1 - np.exp(-time_horizon / tau)) * delta_f1 * f1
            ch4_dgwp_df2 = A * tau / co2_agwp * (1 - np.exp(-time_horizon / tau)) * delta_f2 * f2
            x_delta_gwp, x_std_multiplier_gwp = compute_delta_std_gwp(
                tau, A, time_horizon, delta_A, delta_tau, mult, ch4_dgwp_df1, ch4_dgwp_df2,
            )
        elif substance_name=="Dinitrogen monoxide":
            f1 = dict_.get("f1")  # due to effects on ozone
            f2 = dict_.get("f2")  # due to stratospheric H2O
            delta_f1 = dict_.get("delta_f1")
            delta_f2 = dict_.get("delta_f2")
            dict_methane = substances_data["Methane"]
            M_ch4 = dict_methane.get("Molecular weight")
            A_ch4 = dict_methane.get("Radiative efficiency") * ppbv_to_kg(M_ch4)
            RE_ch4 = A_ch4
            RE_n2o = A
            _, _, co2_agwp = compute_co2_agwp(time_horizon)
            n2o_dgwp_df1 = -0.36 * RE_ch4 / RE_n2o * A * tau / co2_agwp * (1 - np.exp(-time_horizon / tau)) * delta_f1 * f1
            n2o_dgwp_df2 = -0.36 * RE_ch4 / RE_n2o * A * tau / co2_agwp * (1 - np.exp(-time_horizon / tau)) * delta_f2 * f2
            x_delta_gwp, x_std_multiplier_gwp = compute_delta_std_gwp(
                tau, A, time_horizon, delta_A, delta_tau, mult, n2o_dgwp_df1, n2o_dgwp_df2
            )
        else:
            x_delta_gwp, x_std_multiplier_gwp = compute_delta_std_gwp(
                tau, A, time_horizon, delta_A, delta_tau, mult,
            )
        if verbose:
            print_uncertainties(i, substance_name, x_delta_gwp, x_std_multiplier_gwp)
        return x_delta_gwp, x_std_multiplier_gwp
    except:
        if verbose:
            print_uncertainties(i, substance_name, np.nan, np.nan)
        return np.nan, np.nan
