# src/option3_waqf_numerique.py
"""
Option 3 : Générateur de waqf numérique pour DAO islamique
Contrat intelligent en Solidity
Version corrigée et optimisée
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Any
import logging
import yaml

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/option3.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WaqfGenerator:
    """Générateur de contrat intelligent waqf"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialise le générateur de waqf
        
        Args:
            config: Configuration du waqf
        """
        self.config = config or self._load_default_config()
        self.nom_waqf = self.config.get('nom_waqf', 'WaqfClusterMed')
        self.naqib = self.config.get('naqib', '0x1234567890123456789012345678901234567890')
        self.biens = self.config.get('biens', [
            {"id": "B001", "nom": "Port de Bizerte", "beneficiaire": "0x1111111111111111111111111111111111111111"},
            {"id": "B002", "nom": "Route Marseille-Bizerte", "beneficiaire": "0x2222222222222222222222222222222222222222"},
            {"id": "B003", "nom": "Hubs Istanbul", "beneficiaire": "0x3333333333333333333333333333333333333333"},
            {"id": "B004", "nom": "Stockage Odessa", "beneficiaire": "0x4444444444444444444444444444444444444444"}
        ])
        self.beneficiaires = self.config.get('beneficiaires', [
            {"adresse": "0x1111111111111111111111111111111111111111", 
             "nom": "Fondation Permaculture", "part": 30},
            {"adresse": "0x2222222222222222222222222222222222222222", 
             "nom": "Coopérative Logistique", "part": 25},
            {"adresse": "0x3333333333333333333333333333333333333333", 
             "nom": "Fonds Souverain Tunisien", "part": 25},
            {"adresse": "0x4444444444444444444444444444444444444444", 
             "nom": "INRAT", "part": 20}
        ])
        self._ensure_directories()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Charge la configuration par défaut"""
        return {
            'nom_waqf': 'WaqfClusterMed',
            'naqib': '0x1234567890123456789012345678901234567890',
            'biens': [
                {"id": "B001", "nom": "Port de Bizerte", "beneficiaire": "0x1111111111111111111111111111111111111111"},
                {"id": "B002", "nom": "Route Marseille-Bizerte", "beneficiaire": "0x2222222222222222222222222222222222222222"},
                {"id": "B003", "nom": "Hubs Istanbul", "beneficiaire": "0x3333333333333333333333333333333333333333"},
                {"id": "B004", "nom": "Stockage Odessa", "beneficiaire": "0x4444444444444444444444444444444444444444"}
            ],
            'beneficiaires': [
                {"adresse": "0x1111111111111111111111111111111111111111", 
                 "nom": "Fondation Permaculture", "part": 30},
                {"adresse": "0x2222222222222222222222222222222222222222", 
                 "nom": "Coopérative Logistique", "part": 25},
                {"adresse": "0x3333333333333333333333333333333333333333", 
                 "nom": "Fonds Souverain Tunisien", "part": 25},
                {"adresse": "0x4444444444444444444444444444444444444444", 
                 "nom": "INRAT", "part": 20}
            ]
        }
    
    def _ensure_directories(self):
        """Crée les dossiers nécessaires"""
        dirs = ['contracts', 'docs', 'logs']
        for d in dirs:
            os.makedirs(d, exist_ok=True)
    
    def generer_contrat_solidity(self) -> str:
        """
        Génère le contrat intelligent en Solidity
        
        Returns:
            Code Solidity du contrat
        """
        logger.info("Génération du contrat Solidity...")
        
        # Construction du code Solidity comme une chaîne de caractères valide
        contrat_lines = []
        contrat_lines.append("// SPDX-License-Identifier: MIT")
        contrat_lines.append("pragma solidity ^0.8.0;")
        contrat_lines.append("")
        contrat_lines.append("/**")
        contrat_lines.append(f" * @title {self.nom_waqf}")
        contrat_lines.append(" * @dev Waqf numérique pour la coopération méditerranéenne")
        contrat_lines.append(" * @author Généré automatiquement par DeerFlow")
        contrat_lines.append(f" * @date {datetime.now().strftime('%Y-%m-%d')}")
        contrat_lines.append(" */")
        contrat_lines.append(f"contract {self.nom_waqf} {{")
        contrat_lines.append("    ")
        contrat_lines.append("    // ======== STRUCTURES ========")
        contrat_lines.append("    ")
        contrat_lines.append("    struct Bien {")
        contrat_lines.append("        string id;")
        contrat_lines.append("        string nom;")
        contrat_lines.append("        address beneficiaire;")
        contrat_lines.append("        uint256 montant;")
        contrat_lines.append("        bool actif;")
        contrat_lines.append("    }")
        contrat_lines.append("    ")
        contrat_lines.append("    struct Redistribution {")
        contrat_lines.append("        uint256 timestamp;")
        contrat_lines.append("        uint256 montantTotal;")
        contrat_lines.append("        mapping(address => uint256) parts;")
        contrat_lines.append("    }")
        contrat_lines.append("    ")
        contrat_lines.append("    // ======== ÉVÉNEMENTS ========")
        contrat_lines.append("    ")
        contrat_lines.append("    event BienAjoute(string id, string nom, address beneficiaire);")
        contrat_lines.append("    event RedistributionEffectuee(uint256 timestamp, uint256 montantTotal);")
        contrat_lines.append("    event PartModifiee(address beneficiaire, uint256 nouvellePart);")
        contrat_lines.append("    event FraisRecus(address sender, uint256 montant);")
        contrat_lines.append("    event FondsRecuperes(address naqib, uint256 montant);")
        contrat_lines.append("    ")
        contrat_lines.append("    // ======== ÉTATS ========")
        contrat_lines.append("    ")
        contrat_lines.append("    address public naqib; // Gestionnaire du waqf")
        contrat_lines.append("    string public nom;")
        contrat_lines.append("    uint256 public totalBiens;")
        contrat_lines.append("    uint256 public totalFrais;")
        contrat_lines.append("    uint256 public totalRedistribue;")
        contrat_lines.append("    ")
        contrat_lines.append("    // Mapping des biens")
        contrat_lines.append("    mapping(string => Bien) public biens;")
        contrat_lines.append("    string[] public listeBiens;")
        contrat_lines.append("    ")
        contrat_lines.append("    // Mapping des bénéficiaires")
        contrat_lines.append("    mapping(address => uint256) public parts; // En pourcentage (base 10000)")
        contrat_lines.append("    address[] public listeBeneficiaires;")
        contrat_lines.append("    ")
        contrat_lines.append("    // Historique des redistributions")
        contrat_lines.append("    Redistribution[] public historique;")
        contrat_lines.append("    ")
        contrat_lines.append("    // ======== MODIFIERS ========")
        contrat_lines.append("    ")
        contrat_lines.append("    modifier seulementNaqib() {")
        contrat_lines.append("        require(msg.sender == naqib, \"Seul le naqib peut effectuer cette action\");")
        contrat_lines.append("        _;")
        contrat_lines.append("    }")
        contrat_lines.append("    ")
        contrat_lines.append("    modifier bienExiste(string memory _id) {")
        contrat_lines.append("        require(biens[_id].actif, \"Le bien n existe pas ou est inactif\");")
        contrat_lines.append("        _;")
        contrat_lines.append("    }")
        contrat_lines.append("    ")
        contrat_lines.append("    // ======== CONSTRUCTEUR ========")
        contrat_lines.append("    ")
        contrat_lines.append("    constructor(string memory _nom, address _naqib) {")
        contrat_lines.append("        nom = _nom;")
        contrat_lines.append("        naqib = _naqib;")
        contrat_lines.append("        ")
        contrat_lines.append("        // Initialisation des bénéficiaires par défaut")
        
        # Ajout des bénéficiaires
        for benef in self.beneficiaires:
            contrat_lines.append(f"        parts[{benef['adresse']}] = {benef['part'] * 100}; // {benef['part']}%")
            contrat_lines.append(f"        listeBeneficiaires.push({benef['adresse']});")
        
        contrat_lines.append("    }")
        contrat_lines.append("    ")
        contrat_lines.append("    // ======== FONCTIONS DE GESTION ========")
        contrat_lines.append("    ")
        contrat_lines.append("    /**")
        contrat_lines.append("     * @dev Ajoute un bien au waqf")
        contrat_lines.append("     */")
        contrat_lines.append("    function ajouterBien(")
        contrat_lines.append("        string memory _id,")
        contrat_lines.append("        string memory _nom,")
        contrat_lines.append("        address _beneficiaire")
        contrat_lines.append("    ) public seulementNaqib {")
        contrat_lines.append("        require(!biens[_id].actif, \"Ce bien existe deja\");")
        contrat_lines.append("        require(_beneficiaire != address(0), \"Adresse invalide\");")
        contrat_lines.append("        ")
        contrat_lines.append("        biens[_id] = Bien({")
        contrat_lines.append("            id: _id,")
        contrat_lines.append("            nom: _nom,")
        contrat_lines.append("            beneficiaire: _beneficiaire,")
        contrat_lines.append("            montant: 0,")
        contrat_lines.append("            actif: true")
        contrat_lines.append("        });")
        contrat_lines.append("        listeBiens.push(_id);")
        contrat_lines.append("        totalBiens++;")
        contrat_lines.append("        ")
        contrat_lines.append("        emit BienAjoute(_id, _nom, _beneficiaire);")
        contrat_lines.append("    }")
        contrat_lines.append("    ")
        contrat_lines.append("    /**")
        contrat_lines.append("     * @dev Reçoit des frais (en monnaie X)")
        contrat_lines.append("     */")
        contrat_lines.append("    function recevoirFrais() public payable {")
        contrat_lines.append("        require(msg.value > 0, \"Montant nul\");")
        contrat_lines.append("        totalFrais += msg.value;")
        contrat_lines.append("        emit FraisRecus(msg.sender, msg.value);")
        contrat_lines.append("    }")
        contrat_lines.append("    ")
        contrat_lines.append("    /**")
        contrat_lines.append("     * @dev Redistribue les frais aux bénéficiaires")
        contrat_lines.append("     */")
        contrat_lines.append("    function redistribuerRevenus() public seulementNaqib {")
        contrat_lines.append("        require(totalFrais > 0, \"Aucun frais a redistribuer\");")
        contrat_lines.append("        ")
        contrat_lines.append("        uint256 montantTotal = totalFrais;")
        contrat_lines.append("        uint256 index = historique.length;")
        contrat_lines.append("        ")
        contrat_lines.append("        // Création de la redistribution")
        contrat_lines.append("        historique.push();")
        contrat_lines.append("        Redistribution storage redistribution = historique[index];")
        contrat_lines.append("        redistribution.timestamp = block.timestamp;")
        contrat_lines.append("        redistribution.montantTotal = montantTotal;")
        contrat_lines.append("        ")
        contrat_lines.append("        // Redistribution selon les parts")
        contrat_lines.append("        uint256 totalParts = 0;")
        contrat_lines.append("        for (uint256 i = 0; i < listeBeneficiaires.length; i++) {")
        contrat_lines.append("            totalParts += parts[listeBeneficiaires[i]];")
        contrat_lines.append("        }")
        contrat_lines.append("        require(totalParts > 0, \"Total des parts nul\");")
        contrat_lines.append("        ")
        contrat_lines.append("        for (uint256 i = 0; i < listeBeneficiaires.length; i++) {")
        contrat_lines.append("            address benef = listeBeneficiaires[i];")
        contrat_lines.append("            uint256 part = (parts[benef] * montantTotal) / totalParts;")
        contrat_lines.append("            redistribution.parts[benef] = part;")
        contrat_lines.append("            ")
        contrat_lines.append("            // Transfert vers le bénéficiaire")
        contrat_lines.append("            if (part > 0) {")
        contrat_lines.append("                payable(benef).transfer(part);")
        contrat_lines.append("            }")
        contrat_lines.append("        }")
        contrat_lines.append("        ")
        contrat_lines.append("        totalRedistribue += montantTotal;")
        contrat_lines.append("        totalFrais = 0;")
        contrat_lines.append("        emit RedistributionEffectuee(block.timestamp, montantTotal);")
        contrat_lines.append("    }")
        contrat_lines.append("    ")
        contrat_lines.append("    /**")
        contrat_lines.append("     * @dev Modifie la part d'un bénéficiaire")
        contrat_lines.append("     */")
        contrat_lines.append("    function modifierPart(address _beneficiaire, uint256 _nouvellePart) ")
        contrat_lines.append("        public seulementNaqib ")
        contrat_lines.append("    {")
        contrat_lines.append("        require(_beneficiaire != address(0), \"Adresse invalide\");")
        contrat_lines.append("        require(_nouvellePart > 0, \"La part doit etre positive\");")
        contrat_lines.append("        require(_nouvellePart <= 100, \"La part doit etre <= 100%\");")
        contrat_lines.append("        ")
        contrat_lines.append("        parts[_beneficiaire] = _nouvellePart * 100;")
        contrat_lines.append("        emit PartModifiee(_beneficiaire, _nouvellePart);")
        contrat_lines.append("    }")
        contrat_lines.append("    ")
        contrat_lines.append("    /**")
        contrat_lines.append("     * @dev Consultations (view functions)")
        contrat_lines.append("     */")
        contrat_lines.append("    function obtenirPart(address _beneficiaire) public view returns (uint256) {")
        contrat_lines.append("        return parts[_beneficiaire] / 100;")
        contrat_lines.append("    }")
        contrat_lines.append("    ")
        contrat_lines.append("    function obtenirHistorique() public view returns (uint256[] memory) {")
        contrat_lines.append("        uint256[] memory timestamps = new uint256[](historique.length);")
        contrat_lines.append("        for (uint256 i = 0; i < historique.length; i++) {")
        contrat_lines.append("            timestamps[i] = historique[i].timestamp;")
        contrat_lines.append("        }")
        contrat_lines.append("        return timestamps;")
        contrat_lines.append("    }")
        contrat_lines.append("    ")
        contrat_lines.append("    function obtenirMontantTotal() public view returns (uint256) {")
        contrat_lines.append("        return totalFrais;")
        contrat_lines.append("    }")
        contrat_lines.append("    ")
        contrat_lines.append("    function obtenirTotalRedistribue() public view returns (uint256) {")
        contrat_lines.append("        return totalRedistribue;")
        contrat_lines.append("    }")
        contrat_lines.append("    ")
        contrat_lines.append("    function obtenirNombreBiens() public view returns (uint256) {")
        contrat_lines.append("        return totalBiens;")
        contrat_lines.append("    }")
        contrat_lines.append("    ")
        contrat_lines.append("    function obtenirNombreBeneficiaires() public view returns (uint256) {")
        contrat_lines.append("        return listeBeneficiaires.length;")
        contrat_lines.append("    }")
        contrat_lines.append("    ")
        contrat_lines.append("    // ======== FONCTION DE RÉCUPÉRATION D'URGENCE ========")
        contrat_lines.append("    ")
        contrat_lines.append("    /**")
        contrat_lines.append("     * @dev Permet au naqib de récupérer les fonds en cas d'urgence")
        contrat_lines.append("     */")
        contrat_lines.append("    function recupererFonds() public seulementNaqib {")
        contrat_lines.append("        require(totalFrais > 0, \"Aucun fonds a recuperer\");")
        contrat_lines.append("        uint256 montant = totalFrais;")
        contrat_lines.append("        totalFrais = 0;")
        contrat_lines.append("        payable(naqib).transfer(montant);")
        contrat_lines.append("        emit FondsRecuperes(naqib, montant);")
        contrat_lines.append("    }")
        contrat_lines.append("    ")
        contrat_lines.append("    // ======== FONCTION DE DÉSACTIVATION ========")
        contrat_lines.append("    ")
        contrat_lines.append("    /**")
        contrat_lines.append("     * @dev Désactive un bien (le rend inactif)")
        contrat_lines.append("     */")
        contrat_lines.append("    function desactiverBien(string memory _id) public seulementNaqib bienExiste(_id) {")
        contrat_lines.append("        biens[_id].actif = false;")
        contrat_lines.append("        totalBiens--;")
        contrat_lines.append("    }")
        contrat_lines.append("}")
        
        contrat = "\n".join(contrat_lines)
        logger.info("Contrat Solidity généré")
        return contrat
    
    # Les autres méthodes restent identiques...
    def generer_readme(self) -> str:
        """Génère le README explicatif"""
        # ... (méthode inchangée)
        pass
    
    def generer_script_deploiement(self) -> str:
        """Génère le script de déploiement Hardhat"""
        # ... (méthode inchangée)
        pass
    
    def generer_hardhat_config(self) -> str:
        """Génère la configuration Hardhat"""
        # ... (méthode inchangée)
        pass
    
    def generer_json_abi(self) -> Dict[str, Any]:
        """Génère une représentation JSON du contrat"""
        # ... (méthode inchangée)
        pass
    
    def generer_tous_fichiers(self):
        """
        Génère tous les fichiers du projet waqf
        """
        try:
            # 1. Contrat Solidity
            contrat = self.generer_contrat_solidity()
            with open(f'contracts/{self.nom_waqf}.sol', 'w', encoding='utf-8') as f:
                f.write(contrat)
            logger.info(f"Contrat sauvegardé : contracts/{self.nom_waqf}.sol")
            
            # 2. README
            readme = self.generer_readme()
            with open('docs/README_waqf.md', 'w', encoding='utf-8') as f:
                f.write(readme)
            logger.info("README sauvegardé : docs/README_waqf.md")
            
            # 3. Script de déploiement
            deploy_script = self.generer_script_deploiement()
            os.makedirs('scripts', exist_ok=True)
            with open(f'scripts/deploy_{self.nom_waqf}.js', 'w', encoding='utf-8') as f:
                f.write(deploy_script)
            logger.info(f"Script de déploiement sauvegardé : scripts/deploy_{self.nom_waqf}.js")
            
            # 4. Configuration Hardhat
            hardhat_config = self.generer_hardhat_config()
            with open('hardhat.config.js', 'w', encoding='utf-8') as f:
                f.write(hardhat_config)
            logger.info("Configuration Hardhat sauvegardée : hardhat.config.js")
            
            # 5. JSON ABI
            json_data = self.generer_json_abi()
            with open('contracts/waqf_abi.json', 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            logger.info("JSON ABI sauvegardé : contracts/waqf_abi.json")
            
            print("\n" + "="*60)
            print("✅ OPTION 3 TERMINÉE AVEC SUCCÈS")
            print("="*60)
            print(f"   - Contrat : contracts/{self.nom_waqf}.sol")
            print(f"   - README : docs/README_waqf.md")
            print(f"   - Script déploiement : scripts/deploy_{self.nom_waqf}.js")
            print(f"   - Hardhat config : hardhat.config.js")
            print(f"   - JSON ABI : contracts/waqf_abi.json")
            
            logger.info("✅ Génération terminée avec succès !")
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération : {str(e)}")
            raise

def main():
    """Fonction principale"""
    # Chargement de la configuration depuis un fichier YAML si existant
    config = None
    if os.path.exists('config.yaml'):
        try:
            with open('config.yaml', 'r', encoding='utf-8') as f:
                full_config = yaml.safe_load(f)
                config = full_config.get('option3', {})
                logger.info("Configuration chargée depuis config.yaml")
        except Exception as e:
            logger.warning(f"Impossible de charger config.yaml : {str(e)}")
    
    generator = WaqfGenerator(config)
    generator.generer_tous_fichiers()

if __name__ == "__main__":
    main()
