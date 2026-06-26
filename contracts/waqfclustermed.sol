contract WaqfClusterMed {
    struct Bien {
        string id;
        string nom;
        address beneficiaire;
        uint256 montant;
        bool actif;
    }
    
    mapping(address => uint256) public parts;
    
    function redistribuerRevenus() public seulementNaqib {
        uint256 montantTotal = totalFrais;
        uint256 totalParts = 0;
        
        for (uint256 i = 0; i < listeBeneficiaires.length; i++) {
            totalParts += parts[listeBeneficiaires[i]];
        }
        
        for (uint256 i = 0; i < listeBeneficiaires.length; i++) {
            address benef = listeBeneficiaires[i];
            uint256 part = (parts[benef] * montantTotal) / totalParts;
            payable(benef).transfer(part);
        }
    }
}
