SELECT 
    niveau,
    CONCAT(region,"_",code_pathologie,"_",sexe) as cle_unique,
    sexe,
    year,
    pathologie,
    code_pathologie,
    nom_pathologie,
    region AS departement,
    code_region AS code_departement,
    nom_region AS nom_departement,
    code_age,
    tranche_age,
    nbr_hospi,
FROM {{ref("stg_morbidite_h__nombre_hospit")}}
WHERE NOT (region LIKE '3 - France%' OR region LIKE '1 - France%')
    AND niveau LIKE "Départements"
    AND nom_pathologie != 'TOTAL TOUTES CAUSES'
    AND (pathologie NOT LIKE '%000%'OR pathologie LIKE "%Covid%")
    AND tranche_age NOT LIKE "Tous âges confondus"
    AND sexe NOT LIKE "Ensemble"
ORDER BY cle_unique