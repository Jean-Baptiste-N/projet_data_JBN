WITH calculs as (
    SELECT
    niveau,
    cle_unique,
    sexe,
    pathologie,
    code_pathologie,
    nom_pathologie,
    region,
    code_region,
    nom_region,
    ROUND(safe_divide(nbr_hospi_2019 - nbr_hospi_2018,nbr_hospi_2018) ,2) as evolution_2019_nbr_hospi,
    ROUND(safe_divide(nbr_hospi_2020 - nbr_hospi_2019,nbr_hospi_2019) ,2) as evolution_2020_nbr_hospi,
    ROUND(safe_divide(nbr_hospi_2021 - nbr_hospi_2020,nbr_hospi_2020) ,2) as evolution_2021_nbr_hospi,
    ROUND(safe_divide(nbr_hospi_2022 - nbr_hospi_2021,nbr_hospi_2021) ,2) as evolution_2022_nbr_hospi,
    ROUND(safe_divide(nbr_hospi_2022 - nbr_hospi_2018,nbr_hospi_2018) ,2) as evolution_4ans_nbr_hospi,

FROM {{ref("int_nbr_hospi_reg_ens_par_annee")}}


)

SELECT 
    t1.* 
    ,classification
FROM calculs AS t1
LEFT JOIN {{ref("stg_morbidite_h__class_services")}} c2
ON t1.nom_pathologie = c2.pathologie