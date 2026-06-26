
```python
# tests/test_option2.py
"""
Tests unitaires pour l'option 2 : Transport optimal
"""
import pytest
import numpy as np
import sys
import os
sys.path.append('src')

from option2_logistique_villani import Port, VillaniLogistics

# Fixtures
@pytest.fixture
def ports_standard():
    """Crée des ports de test standard"""
    return [
        Port("Marseille", 43.3, 5.4, 0.4, 0.25),
        Port("Bizerte", 37.3, 9.9, 0.2, 0.35),
        Port("Istanbul", 41.0, 29.0, 0.25, 0.2),
        Port("Odessa", 46.5, 30.7, 0.15, 0.2)
    ]

@pytest.fixture
def ports_2():
    """Crée 2 ports pour les tests simples"""
    return [
        Port("A", 0, 0, 0.5, 0.5),
        Port("B", 10, 0, 0.5, 0.5)
    ]

@pytest.fixture
def model(ports_standard):
    """Crée un modèle standard"""
    return VillaniLogistics(ports_standard, epsilon=0.05, max_iter=100)

def test_port_creation():
    """Test de création d'un port"""
    port = Port("Test", 10.0, 20.0, 0.3, 0.7)
    assert port.nom == "Test"
    assert port.lat == 10.0
    assert port.lon == 20.0
    assert port.offre == 0.3
    assert port.demande == 0.7

def test_port_repr():
    """Test de la représentation d'un port"""
    port = Port("Test", 10.0, 20.0, 0.3, 0.7)
    repr_str = repr(port)
    assert "Test" in repr_str
    assert "0.30" in repr_str
    assert "0.70" in repr_str

def test_model_initialization(ports_standard):
    """Test de l'initialisation du modèle"""
    model = VillaniLogistics(ports_standard)
    assert model.n == 4
    assert model.epsilon == 0.05
    assert model.max_iter == 200
    assert model.tol == 1e-6
    assert model.cost_matrix is None
    assert model.transport_plan is None

def test_build_cost_matrix(model):
    """Test de la construction de la matrice de coût"""
    cost_matrix = model.build_cost_matrix()
    assert cost_matrix.shape == (4, 4)
    assert np.all(cost_matrix >= 0)
    assert np.allclose(cost_matrix, cost_matrix.T)  # Symétrique

def test_sinkhorn_convergence(model):
    """Test de convergence de l'algorithme de Sinkhorn"""
    model.build_cost_matrix()
    transport_plan = model.sinkhorn()
    assert transport_plan.shape == (4, 4)
    assert np.all(transport_plan >= 0)
    # Vérification des marges
    assert np.allclose(transport_plan.sum(axis=1), 
                       np.array([p.offre for p in model.ports]) / np.sum([p.offre for p in model.ports]))
    assert np.allclose(transport_plan.sum(axis=0), 
                       np.array([p.demande for p in model.ports]) / np.sum([p.demande for p in model.ports]))

def test_sinkhorn_2_ports(ports_2):
    """Test de Sinkhorn avec 2 ports"""
    model = VillaniLogistics(ports_2, epsilon=0.1, max_iter=50)
    model.build_cost_matrix()
    transport_plan = model.sinkhorn()
    assert transport_plan.shape == (2, 2)
    assert np.all(transport_plan >= 0)
    # Avec 2 ports, le transport devrait être trivial
    assert transport_plan[0, 1] > 0.4 or transport_plan[0, 0] > 0.4

def test_ricci_curvature(model):
    """Test du calcul de la courbure de Ricci"""
    model.build_cost_matrix()
    model.sinkhorn()
    curvature = model.compute_ricci_curvature()
    assert curvature.shape == (4, 4)
    assert np.allclose(np.diag(curvature), 0)
    # La courbure devrait être dans [-1, 1]
    assert np.all(curvature >= -1.1) and np.all(curvature <= 1.1)

def test_visualize_network(model):
    """Test de la visualisation du réseau"""
    model.build_cost_matrix()
    model.sinkhorn()
    fig = model.visualize_network()
    assert fig is not None

def test_generate_log(model):
    """Test de génération du log"""
    model.build_cost_matrix()
    model.sinkhorn()
    log = model.generate_log()
    assert isinstance(log, str)
    assert len(log) > 100
    assert "Configuration" in log
    assert "Résultats" in log

def test_sauvegarder_resultats(model, tmp_path):
    """Test de sauvegarde des résultats"""
    # Rediriger les sauvegardes vers un dossier temporaire
    original_path = os.getcwd()
    os.chdir(tmp_path)
    
    # Créer les dossiers nécessaires
    os.makedirs('data', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    
    model.build_cost_matrix()
    model.sinkhorn()
    model.sauvegarder_resultats()
    
    # Vérifier que les fichiers ont été créés
    assert os.path.exists('data/matrice_transport.csv')
    assert os.path.exists('results/resultats_transport.json')
    
    os.chdir(original_path)

def test_epsilon_variation(ports_standard):
    """Test de l'influence du paramètre epsilon"""
    epsilons = [0.01, 0.05, 0.1, 0.5]
    results = []
    for eps in epsilons:
        model = VillaniLogistics(ports_standard, epsilon=eps, max_iter=100)
        model.build_cost_matrix()
        model.sinkhorn()
        results.append({
            'epsilon': eps,
            'wasserstein': model.wasserstein_distance,
            'max_flow': np.max(model.transport_plan)
        })
    
    # Avec epsilon plus grand, le transport devrait être plus régularisé
    assert results[0]['wasserstein'] >= results[-1]['wasserstein'] * 0.5

def test_model_reproducibility(ports_standard):
    """Test de reproductibilité avec la même graine"""
    model1 = VillaniLogistics(ports_standard, seed=42)
    model2 = VillaniLogistics(ports_standard, seed=42)
    
    model1.build_cost_matrix()
    model2.build_cost_matrix()
    
    assert np.allclose(model1.cost_matrix, model2.cost_matrix)

def test_sinkhorn_offre_demande_egales(ports_standard):
    """Test quand offre = demande"""
    model = VillaniLogistics(ports_standard)
    model.build_cost_matrix()
    
    a = np.array([p.offre for p in model.ports])
    b = np.array([p.demande for p in model.ports])
    
    # Normaliser
    a = a / a.sum()
    b = b / b.sum()
    
    # Vérifier que les marges sont égales
    assert np.allclose(a.sum(), 1.0)
    assert np.allclose(b.sum(), 1.0)

def test_invalid_ports():
    """Test avec des ports invalides"""
    with pytest.raises(Exception):
        ports = [Port("A", 0, 0, -0.1, 0.5)]  # Offre négative
        model = VillaniLogistics(ports)
        model.build_cost_matrix()

def test_performance_large_number_ports():
    """Test de performance avec un grand nombre de ports"""
    # Créer 10 ports aléatoires
    np.random.seed(42)
    ports = []
    for i in range(10):
        offre = np.random.random()
        demande = np.random.random()
        ports.append(Port(f"P{i}", np.random.random()*10, np.random.random()*10, offre, demande))
    
    model = VillaniLogistics(ports, max_iter=50)
    model.build_cost_matrix()
    transport = model.sinkhorn()
    
    assert transport.shape == (10, 10)
    assert np.all(transport >= 0)

if __name__ == "__main__":
    pytest.main(["-v", __file__])
