WITH transposed_data AS (
    SELECT 
        niveau,
        cle_unique,
        sexe,
        year,
        pathologie,
        code_pathologie,
        nom_pathologie,
        departement,
        code_departement,
        nom_departement,
        CASE WHEN code_age = 0 THEN nbr_hospi END AS tranche_age_0_1,
        CASE WHEN code_age = 1 THEN nbr_hospi END AS tranche_age_1_4,
        CASE WHEN code_age = 2 THEN nbr_hospi END AS tranche_age_5_14,
        CASE WHEN code_age = 3 THEN nbr_hospi END AS tranche_age_15_24,
        CASE WHEN code_age = 4 THEN nbr_hospi END AS tranche_age_25_34,
        CASE WHEN code_age = 5 THEN nbr_hospi END AS tranche_age_35_44,
        CASE WHEN code_age = 6 THEN nbr_hospi END AS tranche_age_45_54,
        CASE WHEN code_age = 7 THEN nbr_hospi END AS tranche_age_55_64,
        CASE WHEN code_age = 8 THEN nbr_hospi END AS tranche_age_65_74,
        CASE WHEN code_age = 9 THEN nbr_hospi END AS tranche_age_75_84,
        CASE WHEN code_age = 10 THEN nbr_hospi END AS tranche_age_85_et_plus,
        CASE WHEN code_age = 11 THEN nbr_hospi END AS tranche_age_tous_ages,
    FROM {{ ref("int_nbr_hospi_dpt_hf") }}
)
SELECT
    niveau,
    cle_unique,
    sexe,
    year,
    pathologie,
    code_pathologie,
    nom_pathologie,
    departement,
    code_departement,
    nom_departement,
    MAX(tranche_age_0_1) AS tranche_age_0_1,
    MAX(tranche_age_1_4) AS tranche_age_1_4,
    MAX(tranche_age_5_14) AS tranche_age_5_14,
    MAX(tranche_age_15_24) AS tranche_age_15_24,
    MAX(tranche_age_25_34) AS tranche_age_25_34,
    MAX(tranche_age_35_44) AS tranche_age_35_44,
    MAX(tranche_age_45_54) AS tranche_age_45_54,
    MAX(tranche_age_55_64) AS tranche_age_55_64,
    MAX(tranche_age_65_74) AS tranche_age_65_74,
    MAX(tranche_age_75_84) AS tranche_age_75_84,
    MAX(tranche_age_85_et_plus) AS tranche_age_85_et_plus,
    MAX(tranche_age_tous_ages) AS tranche_age_tous_ages,
FROM transposed_data
GROUP BY cle_unique, niveau, sexe, year, pathologie, code_pathologie, nom_pathologie, departement, code_departement, nom_departement
ORDER BY cle_unique


