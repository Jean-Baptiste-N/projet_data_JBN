with calculs AS(
    SELECT
    niveau,
    cle_unique,
    pathologie,
    code_pathologie,
    nom_pathologie,
    departement,
    code_departement,
    nom_departement,
    ROUND(safe_divide(hospi_total_24h_2019 - hospi_total_24h_2018,hospi_total_24h_2018) ,2) as evolution_2019_hospi_total_24h,
    ROUND(safe_divide(hospi_total_jj_2019 - hospi_total_jj_2018,hospi_total_jj_2018) ,2) as evolution_2019_hospi_total_jj,
    ROUND(safe_divide(total_hospi_2019 - total_hospi_2018,total_hospi_2018) ,2) as evolution_2019_total_hospi,
    ROUND(safe_divide(AVG_duree_hospi_2019 - AVG_duree_hospi_2018,AVG_duree_hospi_2018) ,2) as evolution_2019_AVG_duree_hospi,
    ROUND(safe_divide(hospi_total_24h_2020 - hospi_total_24h_2019,hospi_total_24h_2019) ,2) as evolution_2020_hospi_total_24h,
    ROUND(safe_divide(hospi_total_jj_2020 - hospi_total_jj_2019,hospi_total_jj_2019) ,2) as evolution_2020_hospi_total_jj,
    ROUND(safe_divide(total_hospi_2020 - total_hospi_2019,total_hospi_2019) ,2) as evolution_2020_total_hospi,
    ROUND(safe_divide(AVG_duree_hospi_2020 - AVG_duree_hospi_2019,AVG_duree_hospi_2019) ,2) as evolution_2020_AVG_duree_hospi,
    ROUND(safe_divide(hospi_total_24h_2021 - hospi_total_24h_2020,hospi_total_24h_2020) ,2) as evolution_2021_hospi_total_24h,
    ROUND(safe_divide(hospi_total_jj_2021 - hospi_total_jj_2020,hospi_total_jj_2020) ,2) as evolution_2021_hospi_total_jj,
    ROUND(safe_divide(total_hospi_2021 - total_hospi_2020,total_hospi_2020) ,2) as evolution_2021_total_hospi,
    ROUND(safe_divide(AVG_duree_hospi_2021 - AVG_duree_hospi_2020,AVG_duree_hospi_2020) ,2) as evolution_2021_AVG_duree_hospi,
    ROUND(safe_divide(hospi_total_24h_2022 - hospi_total_24h_2021,hospi_total_24h_2021) ,2) as evolution_2022_hospi_total_24h,
    ROUND(safe_divide(hospi_total_jj_2022 - hospi_total_jj_2021,hospi_total_jj_2021) ,2) as evolution_2022_hospi_total_jj,
    ROUND(safe_divide(total_hospi_2022 - total_hospi_2021,total_hospi_2021) ,2) as evolution_2022_total_hospi,
    ROUND(safe_divide(AVG_duree_hospi_2022 - AVG_duree_hospi_2021,AVG_duree_hospi_2021) ,2) as evolution_2022_AVG_duree_hospi,
    ROUND(safe_divide(hospi_total_24h_2022 - hospi_total_24h_2018,hospi_total_24h_2018) ,2) as evolution_4ans_hospi_total_24h,
    ROUND(safe_divide(hospi_total_jj_2022 - hospi_total_jj_2018,hospi_total_jj_2018) ,2) as evolution_4ans_hospi_total_jj,
    ROUND(safe_divide(total_hospi_2022 - total_hospi_2018,total_hospi_2018) ,2) as evolution_4ans_total_hospi,
    ROUND(safe_divide(AVG_duree_hospi_2022 - AVG_duree_hospi_2018,AVG_duree_hospi_2018) ,2) as evolution_4ans_AVG_duree_hospi

FROM {{ref("int_duree_sejours_dpt_ens_par_annee")}}
)

SELECT 
    t1.* 
    ,classification
FROM calculs AS t1
LEFT JOIN {{ref("stg_morbidite_h__class_services")}} c2
ON t1.nom_pathologie = c2.pathologie


