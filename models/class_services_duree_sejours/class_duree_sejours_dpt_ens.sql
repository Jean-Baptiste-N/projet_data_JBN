WITH joined as(
    SELECT
        niveau,
        cle_unique,
        year,
        annee,        
        t1.pathologie,
        code_pathologie,
        nom_pathologie,
        departement,
        code_departement,
        nom_departement,
        hospi_total_24h,
        hospi_total_jj,
        total_hospi,
        AVG_duree_hospi,
        classification
    FROM {{ref("int_duree_sejours_dpt_ens")}} t1
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
    SUM(hospi_total_24h) AS hospi_total_24h,
    SUM(hospi_total_jj) AS hospi_total_jj,
    SUM(total_hospi) AS total_hospi,
    ROUND(AVG(AVG_duree_hospi),2) AS AVG_duree_hospi
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