from .version import version as __version__
from .gwp_computations import get_uncertain_flows

import bw2data as bd

def add_bw_method_with_gwp_uncertainties(time_horizon=100, verbose=False):

    method = ('IPCC 2013', 'climate change', 'GWP {}a'.format(time_horizon))
    bw_method = bd.Method(method)
    uncertain_method = method + ('uncertain',)
    uncertain_bw_method = bd.Method(uncertain_method)
    try:
        uncertain_bw_method.deregister()
    except:
        pass

    flows_list = get_uncertain_flows(time_horizon=time_horizon, verbose=verbose)

    uncertain_bw_method.register(
        **{
            'unit': bw_method.metadata['unit'],
            'num_cfs': len(flows_list),
            'abbreviation': 'nonexistent',
            'description': 'based on IPCC 2013 method but with uncertainties',
            'filename': 'nonexistent'
        }
    )
    uncertain_bw_method.write(flows_list)

    print("Created BW LCIA method ``{}`` with uncertainties in GWP values".format(uncertain_method))

    return