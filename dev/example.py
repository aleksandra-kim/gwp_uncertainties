import numpy as np
import bw2calc as bc
import bw2data as bd
from gwp_uncertainties import add_bw_method_with_gwp_uncertainties

if __name__ == "__main__":

    time_horizon = 100 # TODO choose

    project = "GSA for protocol paper 3"
    bd.projects.set_current(project)

    add_bw_method_with_gwp_uncertainties(time_horizon, verbose=True)

    co = bd.Database('CH consumption 1.0')
    demand_act = co.search('Food')[0]
    demand = {demand_act: 1}
    print(demand_act)
    method = ('IPCC 2013', 'climate change', 'GWP {}a'.format(time_horizon))
    uncertain_method = method + ('uncertain',)
    # lca = bc.LCA(demand, method)
    # lca.lci()
    # lca.lcia()
    # print("{} LCA score with standard IPCC method".format(lca.score))
    # ulca = bc.LCA(demand, uncertain_method)
    # ulca.lci()
    # ulca.lcia()
    # print("{} LCA score with uncertain IPCC method".format(ulca.score))

    iterations = 100
    mc_certain_gwp = bc.ParallelMonteCarlo(demand, method, iterations)
    lca_scores_certain_gwp = np.array(mc_certain_gwp.calculate())
    print("LCA scores W/O  uncertainties in GWP -> std={}".format(
        np.std(lca_scores_certain_gwp))
    )

    mc_uncertain_gwp = bc.ParallelMonteCarlo(demand, uncertain_method, iterations)
    lca_scores_uncertain_gwp = np.array(mc_uncertain_gwp.calculate())
    print("LCA scores WITH uncertainties in GWP -> std={}".format(
        np.std(lca_scores_uncertain_gwp))
    )
