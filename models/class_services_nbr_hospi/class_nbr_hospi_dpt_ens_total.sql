WITH joined as(
    SELECT
        niveau,
        cle_unique,
        sexe,
        year,
        EXTRACT(year from year) as annee,
        t1.pathologie,
        code_pathologie,
        nom_pathologie,
        departement,
        code_departement,
        nom_departement,
        tranche_age_tous_ages AS nbr_hospi,
        classification
    FROM {{ref("int_nbr_hospi_dpt_ens_par_tranche_age")}} t1
    LEFT JOIN {{ref("stg_morbidite_h__class_services")}} c2
    ON t1.nom_pathologie = c2.pathologie
)
SELECT 
    niveau,
    CONCAT(departement ,"_", annee ,"_", classification) AS cle_unique,
    year,
    annee,
    departement,
    code_departement,
    nom_departement,
    classification,
    SUM(nbr_hospi) AS nbr_hospi
FROM joined
GROUP BY niveau,
    cle_unique,
    year,
    annee,
    departement,
    code_departement,
    nom_departement,
    classification
ORDER BY cle_unique