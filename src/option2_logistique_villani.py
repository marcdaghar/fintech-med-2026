# src/option2_logistique_villani.py
"""
Option 2 : Simulation logistique méditerranéenne
Algorithme de Sinkhorn pour le transport optimal (Villani)
Version corrigée et optimisée
"""
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from scipy.spatial.distance import pdist, squareform
import os
import logging
import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Tuple, Optional
import yaml

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/option2.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Port:
    """Représentation d'un port méditerranéen"""
    nom: str
    lat: float
    lon: float
    offre: float
    demande: float
    
    def __repr__(self):
        return f"Port({self.nom}, offre={self.offre:.2f}, demande={self.demande:.2f})"

class VillaniLogistics:
    """Modèle de transport optimal basé sur l'algorithme de Sinkhorn"""
    
    def __init__(self, ports: List[Port], epsilon: float = 0.05, 
                 max_iter: int = 200, tol: float = 1e-6, seed: int = 42):
        """
        Initialise le modèle de transport
        
        Args:
            ports: Liste des ports
            epsilon: Paramètre de régularisation entropique
            max_iter: Nombre maximal d'itérations
            tol: Tolérance de convergence
            seed: Graine aléatoire
        """
        self.ports = ports
        self.n = len(ports)
        self.epsilon = epsilon
        self.max_iter = max_iter
        self.tol = tol
        self.seed = seed
        np.random.seed(seed)
        
        self.cost_matrix = None
        self.transport_plan = None
        self.wasserstein_distance = None
        self.curvature_matrix = None
        
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Crée les dossiers nécessaires"""
        dirs = ['results', 'logs', 'data']
        for d in dirs:
            os.makedirs(d, exist_ok=True)
    
    def build_cost_matrix(self) -> np.ndarray:
        """
        Construit la matrice de coût de transport
        
        Returns:
            Matrice de coût (n x n)
        """
        logger.info("Construction de la matrice de coût...")
        positions = np.array([[p.lat, p.lon] for p in self.ports])
        distances = squareform(pdist(positions, 'euclidean'))
        
        # Ajout d'un facteur de péage aléatoire
        peages = np.random.uniform(0, 0.3, (self.n, self.n))
        peages = (peages + peages.T) / 2  # Symétrisation
        np.fill_diagonal(peages, 0)
        
        self.cost_matrix = distances + peages
        logger.info(f"Matrice de coût construite (dimension {self.n}x{self.n})")
        return self.cost_matrix
    
    def sinkhorn(self) -> np.ndarray:
        """
        Algorithme de Sinkhorn pour le transport optimal régularisé
        
        Returns:
            Plan de transport optimal (n x n)
        """
        logger.info(f"Exécution de l'algorithme de Sinkhorn (ε={self.epsilon})...")
        
        a = np.array([p.offre for p in self.ports])
        b = np.array([p.demande for p in self.ports])
        
        # Normalisation
        a = a / a.sum()
        b = b / b.sum()
        
        # Matrice de Gibbs
        K = np.exp(-self.cost_matrix / self.epsilon)
        
        # Initialisation
        u = np.ones(self.n)
        v = np.ones(self.n)
        
        # Itérations de Sinkhorn
        for iteration in range(self.max_iter):
            u_prev = u.copy()
            
            # Mise à jour de u et v avec stabilisation
            v = b / (K.T @ u + 1e-12)
            u = a / (K @ v + 1e-12)
            
            # Vérification de la convergence
            if np.linalg.norm(u - u_prev) < self.tol:
                logger.info(f"✅ Sinkhorn converge après {iteration+1} itérations")
                break
        else:
            logger.warning(f"⚠️ Sinkhorn n'a pas convergé après {self.max_iter} itérations")
        
        # Plan de transport optimal
        self.transport_plan = np.diag(u) @ K @ np.diag(v)
        
        # Distance de Wasserstein
        self.wasserstein_distance = np.sum(self.transport_plan * self.cost_matrix)
        logger.info(f"Distance de Wasserstein-1 : {self.wasserstein_distance:.4f}")
        
        return self.transport_plan
    
    def compute_ricci_curvature(self) -> np.ndarray:
        """
        Calcul de la courbure de Ricci approchée (Ollivier-Ricci)
        
        Returns:
            Matrice de courbure (n x n)
        """
        logger.info("Calcul de la courbure de Ricci...")
        
        if self.transport_plan is None:
            self.sinkhorn()
        
        self.curvature_matrix = np.zeros((self.n, self.n))
        
        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    # Distance géodésique
                    d_ij = self.cost_matrix[i, j]
                    if d_ij > 1e-12:
                        # Courbure = 1 - W1/d_ij
                        self.curvature_matrix[i, j] = 1 - self.wasserstein_distance / d_ij
                    else:
                        self.curvature_matrix[i, j] = 0
        
        logger.info(f"Courbure moyenne : {np.mean(self.curvature_matrix):.4f}")
        return self.curvature_matrix
    
    def visualize_network(self):
        """
        Visualisation du réseau de transport
        """
        logger.info("Visualisation du réseau...")
        
        G = nx.DiGraph()
        
        # Ajout des nœuds
        for i, port in enumerate(self.ports):
            G.add_node(i, pos=(port.lon, port.lat), label=port.nom)
        
        # Ajout des arêtes avec flux
        if self.transport_plan is not None:
            for i in range(self.n):
                for j in range(self.n):
                    if self.transport_plan[i, j] > 0.01:
                        G.add_edge(i, j, weight=self.transport_plan[i, j])
        
        # Position des nœuds
        pos = nx.get_node_attributes(G, 'pos')
        
        # Création de la figure
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
        
        # Graphique 1 : Réseau avec flux
        nx.draw(G, pos, ax=ax1, with_labels=True, 
                labels=nx.get_node_attributes(G, 'label'),
                node_size=500, node_color='lightblue',
                font_size=10, font_weight='bold')
        
        # Ajout des épaisseurs de flux
        edges = G.edges()
        if edges:
            weights = [G[u][v]['weight'] * 100 for u, v in edges]
            nx.draw_networkx_edges(G, pos, ax=ax1, width=weights, alpha=0.6)
        ax1.set_title('Réseau de transport optimal (flux proportionnels)')
        
        # Graphique 2 : Matrice de transport
        im = ax2.imshow(self.transport_plan, cmap='viridis', aspect='auto')
        ax2.set_xlabel('Destination')
        ax2.set_ylabel('Source')
        ax2.set_title('Plan de transport optimal')
        plt.colorbar(im, ax=ax2)
        
        # Ajout des noms de ports
        labels = [p.nom for p in self.ports]
        ax2.set_xticks(range(self.n))
        ax2.set_yticks(range(self.n))
        ax2.set_xticklabels(labels, rotation=45, ha='right')
        ax2.set_yticklabels(labels)
        
        # Graphique 3 : Courbure de Ricci
        if self.curvature_matrix is not None:
            im2 = ax3.imshow(self.curvature_matrix, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1)
            ax3.set_xlabel('Destination')
            ax3.set_ylabel('Source')
            ax3.set_title('Courbure de Ricci')
            plt.colorbar(im2, ax=ax3)
            ax3.set_xticks(range(self.n))
            ax3.set_yticks(range(self.n))
            ax3.set_xticklabels(labels, rotation=45, ha='right')
            ax3.set_yticklabels(labels)
        
        plt.tight_layout()
        plt.savefig('results/transport_optimal.png', dpi=300, bbox_inches='tight')
        logger.info("Graphique sauvegardé : results/transport_optimal.png")
        plt.show()
        
        return fig
    
    def generate_log(self) -> str:
        """
        Génère un log détaillé de la simulation
        """
        log = f"""
# 🌊 Simulation logistique Villani / Transport optimal
## 📊 Rapport de simulation

### Configuration
- **Nombre de ports** : {self.n}
- **Régularisation entropique (ε)** : {self.epsilon}
- **Itérations max** : {self.max_iter}
- **Tolérance** : {self.tol}
- **Date** : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

### Résultats
- **Distance de Wasserstein-1** : {self.wasserstein_distance:.4f}
- **Coût total de transport** : {np.sum(self.transport_plan * self.cost_matrix):.4f}

### Ports
"""
        for port in self.ports:
            log += f"\n- **{port.nom}** : Offre={port.offre:.2f}, Demande={port.demande:.2f}"
        
        log += f"\n\n### Plan de transport"
        for i in range(self.n):
            log += f"\n- **{self.ports[i].nom}** → " + ", ".join(
                f"{self.ports[j].nom}: {self.transport_plan[i,j]:.3f}" 
                for j in range(self.n) if self.transport_plan[i,j] > 0.01
            )
        
        if self.curvature_matrix is not None:
            log += f"\n\n### Courbure de Ricci"
            for i in range(self.n):
                for j in range(self.n):
                    if i != j and abs(self.curvature_matrix[i,j]) > 0.01:
                        log += f"\n- **{self.ports[i].nom} → {self.ports[j].nom}** : {self.curvature_matrix[i,j]:.3f}"
        
        log += f"\n\n### Interprétation"
        if self.curvature_matrix is not None:
            neg_curv = np.sum(self.curvature_matrix < -0.1)
            log += f"\n- **{neg_curv}** liens avec courbure négative significative (goulots d'étranglement)"
        
        log += f"\n- **Courbure moyenne** : {np.mean(self.curvature_matrix):.4f}"
        
        return log
    
    def sauvegarder_resultats(self):
        """
        Sauvegarde les résultats dans différents formats
        """
        # Sauvegarde de la matrice de transport
        np.savetxt('data/matrice_transport.csv', self.transport_plan, delimiter=',')
        
        # Sauvegarde de la courbure
        if self.curvature_matrix is not None:
            np.savetxt('data/matrice_curbure.csv', self.curvature_matrix, delimiter=',')
        
        # Sauvegarde JSON
        resultats = {
            'ports': [{'nom': p.nom, 'offre': p.offre, 'demande': p.demande} for p in self.ports],
            'wasserstein_distance': float(self.wasserstein_distance),
            'transport_plan': self.transport_plan.tolist(),
            'cost_matrix': self.cost_matrix.tolist(),
            'curvature_matrix': self.curvature_matrix.tolist() if self.curvature_matrix is not None else None,
            'parametres': {
                'epsilon': self.epsilon,
                'max_iter': self.max_iter,
                'tol': self.tol
            },
            'date_generation': datetime.now().isoformat()
        }
        
        with open('results/resultats_transport.json', 'w', encoding='utf-8') as f:
            json.dump(resultats, f, indent=2, ensure_ascii=False)
        
        logger.info("Résultats sauvegardés")
    
    def run_simulation(self):
        """
        Exécute la simulation complète
        """
        try:
            # 1. Construction de la matrice de coût
            self.build_cost_matrix()
            
            # 2. Résolution du transport optimal
            self.sinkhorn()
            
            # 3. Calcul de la courbure de Ricci
            self.compute_ricci_curvature()
            
            # 4. Visualisation
            self.visualize_network()
            
            # 5. Génération du log
            log = self.generate_log()
            with open('results/log_villani.txt', 'w', encoding='utf-8') as f:
                f.write(log)
            
            # 6. Sauvegarde des résultats
            self.sauvegarder_resultats()
            
            logger.info("✅ Simulation terminée avec succès !")
            print("\n" + "="*60)
            print("✅ OPTION 2 TERMINÉE AVEC SUCCÈS")
            print("="*60)
            print(f"   - Graphique : results/transport_optimal.png")
            print(f"   - Log : results/log_villani.txt")
            print(f"   - Matrice transport : data/matrice_transport.csv")
            print(f"   - Résultats JSON : results/resultats_transport.json")
            
            return self.transport_plan, self.curvature_matrix
            
        except Exception as e:
            logger.error(f"Erreur lors de la simulation : {str(e)}")
            raise

def main():
    """Fonction principale"""
    # Définition des ports (données réalistes)
    ports = [
        Port("Marseille", 43.3, 5.4, 0.4, 0.25),
        Port("Bizerte", 37.3, 9.9, 0.2, 0.35),
        Port("Istanbul", 41.0, 29.0, 0.25, 0.2),
        Port("Odessa", 46.5, 30.7, 0.15, 0.2)
    ]
    
    # Création et exécution du modèle
    model = VillaniLogistics(ports, epsilon=0.05, max_iter=200)
    model.run_simulation()

if __name__ == "__main__":
    main()
