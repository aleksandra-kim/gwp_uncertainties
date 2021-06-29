import bw2calc as bc
import bw2data as bd
from gwp_uncertainties.gwp_computations import get_uncertain_flows

time_horizon = 100 # TODO choose

project = "GSA for protocol"
bd.projects.set_current(project)

co = bd.Database('CH consumption 1.0')
demand_act = co.search('food sector')[0]
demand = {demand_act: 1}
method = ('IPCC 2013', 'climate change', 'GWP {}a'.format(time_horizon))
print(demand_act)

lca = bc.LCA(demand, method)
lca.lci()
lca.lcia()
print("{} LCA score with standard IPCC method".format(lca.score))

uncertain_flows = get_uncertain_flows(time_horizon=time_horizon)
print(len(uncertain_flows))