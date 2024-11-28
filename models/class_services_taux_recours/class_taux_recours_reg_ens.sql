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
        region,
        code_region,
        nom_region,
        tx_brut_tt_age_pour_mille,
        tx_standard_tt_age_pour_mille,
        indice_comparatif_tt_age_percent,
        classification
    FROM {{ref("int_taux_recours_reg_ens")}} t1
    LEFT JOIN {{ref("stg_morbidite_h__class_services")}} c2
    ON t1.nom_pathologie = c2.pathologie
)
SELECT 
    niveau,
    CONCAT(region ,"_", annee ,"_", classification) AS cle_unique,
    year,
    annee,
    region,
    code_region,
    nom_region,
    classification,
    ROUND(AVG(tx_brut_tt_age_pour_mille),2) AS tx_brut_tt_age_pour_mille,
    ROUND(AVG(tx_standard_tt_age_pour_mille),2) AS tx_standard_tt_age_pour_mille,
    ROUND(AVG(indice_comparatif_tt_age_percent),2) AS indice_comparatif_tt_age_percent
FROM joined
GROUP BY niveau,
    cle_unique,
    year,
    annee,
    region,
    code_region,
    nom_region,
    classification
ORDER BY cle_unique