import pytest
import pandas as pd
import sys
sys.path.append('src')
from option1_flux_entropique import generer_donnees_commerce, calculer_flux_entropique

def test_generation_donnees():
    df = generer_donnees_commerce()
    assert not df.empty
    assert 'flux_entropique_millions_usd' in df.columns
    assert len(df['annee'].unique()) == 7

def test_flux_entropique_calcul():
    df = pd.DataFrame({
        'import_tunisie_france_millions_usd': [100, 200],
        'export_tunisie_france_millions_usd': [80, 150]
    })
    df = calculer_flux_entropique(df)
    assert df['flux_entropique_millions_usd'].iloc[0] == 20
    assert df['flux_entropique_millions_usd'].iloc[1] == 50
EOF
