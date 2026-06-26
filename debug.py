import sys
import subprocess
import importlib
import traceback
from datetime import datetime

def verifier_dependances():
    dependances = ['numpy', 'pandas', 'matplotlib', 'seaborn', 'networkx', 'scipy', 'pytest']
    manquantes = []
    for dep in dependances:
        try:
            importlib.import_module(dep)
            print(f"✅ {dep} installé")
        except ImportError:
            print(f"❌ {dep} manquant")
            manquantes.append(dep)
    return manquantes

def main():
    print("🔍 DÉBOGAGE AUTOMATISÉ DU PROJET FINTECH MED 2026")
    print("="*60)
    
    print("\n1. Vérification des dépendances...")
    manquantes = verifier_dependances()
    
    if manquantes:
        print(f"\n📦 Dépendances manquantes : {', '.join(manquantes)}")
        return
    
    print("\n2. Tests des options...")
    for i in range(1, 4):
        print(f"\nTest option {i}...")
        try:
            exec(open(f'src/option{i}_flux_entropique.py' if i==1 else f'src/option{i}_logistique_villani.py' if i==2 else f'src/option{i}_waqf_numerique.py').read())
            print(f"✅ Option {i} réussie")
        except Exception as e:
            print(f"❌ Option {i} échouée : {str(e)}")

if __name__ == "__main__":
    main()
EOF
