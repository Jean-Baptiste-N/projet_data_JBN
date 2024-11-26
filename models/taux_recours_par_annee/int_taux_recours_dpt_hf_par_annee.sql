WITH T2018 AS (
    SELECT 
        cle_unique,
        tx_brut_tt_age_pour_mille AS tx_brut_tt_age_pour_mille_2018,
        tx_standard_tt_age_pour_mille AS tx_standard_tt_age_pour_mille_2018,
        indice_comparatif_tt_age_percent AS indice_comparatif_tt_age_percent_2018
    FROM {{ ref("int_taux_recours_dpt_hf") }}
    WHERE year = "2018-12-31"
),
T2019 AS (
    SELECT 
        cle_unique,
        tx_brut_tt_age_pour_mille AS tx_brut_tt_age_pour_mille_2019,
        tx_standard_tt_age_pour_mille AS tx_standard_tt_age_pour_mille_2019,
        indice_comparatif_tt_age_percent AS indice_comparatif_tt_age_percent_2019
    FROM {{ ref("int_taux_recours_dpt_hf") }}
    WHERE year = "2019-12-31"
),
T2020 AS (
    SELECT 
        cle_unique,
        tx_brut_tt_age_pour_mille AS tx_brut_tt_age_pour_mille_2020,
        tx_standard_tt_age_pour_mille AS tx_standard_tt_age_pour_mille_2020,
        indice_comparatif_tt_age_percent AS indice_comparatif_tt_age_percent_2020
    FROM {{ ref("int_taux_recours_dpt_hf") }}
    WHERE year = "2020-12-31"
),
T2021 AS (
    SELECT 
        cle_unique,
        tx_brut_tt_age_pour_mille AS tx_brut_tt_age_pour_mille_2021,
        tx_standard_tt_age_pour_mille AS tx_standard_tt_age_pour_mille_2021,
        indice_comparatif_tt_age_percent AS indice_comparatif_tt_age_percent_2021
    FROM {{ ref("int_taux_recours_dpt_hf") }}
    WHERE year = "2021-12-31"
),
T2022 AS (
    SELECT 
        cle_unique,
        tx_brut_tt_age_pour_mille AS tx_brut_tt_age_pour_mille_2022,
        tx_standard_tt_age_pour_mille AS tx_standard_tt_age_pour_mille_2022,
        indice_comparatif_tt_age_percent AS indice_comparatif_tt_age_percent_2022
    FROM {{ ref("int_taux_recours_dpt_hf") }}
    WHERE year = "2022-12-31"
),
inner1 AS (
    SELECT DISTINCT 
        niveau,
        cle_unique,
        sexe,
        pathologie,
        code_pathologie,
        nom_pathologie,
        region,
        code_departement,
        nom_departement,
        tx_brut_tt_age_pour_mille_2018,
        tx_standard_tt_age_pour_mille_2018,
        indice_comparatif_tt_age_percent_2018
    FROM {{ ref("int_taux_recours_dpt_hf") }}
    INNER JOIN T2018
    USING (cle_unique)
),
inner2 AS (
    SELECT DISTINCT 
        niveau,
        cle_unique,
        sexe,
        pathologie,
        code_pathologie,
        nom_pathologie,
        region,
        code_departement,
        nom_departement,
        tx_brut_tt_age_pour_mille_2018,
        tx_standard_tt_age_pour_mille_2018,
        indice_comparatif_tt_age_percent_2018,
        tx_brut_tt_age_pour_mille_2019,
        tx_standard_tt_age_pour_mille_2019,
        indice_comparatif_tt_age_percent_2019
    FROM inner1
    INNER JOIN T2019 USING (cle_unique)
),
inner3 AS (
    SELECT DISTINCT 
        niveau,
        cle_unique,
        sexe,
        pathologie,
        code_pathologie,
        nom_pathologie,
        region,
        code_departement,
        nom_departement,
        tx_brut_tt_age_pour_mille_2018,
        tx_standard_tt_age_pour_mille_2018,
        indice_comparatif_tt_age_percent_2018,
        tx_brut_tt_age_pour_mille_2019,
        tx_standard_tt_age_pour_mille_2019,
        indice_comparatif_tt_age_percent_2019,
        tx_brut_tt_age_pour_mille_2020,
        tx_standard_tt_age_pour_mille_2020,
        indice_comparatif_tt_age_percent_2020
    FROM inner2
    INNER JOIN T2020 USING (cle_unique)
),
inner4 AS (
    SELECT DISTINCT 
        niveau,
        cle_unique,
        sexe,
        pathologie,
        code_pathologie,
        nom_pathologie,
        region,
        code_departement,
        nom_departement,
        tx_brut_tt_age_pour_mille_2018,
        tx_standard_tt_age_pour_mille_2018,
        indice_comparatif_tt_age_percent_2018,
        tx_brut_tt_age_pour_mille_2019,
        tx_standard_tt_age_pour_mille_2019,
        indice_comparatif_tt_age_percent_2019,
        tx_brut_tt_age_pour_mille_2020,
        tx_standard_tt_age_pour_mille_2020,
        indice_comparatif_tt_age_percent_2020,
        tx_brut_tt_age_pour_mille_2021,
        tx_standard_tt_age_pour_mille_2021,
        indice_comparatif_tt_age_percent_2021
    FROM inner3
    INNER JOIN T2021 USING (cle_unique)
)

SELECT DISTINCT 
    niveau,
    cle_unique,
    sexe,
    pathologie,
    code_pathologie,
    nom_pathologie,
    region,
    code_departement,
    nom_departement,
    tx_brut_tt_age_pour_mille_2018,
    tx_standard_tt_age_pour_mille_2018,
    indice_comparatif_tt_age_percent_2018,
    tx_brut_tt_age_pour_mille_2019,
    tx_standard_tt_age_pour_mille_2019,
    indice_comparatif_tt_age_percent_2019,
    tx_brut_tt_age_pour_mille_2020,
    tx_standard_tt_age_pour_mille_2020,
    indice_comparatif_tt_age_percent_2020,
    tx_brut_tt_age_pour_mille_2021,
    tx_standard_tt_age_pour_mille_2021,
    indice_comparatif_tt_age_percent_2021,
    tx_brut_tt_age_pour_mille_2022,
    tx_standard_tt_age_pour_mille_2022,
    indice_comparatif_tt_age_percent_2022
FROM inner4
INNER JOIN T2022 USING (cle_unique)
ORDER BY cle_unique
