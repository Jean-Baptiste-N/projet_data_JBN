WITH transposed_data AS (
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
        -- Utilisation de CASE WHEN pour chaque métrique et année
        CASE WHEN year = '2018-12-31' THEN tranche_age_tous_ages END AS nbr_hospi_2018,
        CASE WHEN year = '2019-12-31' THEN tranche_age_tous_ages END AS nbr_hospi_2019,
        CASE WHEN year = '2020-12-31' THEN tranche_age_tous_ages END AS nbr_hospi_2020,
        CASE WHEN year = '2021-12-31' THEN tranche_age_tous_ages END AS nbr_hospi_2021,
        CASE WHEN year = '2022-12-31' THEN tranche_age_tous_ages END AS nbr_hospi_2022,
    FROM {{ ref("int_nbr_hospi_reg_hf_par_tranche_age") }}
)
SELECT
    cle_unique,
    niveau,
    sexe,
    pathologie,
    code_pathologie,
    nom_pathologie,
    region,
    code_region,
    nom_region,
    MAX(nbr_hospi_2018) AS nbr_hospi_2018,
    MAX(nbr_hospi_2019) AS nbr_hospi_2019,
    MAX(nbr_hospi_2020) AS nbr_hospi_2020,
    MAX(nbr_hospi_2021) AS nbr_hospi_2021,
    MAX(nbr_hospi_2022) AS nbr_hospi_2022
FROM transposed_data
GROUP BY cle_unique, niveau, sexe, pathologie, code_pathologie, nom_pathologie, region, code_region, nom_region
ORDER BY cle_unique


