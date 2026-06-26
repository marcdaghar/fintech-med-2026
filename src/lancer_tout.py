def executer_option(numero, timeout=300):
    """Exécute une option avec timeout et gestion d'erreurs"""
    fichiers = {
        1: "option1_flux_entropique.py",
        2: "option2_logistique_villani.py", 
        3: "option3_waqf_numerique.py"
    }
    
    try:
        resultat = subprocess.run(
            [sys.executable, fichiers[numero]],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        
        if resultat.returncode != 0:
            print(f"❌ Erreur option {numero}: {resultat.stderr}")
            return False
        else:
            print(f"✅ Option {numero} réussie")
            return True
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout option {numero} après {timeout}s")
        return False
    except Exception as e:
        print(f"💥 Exception option {numero}: {str(e)}")
        return False
