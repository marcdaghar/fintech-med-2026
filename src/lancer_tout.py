
---

## 2. src/lancer_tout.py (Complet avec imports et main())

```python
#!/usr/bin/env python3
# src/lancer_tout.py
"""
Script d'exécution global pour les 3 options du projet Fintech Med
Version corrigée avec gestion d'erreurs complète
"""
import subprocess
import sys
import os
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/lancer_tout.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def executer_option(numero, timeout=300):
    """
    Exécute une option avec timeout et gestion d'erreurs
    
    Args:
        numero (int): Numéro de l'option (1, 2 ou 3)
        timeout (int): Timeout en secondes
    
    Returns:
        bool: True si l'exécution a réussi, False sinon
    """
    fichiers = {
        1: "option1_flux_entropique.py",
        2: "option2_logistique_villani.py",
        3: "option3_waqf_numerique.py"
    }
    
    nom_option = f"Option {numero}"
    fichier = fichiers.get(numero)
    
    if not fichier:
        logger.error(f"Option {numero} inconnue")
        return False
    
    chemin_fichier = os.path.join('src', fichier)
    
    if not os.path.exists(chemin_fichier):
        logger.error(f"Fichier {chemin_fichier} non trouvé")
        return False
    
    logger.info(f"🚀 Démarrage de l'{nom_option}...")
    print(f"\n{'='*60}")
    print(f"🚀 EXÉCUTION DE L'OPTION {numero}")
    print(f"{'='*60}\n")
    
    try:
        resultat = subprocess.run(
            [sys.executable, chemin_fichier],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=os.environ.copy()
        )
        
        # Afficher la sortie standard
        if resultat.stdout:
            print(resultat.stdout)
        
        # Afficher les erreurs
        if resultat.stderr:
            print(f"⚠️ Erreurs : {resultat.stderr}")
            logger.warning(f"{nom_option} - Erreurs : {resultat.stderr[:200]}...")
        
        if resultat.returncode == 0:
            logger.info(f"✅ {nom_option} terminée avec succès")
            print(f"\n✅ {nom_option} réussie")
            return True
        else:
            logger.error(f"❌ {nom_option} échouée avec le code {resultat.returncode}")
            print(f"\n❌ {nom_option} échouée (code {resultat.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"⏰ Timeout {nom_option} après {timeout}s")
        print(f"\n⏰ Timeout {nom_option} après {timeout}s")
        return False
    except FileNotFoundError as e:
        logger.error(f"❌ Fichier non trouvé : {str(e)}")
        print(f"\n❌ Erreur : {str(e)}")
        return False
    except Exception as e:
        logger.error(f"💥 Exception {nom_option}: {str(e)}")
        print(f"\n💥 Exception {nom_option}: {str(e)}")
        return False

def creer_dossiers():
    """Crée les dossiers nécessaires pour le projet"""
    dossiers = ['data', 'results', 'logs', 'contracts', 'docs']
    for dossier in dossiers:
        os.makedirs(dossier, exist_ok=True)
        logger.info(f"Dossier créé/vérifié : {dossier}")

def generer_rapport(success_options):
    """
    Génère un rapport des exécutions
    
    Args:
        success_options (list): Liste des options réussies
    """
    rapport = f"""
# 📊 Rapport d'Exécution - Fintech Méditerranée 2026

## 📅 Date
{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

## 📈 Résultats
"""
    
    for i in range(1, 4):
        statut = "✅ Succès" if i in success_options else "❌ Échec"
        rapport += f"- Option {i}: {statut}\n"
    
    if len(success_options) == 3:
        rapport += "\n## 🎉 TOUTES LES OPTIONS ONT RÉUSSI !"
    else:
        rapport += f"\n## ⚠️ {3 - len(success_options)} option(s) ont échoué"
    
    with open('logs/rapport_execution.md', 'w', encoding='utf-8') as f:
        f.write(rapport)
    
    logger.info("Rapport d'exécution sauvegardé : logs/rapport_execution.md")

def main():
    """Fonction principale"""
    print("""\
╔══════════════════════════════════════════════════════════════╗
║  🚀 PROJET FINTECH MÉDITERRANÉE 2026                        ║
║  Exécution des 3 options complémentaires                    ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Création des dossiers
    creer_dossiers()
    
    # Exécution des options
    success_options = []
    for i in range(1, 4):
        if executer_option(i):
            success_options.append(i)
    
    # Génération du rapport
    generer_rapport(success_options)
    
    # Résumé final
    print("\n" + "="*60)
    if len(success_options) == 3:
        print("✅ TOUTES LES OPTIONS ONT ÉTÉ EXÉCUTÉES AVEC SUCCÈS !")
    else:
        print(f"⚠️ {3 - len(success_options)} OPTION(S) ONT RENCONTRÉ DES ERREURS")
    print("="*60)
    print("\n📁 Dossier : Projet_Fintech_Med_2026/")
    print("📋 Logs : logs/")
    print("📊 Résultats : results/")
    print("📝 Rapport : logs/rapport_execution.md")

if __name__ == "__main__":
    main()
