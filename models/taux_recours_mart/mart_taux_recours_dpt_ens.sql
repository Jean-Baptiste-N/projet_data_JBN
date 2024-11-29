WITH calculs as (
    SELECT
    niveau,
    cle_unique,
    sexe,
    pathologie,
    code_pathologie,
    nom_pathologie,
    departement,
    code_departement,
    nom_departement,
    ROUND(safe_divide(tx_brut_tt_age_pour_mille_2019 - tx_brut_tt_age_pour_mille_2018,tx_brut_tt_age_pour_mille_2018) ,2) as permille_evolution_2019_tx_brut_tt_age,
    ROUND(safe_divide(tx_standard_tt_age_pour_mille_2019 - tx_standard_tt_age_pour_mille_2018,tx_standard_tt_age_pour_mille_2018) ,2) as permille_evolution_2019_tx_standard_tt_age,
    ROUND(safe_divide(indice_comparatif_tt_age_percent_2019 - indice_comparatif_tt_age_percent_2018,indice_comparatif_tt_age_percent_2018) ,2) as percent_evolution_2019_indice_comparatif_tt_age,
    ROUND(safe_divide(tx_brut_tt_age_pour_mille_2020 - tx_brut_tt_age_pour_mille_2019,tx_brut_tt_age_pour_mille_2019) ,2) as permille_evolution_2020_tx_brut_tt_age,
    ROUND(safe_divide(tx_standard_tt_age_pour_mille_2020 - tx_standard_tt_age_pour_mille_2019,tx_standard_tt_age_pour_mille_2019) ,2) as permille_evolution_2020_tx_standard_tt_age,
    ROUND(safe_divide(indice_comparatif_tt_age_percent_2020 - indice_comparatif_tt_age_percent_2019,indice_comparatif_tt_age_percent_2019) ,2) as percent_evolution_2020_indice_comparatif_tt_age,
    ROUND(safe_divide(tx_brut_tt_age_pour_mille_2021 - tx_brut_tt_age_pour_mille_2020,tx_brut_tt_age_pour_mille_2020) ,2) as permille_evolution_2021_tx_brut_tt_age,
    ROUND(safe_divide(tx_standard_tt_age_pour_mille_2021 - tx_standard_tt_age_pour_mille_2020,tx_standard_tt_age_pour_mille_2020) ,2) as permille_evolution_2021_tx_standard_tt_age,
    ROUND(safe_divide(indice_comparatif_tt_age_percent_2021 - indice_comparatif_tt_age_percent_2020,indice_comparatif_tt_age_percent_2020) ,2) as percent_evolution_2021_indice_comparatif_tt_age,
    ROUND(safe_divide(tx_brut_tt_age_pour_mille_2022 - tx_brut_tt_age_pour_mille_2021,tx_brut_tt_age_pour_mille_2021) ,2) as permille_evolution_2022_tx_brut_tt_age,
    ROUND(safe_divide(tx_standard_tt_age_pour_mille_2022 - tx_standard_tt_age_pour_mille_2021,tx_standard_tt_age_pour_mille_2021) ,2) as permille_evolution_2022_tx_standard_tt_age,
    ROUND(safe_divide(indice_comparatif_tt_age_percent_2022 - indice_comparatif_tt_age_percent_2021,indice_comparatif_tt_age_percent_2021) ,2) as percent_evolution_2022_indice_comparatif_tt_age,
    ROUND(safe_divide(tx_brut_tt_age_pour_mille_2022 - tx_brut_tt_age_pour_mille_2018,tx_brut_tt_age_pour_mille_2018) ,2) as permille_evolution_4ans_tx_brut_tt_age,
    ROUND(safe_divide(tx_standard_tt_age_pour_mille_2022 - tx_standard_tt_age_pour_mille_2018,tx_standard_tt_age_pour_mille_2018) ,2) as permille_evolution_4ans_tx_standard_tt_age,
    ROUND(safe_divide(indice_comparatif_tt_age_percent_2022 - indice_comparatif_tt_age_percent_2018,indice_comparatif_tt_age_percent_2018) ,2) as percent_evolution_4ans_indice_comparatif_tt_age

FROM {{ref("int_taux_recours_dpt_ens_par_annee")}}


)

SELECT 
    t1.* 
    ,classification
FROM calculs AS t1
LEFT JOIN {{ref("stg_morbidite_h__class_services")}} c2
ON t1.nom_pathologie = c2.pathologie