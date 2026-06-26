#!/usr/bin/env python3
# debug.py
"""
Script de débogage automatisé pour le projet Fintech Med 2026
Version corrigée utilisant subprocess pour une exécution propre
"""
import sys
import subprocess
import importlib
import os
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def verifier_dependances():
    """
    Vérifie que toutes les dépendances sont installées
    
    Returns:
        list: Liste des dépendances manquantes
    """
    dependances = ['numpy', 'pandas', 'matplotlib', 'seaborn', 'networkx', 'scipy', 'pytest', 'yaml']
    manquantes = []
    
    print("\n📦 Vérification des dépendances...")
    for dep in dependances:
        try:
            importlib.import_module(dep)
            print(f"   ✅ {dep} installé")
        except ImportError:
            print(f"   ❌ {dep} manquant")
            manquantes.append(dep)
    
    return manquantes

def tester_option(numero):
    """
    Teste une option et capture les erreurs
    
    Args:
        numero (int): Numéro de l'option (1, 2 ou 3)
    
    Returns:
        bool: True si le test a réussi, False sinon
    """
    fichiers = {
        1: "src/option1_flux_entropique.py",
        2: "src/option2_logistique_villani.py",
        3: "src/option3_waqf_numerique.py"
    }
    
    nom_option = f"Option {numero}"
    fichier = fichiers.get(numero)
    
    if not fichier:
        logger.error(f"Option {numero} inconnue")
        return False
    
    if not os.path.exists(fichier):
        logger.error(f"Fichier {fichier} non trouvé")
        return False
    
    print(f"\n🔍 Test de l'{nom_option}...")
    logger.info(f"Démarrage du test {nom_option}")
    
    try:
        resultat = subprocess.run(
            [sys.executable, fichier],
            capture_output=True,
            text=True,
            timeout=60,  # Timeout de 60 secondes
            check=False,
            env=os.environ.copy()
        )
        
        # Afficher la sortie standard (limitée)
        if resultat.stdout:
            lignes = resultat.stdout.split('\n')
            if len(lignes) > 20:
                print('\n'.join(lignes[:10]))
                print(f"... ({len(lignes)-20} lignes supplémentaires)")
                print('\n'.join(lignes[-10:]))
            else:
                print(resultat.stdout)
        
        # Afficher les erreurs
        if resultat.stderr:
            print(f"\n⚠️ Erreurs : {resultat.stderr[:500]}...")
            logger.warning(f"{nom_option} - Erreurs détectées")
        
        if resultat.returncode == 0:
            print(f"   ✅ {nom_option} réussie")
            logger.info(f"{nom_option} - Test réussi")
            return True
        else:
            print(f"   ❌ {nom_option} échouée (code {resultat.returncode})")
            logger.error(f"{nom_option} - Échec avec le code {resultat.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout {nom_option} après 60s")
        logger.error(f"{nom_option} - Timeout")
        return False
    except Exception as e:
        print(f"   💥 Exception {nom_option}: {str(e)}")
        logger.error(f"{nom_option} - Exception: {str(e)}")
        return False

def generer_rapport_debug(resultats):
    """
    Génère un rapport de débogage
    
    Args:
        resultats (dict): Dictionnaire des résultats par option
    """
    rapport = f"""# 🔍 Rapport de Débogage - Fintech Méditerranée 2026

## 📅 Date
{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

## 📊 Résultats des Tests

| Option | Statut |
|--------|--------|
"""
    
    for i in range(1, 4):
        statut = "✅ OK" if resultats.get(i, False) else "❌ KO"
        rapport += f"| Option {i} | {statut} |\n"
    
    total_ok = sum(1 for v in resultats.values() if v)
    rapport += f"\n## 📈 Résumé\n"
    rapport += f"- **Total** : {len(resultats)} options testées\n"
    rapport += f"- **Réussites** : {total_ok}\n"
    rapport += f"- **Échecs** : {len(resultats) - total_ok}\n"
    
    if total_ok == len(resultats):
        rapport += "\n### 🎉 Tous les tests ont réussi !"
    else:
        rapport += f"\n### ⚠️ {len(resultats) - total_ok} option(s) ont échoué"
    
    rapport += f"\n\n## 💡 Recommandations\n"
    if total_ok < len(resultats):
        rapport += "- Vérifiez les logs dans `logs/` pour plus de détails\n"
        rapport += "- Assurez-vous que toutes les dépendances sont installées\n"
        rapport += "- Exécutez `python src/lancer_tout.py` pour un test complet\n"
    else:
        rapport += "- Le projet est prêt pour une exécution complète\n"
        rapport += "- Exécutez `python src/lancer_tout.py` pour lancer toutes les options\n"
    
    # Sauvegarder le rapport
    with open('logs/rapport_debug.md', 'w', encoding='utf-8') as f:
        f.write(rapport)
    
    logger.info("Rapport de débogage sauvegardé : logs/rapport_debug.md")

def main():
    """Fonction principale"""
    print("""\
╔══════════════════════════════════════════════════════════════╗
║  🔍 DÉBOGAGE AUTOMATISÉ DU PROJET FINTECH MED 2026          ║
║  Vérification des dépendances et des options                ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Création des dossiers
    os.makedirs('logs', exist_ok=True)
    os.makedirs('src', exist_ok=True)
    
    # 1. Vérification des dépendances
    manquantes = verifier_dependances()
    
    if manquantes:
        print(f"\n📦 Dépendances manquantes : {', '.join(manquantes)}")
        print("   Exécutez : pip install " + " ".join(manquantes))
        return
    
    # 2. Tests des options
    resultats = {}
    for i in range(1, 4):
        resultats[i] = tester_option(i)
    
    # 3. Génération du rapport
    generer_rapport_debug(resultats)
    
    # 4. Résumé final
    print("\n" + "="*60)
    total_ok = sum(1 for v in resultats.values() if v)
    if total_ok == len(resultats):
        print("🎉 TOUS LES TESTS ONT RÉUSSI !")
    else:
        print(f"⚠️ {len(resultats) - total_ok} OPTION(S) ONT ÉCHOUÉ")
    print("="*60)
    print(f"\n📋 Rapport : logs/rapport_debug.md")
    print(f"📊 Logs : logs/debug.log")

if __name__ == "__main__":
    main()
