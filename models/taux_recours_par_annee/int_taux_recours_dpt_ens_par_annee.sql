WITH transposed_data AS (
    SELECT 
        cle_unique,
        niveau,
        sexe,
        pathologie,
        code_pathologie,
        nom_pathologie,
        region,
        code_departement,
        nom_departement,
        -- Utilisation de CASE WHEN pour chaque métrique et année
        CASE WHEN year = '2018-12-31' THEN tx_brut_tt_age_pour_mille END AS tx_brut_tt_age_pour_mille_2018,
        CASE WHEN year = '2018-12-31' THEN tx_standard_tt_age_pour_mille END AS tx_standard_tt_age_pour_mille_2018,
        CASE WHEN year = '2018-12-31' THEN indice_comparatif_tt_age_percent END AS indice_comparatif_tt_age_percent_2018,
        CASE WHEN year = '2019-12-31' THEN tx_brut_tt_age_pour_mille END AS tx_brut_tt_age_pour_mille_2019,
        CASE WHEN year = '2019-12-31' THEN tx_standard_tt_age_pour_mille END AS tx_standard_tt_age_pour_mille_2019,
        CASE WHEN year = '2019-12-31' THEN indice_comparatif_tt_age_percent END AS indice_comparatif_tt_age_percent_2019,
        CASE WHEN year = '2020-12-31' THEN tx_brut_tt_age_pour_mille END AS tx_brut_tt_age_pour_mille_2020,
        CASE WHEN year = '2020-12-31' THEN tx_standard_tt_age_pour_mille END AS tx_standard_tt_age_pour_mille_2020,
        CASE WHEN year = '2020-12-31' THEN indice_comparatif_tt_age_percent END AS indice_comparatif_tt_age_percent_2020,
        CASE WHEN year = '2021-12-31' THEN tx_brut_tt_age_pour_mille END AS tx_brut_tt_age_pour_mille_2021,
        CASE WHEN year = '2021-12-31' THEN tx_standard_tt_age_pour_mille END AS tx_standard_tt_age_pour_mille_2021,
        CASE WHEN year = '2021-12-31' THEN indice_comparatif_tt_age_percent END AS indice_comparatif_tt_age_percent_2021,
        CASE WHEN year = '2022-12-31' THEN tx_brut_tt_age_pour_mille END AS tx_brut_tt_age_pour_mille_2022,
        CASE WHEN year = '2022-12-31' THEN tx_standard_tt_age_pour_mille END AS tx_standard_tt_age_pour_mille_2022,
        CASE WHEN year = '2022-12-31' THEN indice_comparatif_tt_age_percent END AS indice_comparatif_tt_age_percent_2022
    FROM {{ ref("int_taux_recours_dpt_ens") }}
)
SELECT
    cle_unique,
    niveau,
    sexe,
    pathologie,
    code_pathologie,
    nom_pathologie,
    region,
    code_departement,
    nom_departement,
    MAX(tx_brut_tt_age_pour_mille_2018) AS tx_brut_tt_age_pour_mille_2018,
    MAX(tx_standard_tt_age_pour_mille_2018) AS tx_standard_tt_age_pour_mille_2018,
    MAX(indice_comparatif_tt_age_percent_2018) AS indice_comparatif_tt_age_percent_2018,
    MAX(tx_brut_tt_age_pour_mille_2019) AS tx_brut_tt_age_pour_mille_2019,
    MAX(tx_standard_tt_age_pour_mille_2019) AS tx_standard_tt_age_pour_mille_2019,
    MAX(indice_comparatif_tt_age_percent_2019) AS indice_comparatif_tt_age_percent_2019,
    MAX(tx_brut_tt_age_pour_mille_2020) AS tx_brut_tt_age_pour_mille_2020,
    MAX(tx_standard_tt_age_pour_mille_2020) AS tx_standard_tt_age_pour_mille_2020,
    MAX(indice_comparatif_tt_age_percent_2020) AS indice_comparatif_tt_age_percent_2020,
    MAX(tx_brut_tt_age_pour_mille_2021) AS tx_brut_tt_age_pour_mille_2021,
    MAX(tx_standard_tt_age_pour_mille_2021) AS tx_standard_tt_age_pour_mille_2021,
    MAX(indice_comparatif_tt_age_percent_2021) AS indice_comparatif_tt_age_percent_2021,
    MAX(tx_brut_tt_age_pour_mille_2022) AS tx_brut_tt_age_pour_mille_2022,
    MAX(tx_standard_tt_age_pour_mille_2022) AS tx_standard_tt_age_pour_mille_2022,
    MAX(indice_comparatif_tt_age_percent_2022) AS indice_comparatif_tt_age_percent_2022
FROM transposed_data
GROUP BY cle_unique, niveau, sexe, pathologie, code_pathologie, nom_pathologie, region, code_departement, nom_departement
ORDER BY cle_unique


