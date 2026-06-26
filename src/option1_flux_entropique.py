# src/option1_flux_entropique.py
"""
Option 1 : Tableau de bord « flux entropique »
Calcul de la fuite de valeur entre la Tunisie et la France
Version corrigée et optimisée
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging
from datetime import datetime
import json
import yaml

# Ajouter en début de fichier, après les imports
def charger_config():
    """Charge la configuration depuis config.yaml"""
    config = None
    try:
        if os.path.exists('config.yaml'):
            with open('config.yaml', 'r', encoding='utf-8') as f:
                full_config = yaml.safe_load(f)
                config = full_config.get('option1', {})
                logger.info("Configuration chargée depuis config.yaml")
    except Exception as e:
        logger.warning(f"Impossible de charger config.yaml : {str(e)}")
    return config

# Modifier le __init__ de FluxEntropiqueAnalyzer
def __init__(self, config=None):
    if config is None:
        config = charger_config()
    self.config = config or self._load_default_config()
    # ... reste du code

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/option1.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
ANNEE_DEBUT = 2020
ANNEE_FIN = 2026
PRODUITS = ['Céréales', 'Phosphates', 'Textiles', 'Composants électroniques', 'Oléagineux']
SEUIL_CRITIQUE_LAMBDA = 0.80

class FluxEntropiqueAnalyzer:
    """Analyseur de flux entropique pour les échanges Tunisie-France"""
    
    def __init__(self, config=None):
        self.config = config or self._load_default_config()
        self.seed = self.config.get('seed', 42)
        np.random.seed(self.seed)
        self._ensure_directories()
        
    def _load_default_config(self):
        """Charge la configuration par défaut"""
        return {
            'seed': 42,
            'annee_debut': ANNEE_DEBUT,
            'annee_fin': ANNEE_FIN,
            'produits': PRODUITS,
            'sigma': 5.0,
            'taux_interet': 0.05,
            'taux_dissipation': 1.0
        }
    
    def _ensure_directories(self):
        """Crée les dossiers nécessaires"""
        dirs = ['data', 'results', 'logs']
        for d in dirs:
            os.makedirs(d, exist_ok=True)
    
    def generer_donnees_commerce(self):
        """
        Génère des données synthétiques d'import/export
        avec des tendances réalistes
        """
        logger.info("Génération des données commerciales...")
        annees = list(range(self.config['annee_debut'], self.config['annee_fin'] + 1))
        data = []
        
        for annee in annees:
            for produit in self.config['produits']:
                # Tendance différente selon le produit
                if produit == 'Phosphates':
                    # Les phosphates augmentent (ressource stratégique)
                    base_export = 120 + 8 * (annee - self.config['annee_debut'])
                    base_import = 20 + 2 * (annee - self.config['annee_debut'])
                elif produit == 'Céréales':
                    # Les céréales diminuent après 2024 (sécheresse)
                    if annee <= 2024:
                        base_export = 80 - 3 * (annee - self.config['annee_debut'])
                    else:
                        base_export = 80 - 3 * 4 - 10 * (annee - 2024)
                    base_import = 30 + 5 * (annee - self.config['annee_debut'])
                elif produit == 'Textiles':
                    base_export = 60 - 2 * (annee - self.config['annee_debut'])
                    base_import = 40 + 3 * (annee - self.config['annee_debut'])
                elif produit == 'Composants électroniques':
                    base_export = 30 + 6 * (annee - self.config['annee_debut'])
                    base_import = 80 + 10 * (annee - self.config['annee_debut'])
                else:  # Oléagineux
                    base_export = 50 - 1 * (annee - self.config['annee_debut'])
                    base_import = 60 + 2 * (annee - self.config['annee_debut'])
                
                # Ajout de bruit
                export = max(0, base_export + np.random.normal(0, self.config['sigma']))
                import_ = max(0, base_import + np.random.normal(0, self.config['sigma']))
                
                data.append({
                    'annee': annee,
                    'produit': produit,
                    'export_tunisie_france_millions_usd': round(export, 2),
                    'import_tunisie_france_millions_usd': round(import_, 2)
                })
        
        df = pd.DataFrame(data)
        logger.info(f"Données générées : {len(df)} lignes")
        return df
    
    def calculer_flux_entropique(self, df):
        """
        Calcule le flux entropique = Import - Export
        """
        logger.info("Calcul du flux entropique...")
        df['flux_entropique_millions_usd'] = (
            df['import_tunisie_france_millions_usd'] - 
            df['export_tunisie_france_millions_usd']
        )
        return df
    
    def calculer_parametre_bifurcation(self, df):
        """
        Calcule le paramètre de bifurcation Λ
        """
        logger.info("Calcul du paramètre de bifurcation...")
        flux_annuel = df.groupby('annee')['flux_entropique_millions_usd'].sum().sort_index()
        
        # Dette cumulée
        dette_cumulee = flux_annuel.cumsum()
        
        # Paramètre de bifurcation
        r = self.config.get('taux_interet', 0.05)
        e_low = self.config.get('taux_dissipation', 1.0)
        
        lambda_param = (dette_cumulee * r) / e_low
        
        # Créer un DataFrame avec les résultats
        resultats = pd.DataFrame({
            'annee': flux_annuel.index,
            'flux': flux_annuel.values,
            'dette_cumulee': dette_cumulee.values,
            'lambda': lambda_param.values
        })
        
        # Ajouter le statut
        resultats['statut'] = resultats['lambda'].apply(
            lambda x: 'Stable' if x < SEUIL_CRITIQUE_LAMBDA else 'Instable'
        )
        
        return resultats
    
    def generer_graphique(self, df, flux_annuel):
        """
        Génère un graphique des flux entropiques
        """
        logger.info("Génération du graphique...")
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Graphique 1 : Flux total par année
        colors = ['green' if x < 0 else 'red' for x in flux_annuel['flux']]
        bars = ax1.bar(flux_annuel['annee'], flux_annuel['flux'], color=colors)
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax1.set_xlabel('Année', fontsize=12)
        ax1.set_ylabel('Flux entropique (millions USD)', fontsize=12)
        ax1.set_title('Flux entropique total Tunisie-France (Import - Export)', fontsize=14)
        ax1.grid(True, alpha=0.3)
        
        # Ajout des valeurs sur les barres
        for bar, val in zip(bars, flux_annuel['flux']):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'{val:.1f}', ha='center', va='bottom', fontsize=10)
        
        # Graphique 2 : Par produit pour la dernière année
        df_2026 = df[df['annee'] == 2026]
        produits = df_2026['produit']
        flux_produit = df_2026['flux_entropique_millions_usd']
        
        colors_produit = ['green' if x < 0 else 'red' for x in flux_produit]
        ax2.barh(produits, flux_produit, color=colors_produit)
        ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        ax2.set_xlabel('Flux entropique (millions USD)', fontsize=12)
        ax2.set_title('Flux entropique par produit (2026)', fontsize=14)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('results/flux_entropique.png', dpi=300, bbox_inches='tight')
        logger.info("Graphique sauvegardé : results/flux_entropique.png")
        plt.show()
        return fig
    
    def generer_graphique_lambda(self, resultats_lambda):
        """
        Génère un graphique du paramètre de bifurcation
        """
        logger.info("Génération du graphique du paramètre de bifurcation...")
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(resultats_lambda['annee'], resultats_lambda['lambda'], 
                'b-o', linewidth=2, markersize=8, label='Λ(t)')
        ax.axhline(y=SEUIL_CRITIQUE_LAMBDA, color='red', linestyle='--', 
                  linewidth=2, label=f'Seuil critique Λc = {SEUIL_CRITIQUE_LAMBDA}')
        
        # Remplir la zone instable
        ax.fill_between(resultats_lambda['annee'], 
                       SEUIL_CRITIQUE_LAMBDA, 
                       resultats_lambda['lambda'].max() + 0.1,
                       where=resultats_lambda['lambda'] > SEUIL_CRITIQUE_LAMBDA,
                       color='red', alpha=0.2, label='Zone d\'instabilité')
        
        ax.set_xlabel('Année', fontsize=12)
        ax.set_ylabel('Paramètre de bifurcation Λ', fontsize=12)
        ax.set_title('Évolution du paramètre de bifurcation Λ', fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.tight_layout()
        plt.savefig('results/parametre_bifurcation.png', dpi=300, bbox_inches='tight')
        logger.info("Graphique sauvegardé : results/parametre_bifurcation.png")
        plt.show()
        return fig
    
    def generer_rapport(self, df, resultats_lambda):
        """
        Génère un rapport en Markdown
        """
        logger.info("Génération du rapport...")
        flux_total = df['flux_entropique_millions_usd'].sum()
        tendance = "détérioration" if flux_total > 0 else "amélioration"
        derniere_annee = df['annee'].max()
        
        # Analyse par produit pour la dernière année
        df_derniere = df[df['annee'] == derniere_annee]
        produits_analyse = []
        for _, row in df_derniere.iterrows():
            statut = "déficitaire" if row['flux_entropique_millions_usd'] > 0 else "excédentaire"
            produits_analyse.append({
                'produit': row['produit'],
                'statut': statut,
                'flux': abs(row['flux_entropique_millions_usd'])
            })
        
        # Statistiques
        statut_global = "importatrice nette" if flux_total > 0 else "exportatrice nette"
        
        rapport = f"""
# Analyse du flux entropique Tunisie-France ({self.config['annee_debut']}-{self.config['annee_fin']})

## 📊 Résumé exécutif
Le flux entropique total sur la période {self.config['annee_debut']}-{self.config['annee_fin']} s'élève à **{flux_total:.2f} millions USD**.
Cette valeur indique une **{tendance}** de la balance commerciale tunisienne.
La Tunisie est **{statut_global}** de valeur vis-à-vis de la France.

## 📈 Évolution par produit ({derniere_annee})
"""
        
        for p in produits_analyse:
            rapport += f"\n- **{p['produit']}** : {p['statut']} de {p['flux']:.2f} millions USD."
        
        rapport += f"""

## 🔍 Paramètre de bifurcation Λ
- **Valeur actuelle** : {resultats_lambda.iloc[-1]['lambda']:.3f}
- **Seuil critique** : {SEUIL_CRITIQUE_LAMBDA}
- **Statut** : {resultats_lambda.iloc[-1]['statut']}

## 📊 Dette cumulée
- **Dette totale** : {resultats_lambda.iloc[-1]['dette_cumulee']:.2f} millions USD
- **Tendance** : Croissante

## 🛠️ Leviers de réduction proposés
1. **Transformation locale des phosphates** : Au lieu d'exporter le minerai brut, développer une industrie de transformation pour capter la valeur ajoutée.
2. **Circuits courts agricoles** : Réduire les importations céréalières via le développement de l'agriculture régénérative.
3. **Intégration des monnaies complémentaires** : Utiliser une monnaie commune pour réduire les coûts de transaction.

## 📊 Visualisations disponibles
- `results/flux_entropique.png` : Évolution du flux entropique
- `results/parametre_bifurcation.png` : Évolution du paramètre de bifurcation

## 💾 Données
- Fichier CSV : `data/donnees_commerce_synthetiques.csv`

---
*Rapport généré le {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*
"""
        return rapport
    
    def sauvegarder_resultats(self, df, resultats_lambda):
        """
        Sauvegarde les résultats dans différents formats
        """
        # Sauvegarde CSV
        df.to_csv('data/donnees_commerce_synthetiques.csv', index=False)
        resultats_lambda.to_csv('data/parametres_bifurcation.csv', index=False)
        
        # Sauvegarde JSON
        resultats = {
            'flux_total': df['flux_entropique_millions_usd'].sum(),
            'lambda_actuel': float(resultats_lambda.iloc[-1]['lambda']),
            'dette_cumulee': float(resultats_lambda.iloc[-1]['dette_cumulee']),
            'statut': resultats_lambda.iloc[-1]['statut'],
            'date_generation': datetime.now().isoformat(),
            'parametres': self.config
        }
        
        with open('results/resultats.json', 'w', encoding='utf-8') as f:
            json.dump(resultats, f, indent=2, ensure_ascii=False)
        
        logger.info("Résultats sauvegardés")
    
    def run_analysis(self):
        """
        Exécute l'analyse complète
        """
        try:
            # 1. Génération des données
            df = self.generer_donnees_commerce()
            
            # 2. Calcul du flux entropique
            df = self.calculer_flux_entropique(df)
            
            # 3. Calcul du paramètre de bifurcation
            flux_annuel = df.groupby('annee')['flux_entropique_millions_usd'].sum().reset_index()
            resultats_lambda = self.calculer_parametre_bifurcation(df)
            
            # 4. Génération des graphiques
            self.generer_graphique(df, flux_annuel)
            self.generer_graphique_lambda(resultats_lambda)
            
            # 5. Génération du rapport
            rapport = self.generer_rapport(df, resultats_lambda)
            with open('results/README_flux_entropique.md', 'w', encoding='utf-8') as f:
                f.write(rapport)
            
            # 6. Sauvegarde des résultats
            self.sauvegarder_resultats(df, resultats_lambda)
            
            logger.info("✅ Analyse terminée avec succès !")
            print("\n" + "="*60)
            print("✅ OPTION 1 TERMINÉE AVEC SUCCÈS")
            print("="*60)
            print(f"   - Données : data/donnees_commerce_synthetiques.csv")
            print(f"   - Graphiques : results/flux_entropique.png, results/parametre_bifurcation.png")
            print(f"   - Rapport : results/README_flux_entropique.md")
            print(f"   - Résultats JSON : results/resultats.json")
            
            return df, resultats_lambda
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse : {str(e)}")
            raise

def main():
    """Fonction principale"""
    analyzer = FluxEntropiqueAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
