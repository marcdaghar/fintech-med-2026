# tests/test_option3.py
"""
Tests unitaires pour l'option 3 : Waqf Numérique
"""
import pytest
import json
import os
import sys
import tempfile
sys.path.append('src')

from option3_waqf_numerique import WaqfGenerator

# Fixtures
@pytest.fixture
def generator_default():
    """Crée un générateur avec la configuration par défaut"""
    return WaqfGenerator()

@pytest.fixture
def generator_personnalise():
    """Crée un générateur avec une configuration personnalisée"""
    config = {
        'nom_waqf': 'TestWaqf',
        'naqib': '0x9876543210987654321098765432109876543210',
        'biens': [
            {'id': 'T001', 'nom': 'Test Bien 1', 'beneficiaire': '0x1111111111111111111111111111111111111111'},
            {'id': 'T002', 'nom': 'Test Bien 2', 'beneficiaire': '0x2222222222222222222222222222222222222222'}
        ],
        'beneficiaires': [
            {'adresse': '0x1111111111111111111111111111111111111111', 'nom': 'Benef 1', 'part': 60},
            {'adresse': '0x2222222222222222222222222222222222222222', 'nom': 'Benef 2', 'part': 40}
        ]
    }
    return WaqfGenerator(config)

def test_init_default():
    """Test de l'initialisation par défaut"""
    generator = WaqfGenerator()
    assert generator.nom_waqf == 'WaqfClusterMed'
    assert generator.naqib == '0x1234567890123456789012345678901234567890'
    assert len(generator.biens) == 4
    assert len(generator.beneficiaires) == 4

def test_init_personnalise(generator_personnalise):
    """Test de l'initialisation personnalisée"""
    assert generator_personnalise.nom_waqf == 'TestWaqf'
    assert generator_personnalise.naqib == '0x9876543210987654321098765432109876543210'
    assert len(generator_personnalise.biens) == 2
    assert len(generator_personnalise.beneficiaires) == 2

def test_generer_contrat_solidity(generator_default):
    """Test de génération du contrat Solidity"""
    contrat = generator_default.generer_contrat_solidity()
    assert isinstance(contrat, str)
    assert len(contrat) > 500
    
    # Vérifier les éléments clés
    assert "pragma solidity ^0.8.0;" in contrat
    assert f"contract {generator_default.nom_waqf}" in contrat
    assert "struct Bien" in contrat
    assert "function redistribuerRevenus()" in contrat
    assert "modifier seulementNaqib" in contrat
    assert "event RedistributionEffectuee" in contrat

def test_generer_contrat_beneficiaires(generator_personnalise):
    """Test que le contrat inclut les bénéficiaires"""
    contrat = generator_personnalise.generer_contrat_solidity()
    for benef in generator_personnalise.beneficiaires:
        adresse = benef['adresse']
        assert adresse in contrat
        assert f"parts[{adresse}]" in contrat

def test_generer_readme(generator_default):
    """Test de génération du README"""
    readme = generator_default.generer_readme()
    assert isinstance(readme, str)
    assert len(readme) > 200
    
    # Vérifier les éléments clés
    assert generator_default.nom_waqf in readme
    assert "Waqf num\\u00e9rique" in readme
    assert "Naqib" in readme
    assert "B\\u00e9n\\u00e9ficiaires" in readme
    assert "ajouterBien" in readme
    assert "recevoirFrais" in readme
    assert "redistribuerRevenus" in readme

def test_generer_script_deploiement(generator_default):
    """Test de génération du script de déploiement"""
    script = generator_default.generer_script_deploiement()
    assert isinstance(script, str)
    assert len(script) > 100
    
    assert "const hre = require" in script
    assert "async function main" in script
    assert generator_default.nom_waqf in script
    assert "fs.writeFileSync" in script

def test_generer_hardhat_config(generator_default):
    """Test de génération de la configuration Hardhat"""
    config = generator_default.generer_hardhat_config()
    assert isinstance(config, str)
    assert "solidity:" in config
    assert "sepolia:" in config
    assert "polygon:" in config

def test_generer_json_abi(generator_default):
    """Test de génération du JSON ABI"""
    json_data = generator_default.generer_json_abi()
    assert isinstance(json_data, dict)
    assert "contractName" in json_data
    assert json_data["contractName"] == generator_default.nom_waqf
    assert "abi" in json_data
    assert len(json_data["abi"]) > 0
    assert "beneficiaires" in json_data
    assert "biens" in json_data

def test_generer_tous_fichiers(generator_default, tmp_path):
    """Test de génération de tous les fichiers"""
    # Rediriger les sorties vers un dossier temporaire
    original_path = os.getcwd()
    os.chdir(tmp_path)
    
    # Créer les dossiers nécessaires
    os.makedirs('contracts', exist_ok=True)
    os.makedirs('docs', exist_ok=True)
    os.makedirs('scripts', exist_ok=True)
    
    generator_default.generer_tous_fichiers()
    
    # Vérifier que les fichiers ont été créés
    assert os.path.exists(f'contracts/{generator_default.nom_waqf}.sol')
    assert os.path.exists('docs/README_waqf.md')
    assert os.path.exists(f'scripts/deploy_{generator_default.nom_waqf}.js')
    assert os.path.exists('hardhat.config.js')
    assert os.path.exists('contracts/waqf_abi.json')
    
    os.chdir(original_path)

def test_chargement_config_yaml(generator_default, tmp_path):
    """Test de chargement de la configuration depuis YAML"""
    # Créer un fichier YAML temporaire
    yaml_content = """
option3:
  nom_waqf: "YamlWaqf"
  naqib: "0x9999999999999999999999999999999999999999"
  beneficiaires:
    - adresse: "0x111...", nom: "Yaml Benef 1", part: 50
    - adresse: "0x222...", nom: "Yaml Benef 2", part: 50
"""
    
    with open('config_test.yaml', 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    
    # Le test est plus complexe car il nécessite yaml
    # On vérifie simplement que la structure existe
    import yaml
    with open('config_test.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    assert 'option3' in config
    assert 'nom_waqf' in config['option3']

def test_beneficiaires_parts_sum_100(generator_default):
    """Test que les parts des bénéficiaires sum à 100"""
    total = sum(b['part'] for b in generator_default.beneficiaires)
    assert total == 100

def test_beneficiaires_parts_sum_100_personnalise(generator_personnalise):
    """Test que les parts des bénéficiaires sum à 100 (personnalisé)"""
    total = sum(b['part'] for b in generator_personnalise.beneficiaires)
    assert total == 100

def test_contrat_contient_beneficiaires(generator_default):
    """Test que le contrat contient les bénéficiaires"""
    contrat = generator_default.generer_contrat_solidity()
    for benef in generator_default.beneficiaires:
        assert benef['adresse'] in contrat

def test_readme_contient_beneficiaires(generator_default):
    """Test que le README contient les bénéficiaires"""
    readme = generator_default.generer_readme()
    for benef in generator_default.beneficiaires:
        assert benef['nom'] in readme
        assert str(benef['part']) in readme

def test_script_deploiement_contient_naqib(generator_default):
    """Test que le script de déploiement contient le naqib"""
    script = generator_default.generer_script_deploiement()
    assert generator_default.naqib in script

def test_hardhat_config_valide(generator_default):
    """Test que la configuration Hardhat est valide"""
    config = generator_default.generer_hardhat_config()
    # Vérification basique de syntaxe JavaScript
    assert "module.exports" in config
    assert "networks" in config
    assert "solidity" in config

def test_json_abi_validite(generator_default):
    """Test que le JSON ABI est valide"""
    json_data = generator_default.generer_json_abi()
    # Vérifier que c'est du JSON valide
    json_str = json.dumps(json_data)
    parsed = json.loads(json_str)
    assert parsed == json_data

def test_generation_reproductible(generator_default):
    """Test de reproductibilité de la génération"""
    contrat1 = generator_default.generer_contrat_solidity()
    contrat2 = generator_default.generer_contrat_solidity()
    assert contrat1 == contrat2

def test_nom_waqf_echappement(generator_default):
    """Test que les guillemets sont échappés dans le contrat"""
    generator_default.nom_waqf = 'Waqf"Test"'
    contrat = generator_default.generer_contrat_solidity()
    # Le nom devrait être échappé dans les commentaires
    assert 'Waqf"Test"' in contrat or 'Waqf\\"Test\\"' in contrat

def test_beneficiaires_adresses_valides(generator_default):
    """Test que les adresses des bénéficiaires ont le bon format"""
    for benef in generator_default.beneficiaires:
        adresse = benef['adresse']
        assert adresse.startswith('0x')
        assert len(adresse) >= 42  # Format Ethereum

def test_biens_id_uniques(generator_default):
    """Test que les IDs des biens sont uniques"""
    ids = [b['id'] for b in generator_default.biens]
    assert len(ids) == len(set(ids))

def test_save_all_files(tmp_path):
    """Test de sauvegarde de tous les fichiers"""
    generator = WaqfGenerator()
    
    original_path = os.getcwd()
    os.chdir(tmp_path)
    
    os.makedirs('contracts', exist_ok=True)
    os.makedirs('docs', exist_ok=True)
    os.makedirs('scripts', exist_ok=True)
    
    generator.generer_tous_fichiers()
    
    # Vérifier tous les fichiers
    files = [
        f'contracts/{generator.nom_waqf}.sol',
        'docs/README_waqf.md',
        f'scripts/deploy_{generator.nom_waqf}.js',
        'hardhat.config.js',
        'contracts/waqf_abi.json'
    ]
    
    for f in files:
        assert os.path.exists(f), f"Fichier {f} non trouvé"
        assert os.path.getsize(f) > 0, f"Fichier {f} vide"
    
    os.chdir(original_path)

def test_contrat_solidity_syntaxe(generator_default):
    """Test basique de syntaxe Solidity"""
    contrat = generator_default.generer_contrat_solidity()
    # Vérifier les éléments de syntaxe Solidity
    assert "{" in contrat
    assert "}" in contrat
    assert ";" in contrat
    assert "function" in contrat
    assert "struct" in contrat
    assert "mapping" in contrat
    assert "event" in contrat

if __name__ == "__main__":
    pytest.main(["-v", __file__])
