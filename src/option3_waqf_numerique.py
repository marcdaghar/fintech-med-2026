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
        
        # Échapper les guillemets dans les chaînes
        nom_waqf_escaped = self.nom_waqf.replace('"', '\\"')
        
        contrat = f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title {self.nom_waqf}
 * @dev Waqf num\\u00e9rique pour la coop\\u00e9ration m\\u00e9diterran\\u00e9enne
 * @author G\\u00e9n\\u00e9r\\u00e9 automatiquement par DeerFlow
 * @date {datetime.now().strftime('%Y-%m-%d')}
 */
contract {self.nom_waqf} {{
    
    // ======== STRUCTURES ========
    
    struct Bien {{
        string id;
        string nom;
        address beneficiaire;
        uint256 montant;
        bool actif;
    }}
    
    struct Redistribution {{
        uint256 timestamp;
        uint256 montantTotal;
        mapping(address => uint256) parts;
    }}
    
    // ======== \\u00c9V\\u00c9NEMENTS ========
    
    event BienAjoute(string id, string nom, address beneficiaire);
    event RedistributionEffectuee(uint256 timestamp, uint256 montantTotal);
    event PartModifiee(address beneficiaire, uint256 nouvellePart);
    event FraisRecus(address sender, uint256 montant);
    event FondsRecuperes(address naqib, uint256 montant);
    
    // ======== \\u00c9TATS ========
    
    address public naqib; // Gestionnaire du waqf
    string public nom;
    uint256 public totalBiens;
    uint256 public totalFrais;
    uint256 public totalRedistribue;
    
    // Mapping des biens
    mapping(string => Bien) public biens;
    string[] public listeBiens;
    
    // Mapping des b\\u00e9n\\u00e9ficiaires
    mapping(address => uint256) public parts; // En pourcentage (base 10000)
    address[] public listeBeneficiaires;
    
    // Historique des redistributions
    Redistribution[] public historique;
    
    // ======== MODIFIERS ========
    
    modifier seulementNaqib() {{
        require(msg.sender == naqib, "Seul le naqib peut effectuer cette action");
        _;
    }}
    
    modifier bienExiste(string memory _id) {{
        require(biens[_id].actif, "Le bien n existe pas ou est inactif");
        _;
    }}
    
    // ======== CONSTRUCTEUR ========
    
    constructor(string memory _nom, address _naqib) {{
        nom = _nom;
        naqib = _naqib;
        
        // Initialisation des b\\u00e9n\\u00e9ficiaires par d\\u00e9faut
"""
        
        # Ajout des bénéficiaires
        for benef in self.beneficiaires:
            contrat += f"""
        parts[{benef["adresse"]}] = {benef["part"] * 100}; // {benef["part"]}%
        listeBeneficiaires.push({benef["adresse"]});
"""
        
        contrat += """
    }
    
    // ======== FONCTIONS DE GESTION ========
    
    /**
     * @dev Ajoute un bien au waqf
     */
    function ajouterBien(
        string memory _id,
        string memory _nom,
        address _beneficiaire
    ) public seulementNaqib {
        require(!biens[_id].actif, "Ce bien existe deja");
        require(_beneficiaire != address(0), "Adresse invalide");
        
        biens[_id] = Bien({
            id: _id,
            nom: _nom,
            beneficiaire: _beneficiaire,
            montant: 0,
            actif: true
        });
        listeBiens.push(_id);
        totalBiens++;
        
        emit BienAjoute(_id, _nom, _beneficiaire);
    }
    
    /**
     * @dev Re\\u00e7oit des frais (en monnaie X)
     */
    function recevoirFrais() public payable {
        require(msg.value > 0, "Montant nul");
        totalFrais += msg.value;
        emit FraisRecus(msg.sender, msg.value);
    }
    
    /**
     * @dev Redistribue les frais aux b\\u00e9n\\u00e9ficiaires
     */
    function redistribuerRevenus() public seulementNaqib {
        require(totalFrais > 0, "Aucun frais a redistribuer");
        
        uint256 montantTotal = totalFrais;
        uint256 index = historique.length;
        
        // Cr\\u00e9ation de la redistribution
        historique.push();
        Redistribution storage redistribution = historique[index];
        redistribution.timestamp = block.timestamp;
        redistribution.montantTotal = montantTotal;
        
        // Redistribution selon les parts
        uint256 totalParts = 0;
        for (uint256 i = 0; i < listeBeneficiaires.length; i++) {
            totalParts += parts[listeBeneficiaires[i]];
        }
        require(totalParts > 0, "Total des parts nul");
        
        for (uint256 i = 0; i < listeBeneficiaires.length; i++) {
            address benef = listeBeneficiaires[i];
            uint256 part = (parts[benef] * montantTotal) / totalParts;
            redistribution.parts[benef] = part;
            
            // Transfert vers le b\\u00e9n\\u00e9ficiaire
            if (part > 0) {
                payable(benef).transfer(part);
            }
        }
        
        totalRedistribue += montantTotal;
        totalFrais = 0;
        emit RedistributionEffectuee(block.timestamp, montantTotal);
    }
    
    /**
     * @dev Modifie la part d'un b\\u00e9n\\u00e9ficiaire
     */
    function modifierPart(address _beneficiaire, uint256 _nouvellePart) 
        public seulementNaqib 
    {
        require(_beneficiaire != address(0), "Adresse invalide");
        require(_nouvellePart > 0, "La part doit etre positive");
        require(_nouvellePart <= 100, "La part doit etre <= 100%");
        
        parts[_beneficiaire] = _nouvellePart * 100;
        emit PartModifiee(_beneficiaire, _nouvellePart);
    }
    
    /**
     * @dev Consultations (view functions)
     */
    function obtenirPart(address _beneficiaire) public view returns (uint256) {
        return parts[_beneficiaire] / 100;
    }
    
    function obtenirHistorique() public view returns (uint256[] memory) {
        uint256[] memory timestamps = new uint256[](historique.length);
        for (uint256 i = 0; i < historique.length; i++) {
            timestamps[i] = historique[i].timestamp;
        }
        return timestamps;
    }
    
    function obtenirMontantTotal() public view returns (uint256) {
        return totalFrais;
    }
    
    function obtenirTotalRedistribue() public view returns (uint256) {
        return totalRedistribue;
    }
    
    function obtenirNombreBiens() public view returns (uint256) {
        return totalBiens;
    }
    
    function obtenirNombreBeneficiaires() public view returns (uint256) {
        return listeBeneficiaires.length;
    }
    
    // ======== FONCTION DE R\\u00c9CUP\\u00c9RATION D'URGENCE ========
    
    /**
     * @dev Permet au naqib de r\\u00e9cup\\u00e9rer les fonds en cas d'urgence
     */
    function recupererFonds() public seulementNaqib {
        require(totalFrais > 0, "Aucun fonds a recuperer");
        uint256 montant = totalFrais;
        totalFrais = 0;
        payable(naqib).transfer(montant);
        emit FondsRecuperes(naqib, montant);
    }
    
    // ======== FONCTION DE D\\u00c9SACTIVATION ========
    
    /**
     * @dev D\\u00e9sactive un bien (le rend inactif)
     */
    function desactiverBien(string memory _id) public seulementNaqib bienExiste(_id) {
        biens[_id].actif = false;
        totalBiens--;
    }
}
"""
        logger.info("Contrat Solidity généré")
        return contrat
    
    def generer_readme(self) -> str:
        """
        Génère le README explicatif
        
        Returns:
            README en Markdown
        """
        logger.info("Génération du README...")
        
        readme = f"""# 🕌 {self.nom_waqf} - Contrat intelligent de waqf num\\u00e9rique

## 📖 Description
Ce contrat intelligent impl\\u00e9mente un **waqf num\\u00e9rique** (fondation islamique de bienfaisance) pour la gestion d'actifs logistiques en M\\u00e9diterran\\u00e9e. Il permet de collecter les frais g\\u00e9n\\u00e9r\\u00e9s par les infrastructures (ports, routes, hubs) et de les redistribuer aux b\\u00e9n\\u00e9ficiaires selon des proportions d\\u00e9finies.

## 🏛️ Architecture

### Acteurs
- **Naqib** : Gestionnaire du waqf (adresse : `{self.naqib}`)
- **B\\u00e9n\\u00e9ficiaires** : Organisations recevant les redistributions

### Biens g\\u00e9r\\u00e9s
"""
        for bien in self.biens:
            readme += f"\n- **{bien['id']}** : {bien['nom']} → {bien['beneficiaire']}"
        
        readme += "\n\n### B\\u00e9n\\u00e9ficiaires et parts\n"
        for benef in self.beneficiaires:
            readme += f"\n- **{benef['nom']}** : {benef['part']}% (adresse : {benef['adresse']})"
        
        readme += f"""

## ⚙️ Fonctionnalit\\u00e9s principales

1. **`ajouterBien(string _id, string _nom, address _beneficiaire)`**  
   Ajoute un nouveau bien au waqf. (R\\u00e9serv\\u00e9 au naqib)

2. **`recevoirFrais() payable`**  
   Re\\u00e7oit les frais g\\u00e9n\\u00e9r\\u00e9s par les biens (en monnaie X).

3. **`redistribuerRevenus()`**  
   Redistribue les frais collect\\u00e9s aux b\\u00e9n\\u00e9ficiaires selon leurs parts.  
   \\u00c9met l'\\u00e9v\\u00e9nement `RedistributionEffectuee`.

4. **`modifierPart(address _beneficiaire, uint256 _nouvellePart)`**  
   Modifie la part d'un b\\u00e9n\\u00e9ficiaire. (R\\u00e9serv\\u00e9 au naqib)

5. **`recupererFonds()`**  
   Permet au naqib de r\\u00e9cup\\u00e9rer les fonds en cas d'urgence.

## 🚀 D\\u00e9ploiement sur testnet

### Pr\\u00e9requis
- Node.js (v16+) et npm
- Hardhat ou Truffle
- Wallet connect\\u00e9 (MetaMask)

### \\u00c9tapes de d\\u00e9ploiement (Sepolia)

```bash
# 1. Installation des d\\u00e9pendances
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox

# 2. Cr\\u00e9ation du projet
npx hardhat init

# 3. Copier le contrat dans contracts/{self.nom_waqf}.sol

# 4. D\\u00e9ploiement
npx hardhat run scripts/deploy.js --network sepolia
        Script de d\u00e9ploiement (deploy.js)
const hre = require("hardhat");

async function main() {{
  const Waqf = await hre.ethers.getContractFactory("{self.nom_waqf}");
  const waqf = await Waqf.deploy("{self.nom_waqf}", "{self.naqib}");
  await waqf.waitForDeployment();
  console.log("Waqf d\\u00e9ploy\\u00e9 \\u00e0 :", await waqf.getAddress());
}}

main().catch((error) => {{
  console.error(error);
  process.exitCode = 1;
}});
Int\u00e9gration avec la monnaie X
Le contrat est con\u00e7u pour fonctionner avec une monnaie commune X (RUB + UAH + GEL + TRY). Les frais sont collect\u00e9s en monnaie X et redistribu\u00e9s aux b\u00e9n\u00e9ficiaires.

    📊 Exemple d'utilisation
// 1. Ajouter un bien
await waqf.ajouterBien("B001", "Port de Bizerte", "0x111...");

// 2. Recevoir des frais
await waqf.recevoirFrais({{value: ethers.parseEther("100")}});

// 3. Redistribuer
await waqf.redistribuerRevenus();

// 4. Consulter l'\\u00e9tat
const total = await waqf.obtenirMontantTotal();
console.log("Total des frais :", total);
🔐 S\u00e9curit\u00e9
SeulementNaqib : Modificateur pour restreindre les actions administratives

V\u00e9rification des entr\u00e9es : Validation des adresses et des montants

\u00c9v\u00e9nements : Tra\u00e7abilit\u00e9 compl\u00e8te des actions

📝 Licence
MIT - Open source

📅 G\u00e9n\u00e9r\u00e9 le {datetime.now().strftime('%d/%m/%Y')}
Documentation g\u00e9n\u00e9r\u00e9e automatiquement par DeerFlow
"""
return readme

def generer_script_deploiement(self) -> str:
"""
Génère le script de déploiement Hardhat

Returns:
Script JavaScript de déploiement
"""
return f"""// scripts/deploy_{self.nom_waqf}.js
const hre = require("hardhat");

async function main() {{
console.log("D\u00e9ploiement du contrat {self.nom_waqf}...");

const Waqf = await hre.ethers.getContractFactory("{self.nom_waqf}");
const waqf = await Waqf.deploy("{self.nom_waqf}", "{self.naqib}");

await waqf.waitForDeployment();
const address = await waqf.getAddress();

console.log("✅ {self.nom_waqf} d\u00e9ploy\u00e9 \u00e0 :", address);

// Sauvegarde de l'adresse
const fs = require("fs");
const deploymentInfo = {{
contract: "{self.nom_waqf}",
address: address,
naqib: "{self.naqib}",
network: hre.network.name,
timestamp: new Date().toISOString()
}};

fs.writeFileSync(
deployments/{self.nom_waqf}_${{hre.network.name}}.json,
JSON.stringify(deploymentInfo, null, 2)
);

console.log("📝 Informations sauvegard\u00e9es dans deployments/");
}}

main().catch((error) => {{
console.error(error);
process.exitCode = 1;
}});
"""

def generer_hardhat_config(self) -> str:
"""
Génère la configuration Hardhat

Returns:
Configuration Hardhat
"""
return """// hardhat.config.js
require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
solidity: "0.8.19",
networks: {
sepolia: {
url: process.env.SEPOLIA_RPC_URL || "",
accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
},
polygon: {
url: process.env.POLYGON_RPC_URL || "",
accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
},
},
etherscan: {
apiKey: {
sepolia: process.env.ETHERSCAN_API_KEY || "",
polygon: process.env.POLYGONSCAN_API_KEY || "",
},
},
};
"""

def generer_json_abi(self) -> Dict[str, Any]:
"""
Génère une représentation JSON du contrat

Returns:
Dictionnaire représentant le contrat
"""
return {
"contractName": self.nom_waqf,
"abi": [
{
"type": "constructor",
"inputs": [
{"name": "_nom", "type": "string"},
{"name": "_naqib", "type": "address"}
]
},
{
"type": "function",
"name": "ajouterBien",
"inputs": [
{"name": "_id", "type": "string"},
{"name": "_nom", "type": "string"},
{"name": "_beneficiaire", "type": "address"}
],
"outputs": [],
"stateMutability": "nonpayable"
},
{
"type": "function",
"name": "recevoirFrais",
"inputs": [],
"outputs": [],
"stateMutability": "payable"
},
{
"type": "function",
"name": "redistribuerRevenus",
"inputs": [],
"outputs": [],
"stateMutability": "nonpayable"
},
{
"type": "function",
"name": "modifierPart",
"inputs": [
{"name": "_beneficiaire", "type": "address"},
{"name": "_nouvellePart", "type": "uint256"}
],
"outputs": [],
"stateMutability": "nonpayable"
},
{
"type": "function",
"name": "recupererFonds",
"inputs": [],
"outputs": [],
"stateMutability": "nonpayable"
}
],
"beneficiaires": self.beneficiaires,
"biens": self.biens,
"naqib": self.naqib,
"date_generation": datetime.now().isoformat()
}

def generer_tous_fichiers(self):
"""
Génère tous les fichiers du projet waqf
"""
try:

1. Contrat Solidity
contrat = self.generer_contrat_solidity()
with open(f'contracts/{self.nom_waqf}.sol', 'w', encoding='utf-8') as f:
f.write(contrat)
logger.info(f"Contrat sauvegardé : contracts/{self.nom_waqf}.sol")

2. README
readme = self.generer_readme()
with open('docs/README_waqf.md', 'w', encoding='utf-8') as f:
f.write(readme)
logger.info("README sauvegardé : docs/README_waqf.md")

3. Script de déploiement
deploy_script = self.generer_script_deploiement()
os.makedirs('scripts', exist_ok=True)
with open(f'scripts/deploy_{self.nom_waqf}.js', 'w', encoding='utf-8') as f:
f.write(deploy_script)
logger.info(f"Script de déploiement sauvegardé : scripts/deploy_{self.nom_waqf}.js")

4. Configuration Hardhat
hardhat_config = self.generer_hardhat_config()
with open('hardhat.config.js', 'w', encoding='utf-8') as f:
f.write(hardhat_config)
logger.info("Configuration Hardhat sauvegardée : hardhat.config.js")

5. JSON ABI
json_data = self.generer_json_abi()
with open('contracts/waqf_abi.json', 'w', encoding='utf-8') as f:
json.dump(json_data, f, indent=2, ensure_ascii=False)
logger.info("JSON ABI sauvegardé : contracts/waqf_abi.json")

print("\n" + "="60)
print("✅ OPTION 3 TERMINÉE AVEC SUCCÈS")
print("="60)
print(f" - Contrat : contracts/{self.nom_waqf}.sol")
print(f" - README : docs/README_waqf.md")
print(f" - Script déploiement : scripts/deploy_{self.nom_waqf}.js")
print(f" - Hardhat config : hardhat.config.js")
print(f" - JSON ABI : contracts/waqf_abi.json")

logger.info("✅ Génération terminée avec succès !")

except Exception as e:
logger.error(f"Erreur lors de la génération : {str(e)}")
raise

def main():
"""Fonction principale"""

Chargement de la configuration depuis un fichier YAML si existant
config = None
if os.path.exists('config.yaml'):
with open('config.yaml', 'r', encoding='utf-8') as f:
config = yaml.safe_load(f)
config = config.get('option3', {})

generator = WaqfGenerator(config)
generator.generer_tous_fichiers()

if name == "main":
main()
