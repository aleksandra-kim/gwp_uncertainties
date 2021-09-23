import numpy as np
import pickle
from pathlib import Path
import bw2calc as bc
import bw2data as bd
from gwp_uncertainties import add_bw_method_with_gwp_uncertainties
import plotly.graph_objects as go
import stats_arrays as sa
from plotly.subplots import make_subplots
from dev.utils_paper_plotting import *
from decimal import Decimal

show_figure = False
save_figure = True

path_base = Path(
"/Users/akim/PycharmProjects/gsa-framework-master/dev/write_files/"
)
write_dir = path_base / "protocol_gsa"
write_dir_arr = write_dir / "arrays"
write_dir_fig = write_dir / "figures"

fig_format = ["pdf", "svg"]
num_bins = 60
color = color_darkgray_hex


time_horizon = 100 # TODO choose

project = "GSA for protocol"
bd.projects.set_current(project)

# add_bw_method_with_gwp_uncertainties(time_horizon, verbose=True)

co = bd.Database('CH consumption 1.0')
# demand_act = co.search('food sector')[0]
# demand = {demand_act: 1}
# print(demand_act)
method = ('IPCC 2013', 'climate change', 'GWP {}a'.format(time_horizon))
uncertain_method = method + ('uncertain',)
bw_uncertain_method = bd.Method(uncertain_method)

all_flows = bw_uncertain_method.load()
uncertain_flows = []
inds = []
for i,flow in enumerate(all_flows):
    try:
        flow[1].get('uncertainty type')
        flow_name = bd.get_activity(flow[0])['name']
        if flow_name not in uncertain_flows:
            uncertain_flows.append(flow_name)
            inds.append(i)
    except:
        pass
# unique_uncertain_flows = set(uncertain_flows)
flows_uncertain_list = [all_flows[i] for i in inds]

def format_value(dict, dict_key):
    if dict_key == "uncertainty type":
        value = dict.get(dict_key)
        if value == sa.NormalUncertainty.id:
            value_str = "$\mathcal{N}$"
        elif value == sa.LognormalUncertainty.id:
            value_str = "$Log\mathcal{N}$"
        elif value == sa.UniformUncertainty.id:
            value_str = "\mathcal{U}$"
    else:
        value = dict.get(dict_key, None)
        if value is not None:
            value_str = '%.2e' % Decimal(value)
            value_str = value_str.replace("+0", "")
            value_str = value_str.replace("-0", "-")
        else:
            value_str = "--"
    return value_str

for flow in flows_uncertain_list:
    flow_name = bd.get_activity(flow[0])['name']
    data = flow[1]
    gwp = format_value(data, "amount")
    uct = format_value(data, "uncertainty type")
    min_ = format_value(data, "minimum")
    max_ = format_value(data, "maximum")
    std = format_value(data, "scale")
    print("{} & & {} & {} & {} & {} & {} \\\\".format(flow_name, gwp, uct, std, min_, max_))

opacity = 0.65
iterations = 2000

np.random.seed(23423)

if save_figure or show_figure:
    ncols = 5
    nrows = 8
    flow_names = []
    i = 0
    for flow in flows_uncertain_list:
        flow_name = bd.get_activity(flow[0])['name']
        flow_names.append(flow_name)

    flow_names_short = {
        'Carbon monoxide, fossil': r"$\text{1. CO, fossil}$",
        'Carbon monoxide, from soil or biomass stock': r"$\text{2. CO, from soil}$",
        'Carbon monoxide, non-fossil': r"$\text{3. CO, non-fossil}$",
        'Chloroform': r"$\text{4. CHCl}_3$",
        'Dinitrogen monoxide': r"$\text{5. N}_2\text{O}$",
        'Ethane, 1,1,1,2-tetrafluoro-, HFC-134a': r"$\text{6. HFC-134a}$",
        'Ethane, 1,1,1-trichloro-, HCFC-140': r"$\text{7. HCFC-140}$",
        'Ethane, 1,1,1-trifluoro-, HFC-143a': r"$\text{8. HFC-143a}$",
        'Ethane, 1,1,2-trichloro-1,2,2-trifluoro-, CFC-113': r"$\text{9. CFC-113}$",
        'Ethane, 1,1-dichloro-1-fluoro-, HCFC-141b': r"$\text{10. HCFC-141b}$",
        'Ethane, 1,1-difluoro-, HFC-152a': r"$\text{11. HFC-152a}$",
        'Ethane, 1,2-dichloro-': r"$\text{12. CH}_2\text{ClCH}_2\text{Cl}$",
        'Ethane, 1,2-dichloro-1,1,2,2-tetrafluoro-, CFC-114': r"$\text{13. CFC-114}$",
        'Ethane, 1-chloro-1,1-difluoro-, HCFC-142b': r"$\text{14. HCFC-142b}$",
        'Ethane, 2,2-dichloro-1,1,1-trifluoro-, HCFC-123': r"$\text{15. HCFC-123}$",
        'Ethane, 2-chloro-1,1,1,2-tetrafluoro-, HCFC-124': r"$\text{16. HCFC-124}$",
        'Ethane, chloropentafluoro-, CFC-115': r"$\text{17. CFC-115}$",
        'Ethane, hexafluoro-, HFC-116': r"$\text{18. HFC-116}$",
        'Ethane, pentafluoro-, HFC-125': r"$\text{19. HFC-125}$",
        'Methane': r"$\text{20. CH}_4$",
        'Methane, bromo-, Halon 1001': r"$\text{21. Halon 1001}$",
        'Methane, bromochlorodifluoro-, Halon 1211': r"$\text{22. Halon 1211}$",
        'Methane, bromotrifluoro-, Halon 1301': r"$\text{23. Halon 1301}$",
        'Methane, chlorodifluoro-, HCFC-22': r"$\text{24. HCFC-22}$",
        'Methane, chlorotrifluoro-, CFC-13': r"$\text{25. CFC-13}$",
        'Methane, dichloro-, HCC-30': r"$\text{26. HCC-30}$",
        'Methane, dichlorodifluoro-, CFC-12': r"$\text{27. CFC-12}$",
        'Methane, dichlorofluoro-, HCFC-21': r"$\text{28. HCFC-21}$",
        'Methane, difluoro-, HFC-32': r"$\text{29. HFC-32}$",
        'Methane, fossil': r"$\text{30. CH}_4\text{, fossil}$",
        'Methane, from soil or biomass stock': r"$\text{31. CH}_4\text{, from soil}$",
        'Methane, monochloro-, R-40': r"$\text{32. R-40}$",
        'Methane, non-fossil': r"$\text{33. CH}_4\text{, non-fossil}$",
        'Methane, tetrachloro-, R-10': r"$\text{34. R-10}$",
        'Methane, tetrafluoro-, R-14': r"$\text{35. R-14}$",
        'Methane, trichlorofluoro-, CFC-11': r"$\text{36. CFC-11}$",
        'Methane, trifluoro-, HFC-23': r"$\text{37. HFC-23}$",
        'Nitrogen fluoride': r"$\text{38. NF}_3$",
        'Perfluoropentane': r"$\text{39. n-C}_5\text{F}_{12}$",
        'Sulfur hexafluoride': r"$\text{40. SF}_6$",
    }

    flow_ticks = {
        'Dinitrogen monoxide': {
            "tickvals": [200, 300],
            "ticktext": ['200', '300'],
        },
        'Ethane, 1,1,1,2-tetrafluoro-, HFC-134a': {
            "tickvals": [800, 1600],
            "ticktext": ["800", "1'600"],
        },
        'Ethane, 1,1,1-trichloro-, HCFC-140': {
            "tickvals": [100, 200],
            "ticktext": ["100", "200"],
        },
        'Ethane, 1,1,1-trifluoro-, HFC-143a': {
            "tickvals": [3000, 6000],
            "ticktext": ["3'000", "6'000"],
        },
        'Ethane, 1,1,2-trichloro-1,2,2-trifluoro-, CFC-113': {
            "tickvals": [4000, 7000],
            "ticktext": ["4'000", "7'000"],
        },
        'Ethane, 1,1-dichloro-1-fluoro-, HCFC-141b': {
            "tickvals": [500, 1000],
            "ticktext": ["500", "1'000"],
        },
        'Ethane, 1,1-difluoro-, HFC-152a': {
            "tickvals": [100, 200],
            "ticktext": ["100", "200"],
        },
        'Ethane, 1,2-dichloro-1,1,2,2-tetrafluoro-, CFC-114': {
            "tickvals": [6000, 10000],
            "ticktext": ["6'000", "10'000"],
        },
        'Ethane, 1-chloro-1,1-difluoro-, HCFC-142b': {
            "tickvals": [1500, 2500],
            "ticktext": ["1'500", "2'500"],
        },
        'Ethane, chloropentafluoro-, CFC-115': {
            "tickvals": [6000, 10000],
            "ticktext": ["6'000", "10'000"],
        },
        'Ethane, hexafluoro-, HFC-116': {
            "tickvals": [7000, 14000],
            "ticktext": ["7'000", "14'000"],
        },
        'Ethane, pentafluoro-, HFC-125': {
            "tickvals": [2000, 4000],
            "ticktext": ["2'000", "4'000"],
        },
        'Methane, bromochlorodifluoro-, Halon 1211': {
            "tickvals": [1000, 2000],
            "ticktext": ["1'000", "2'000"],
        },
        'Methane, bromotrifluoro-, Halon 1301': {
            "tickvals": [4000, 8000],
            "ticktext": ["4'000", "8'000"],
        },
        'Methane, chlorodifluoro-, HCFC-22': {
            "tickvals": [1000, 2000],
            "ticktext": ["1'000", "2'000"],
        },
        'Methane, chlorotrifluoro-, CFC-13': {
            "tickvals": [10000, 18000],
            "ticktext": ["10'000", "18'000"],
        },
        'Methane, dichlorodifluoro-, CFC-12': {
            "tickvals": [7000, 14000],
            "ticktext": ["7'000", "14'000"],
        },
        'Methane, dichlorofluoro-, HCFC-21': {
            "tickvals": [100, 200],
            "ticktext": ["100", "200"],
        },
        'Methane, difluoro-, HFC-32': {
            "tickvals": [500, 1000],
            "ticktext": ["500", "1'000"],
        },
        'Methane, tetrachloro-, R-10': {
            "tickvals": [1000, 2000],
            "ticktext": ["1'000", "2'000"],
        },
        'Methane, tetrafluoro-, R-14': {
            "tickvals": [4000, 8000],
            "ticktext": ["4'000", "8'000"],
        },
        'Methane, trichlorofluoro-, CFC-11': {
            "tickvals": [3000, 6000],
            "ticktext": ["3'000", "6'000"],
        },
        'Methane, trifluoro-, HFC-23': {
            "tickvals": [8000, 16000],
            "ticktext": ["8'000", "16'000"],
        },
        'Nitrogen fluoride': {
            "tickvals": [10000, 20000],
            "ticktext": ["10'000", "20'000"],
        },
        'Perfluoropentane': {
            "tickvals": [6000, 10000],
            "ticktext": ["6'000", "10'000"],
        },
        'Sulfur hexafluoride': {
            "tickvals": [15000, 30000],
            "ticktext": ["15'000", "30'000"],
        },
    }

    flow_names_plot = [flow_names_short[n] for n in flow_names]

    fig = make_subplots(
        rows=nrows, cols=ncols,
        subplot_titles=flow_names_plot,
        horizontal_spacing=0.08,
        vertical_spacing=0.08,
    )

    i = 0
    for row in range(1,nrows+1):
        for col in range(1,ncols+1):
            flow = flows_uncertain_list[i]
            flow_name = bd.get_activity(flow[0])['name']
            if flow[1]['uncertainty type'] == sa.NormalUncertainty.id:
                x = np.random.normal(flow[1]['loc'], flow[1]['scale'], iterations)
            elif flow[1]['uncertainty type'] == sa.UniformUncertainty.id:
                x = (flow[1]['maximum'] - flow[1]['minimum'])*np.random.rand(iterations) + flow[1]['minimum']
            bin_min = min(x)
            bin_max = max(x)
            bins_ = np.linspace(bin_min, bin_max, num_bins, endpoint=True)
            freq, bins = np.histogram(x, bins=bins_)
            fig.add_trace(
                go.Scatter(
                    x=bins,
                    y=freq,
                    opacity=opacity,
                    line=dict(color=color, width=1, shape="hvh"),
                    showlegend=False,
                    fill="tozeroy",
                ),
                row=row,
                col=col,
            )
            if flow_name in flow_ticks:
                fig.update_xaxes(
                    tickvals=flow_ticks[flow_name]['tickvals'],
                    ticktext=flow_ticks[flow_name]['ticktext'],
                    row=row,
                    col=col,
                )
            i += 1
            # Both
    fig.update_xaxes(title_text="GWP, [kg CO2-eq]", row=nrows, title_standoff=25,)
    fig.update_yaxes(title_text="Frequency", col=1, title_standoff=25,)
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor=color_gray_hex,
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor=color_gray_hex,
        showline=True,
        linewidth=1,
        linecolor=color_gray_hex,
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor=color_gray_hex,
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor=color_black_hex,
        showline=True,
        linewidth=1,
        linecolor=color_gray_hex,
    )
    fig.update_layout(
        width=ncols*180,
        height=nrows*120,
        paper_bgcolor="rgba(255,255,255,1)",
        plot_bgcolor="rgba(255,255,255,1)",
        legend=dict(
            x=0.85,
            y=1.2,
            orientation="v",
            xanchor="center",
            font=dict(size=14),
            # bgcolor=color_lightgray_hex,
            bordercolor=color_darkgray_hex,
            borderwidth=1,
        ),
        margin=dict(l=0, r=0, t=20, b=0),
    )
    if show_figure: fig.show()
    if save_figure: save_fig(fig, "gwp_uncertainty", fig_format, write_dir_fig)



print()