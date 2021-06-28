import json
from pathlib import Path

DIRPATH = Path(__file__).parent.resolve() / "data"

air_molecular_weight = 28.97      # [kg/kmol], molecular weight of air
atmosphere_total_mass = 5.1352e18  # [kg] total mass of atmosphere

fp_substances = DIRPATH /  "ipcc2013.json"
with open(fp_substances, 'rb') as f:
    substances_data = json.load(f)