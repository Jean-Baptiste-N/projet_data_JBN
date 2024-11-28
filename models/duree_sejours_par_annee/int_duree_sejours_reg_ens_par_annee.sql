WITH transposed_data AS (
    SELECT 
        niveau,
        CONCAT(region,"_",code_pathologie) as cle_unique,
        pathologie,
        code_pathologie,
        nom_pathologie,
        region,
        code_region,
        nom_region,
        -- Utilisation de CASE WHEN pour chaque métrique et année
        CASE WHEN year = '2018-12-31' THEN hospi_total_24h END AS hospi_total_24h_2018,
        CASE WHEN year = '2018-12-31' THEN hospi_total_jj END AS hospi_total_jj_2018,
        CASE WHEN year = '2018-12-31' THEN total_hospi END AS total_hospi_2018,
        CASE WHEN year = '2018-12-31' THEN AVG_duree_hospi END AS AVG_duree_hospi_2018,
        CASE WHEN year = '2019-12-31' THEN hospi_total_24h END AS hospi_total_24h_2019,
        CASE WHEN year = '2019-12-31' THEN hospi_total_jj END AS hospi_total_jj_2019,
        CASE WHEN year = '2019-12-31' THEN total_hospi END AS total_hospi_2019,
        CASE WHEN year = '2019-12-31' THEN AVG_duree_hospi END AS AVG_duree_hospi_2019,
        CASE WHEN year = '2020-12-31' THEN hospi_total_24h END AS hospi_total_24h_2020,
        CASE WHEN year = '2020-12-31' THEN hospi_total_jj END AS hospi_total_jj_2020,
        CASE WHEN year = '2020-12-31' THEN total_hospi END AS total_hospi_2020,
        CASE WHEN year = '2020-12-31' THEN AVG_duree_hospi END AS AVG_duree_hospi_2020,
        CASE WHEN year = '2021-12-31' THEN hospi_total_24h END AS hospi_total_24h_2021,
        CASE WHEN year = '2021-12-31' THEN hospi_total_jj END AS hospi_total_jj_2021,
        CASE WHEN year = '2021-12-31' THEN total_hospi END AS total_hospi_2021,
        CASE WHEN year = '2021-12-31' THEN AVG_duree_hospi END AS AVG_duree_hospi_2021,
        CASE WHEN year = '2022-12-31' THEN hospi_total_24h END AS hospi_total_24h_2022,
        CASE WHEN year = '2022-12-31' THEN hospi_total_jj END AS hospi_total_jj_2022,
        CASE WHEN year = '2022-12-31' THEN total_hospi END AS total_hospi_2022,
        CASE WHEN year = '2022-12-31' THEN AVG_duree_hospi END AS AVG_duree_hospi_2022
    FROM {{ ref("int_duree_sejours_reg_ens") }}
)
SELECT
    niveau,
    cle_unique,
    pathologie,
    code_pathologie,
    nom_pathologie,
    region,
    code_region,
    nom_region,
    MAX(hospi_total_24h_2018) AS hospi_total_24h_2018,
    MAX(hospi_total_jj_2018) AS hospi_total_jj_2018,
    MAX(total_hospi_2018) AS total_hospi_2018,
    MAX(AVG_duree_hospi_2018) AS AVG_duree_hospi_2018,
    MAX(hospi_total_24h_2019) AS hospi_total_24h_2019,
    MAX(hospi_total_jj_2019) AS hospi_total_jj_2019,
    MAX(total_hospi_2019) AS total_hospi_2019,
    MAX(AVG_duree_hospi_2019) AS AVG_duree_hospi_2019,
    MAX(hospi_total_24h_2020) AS hospi_total_24h_2020,
    MAX(hospi_total_jj_2020) AS hospi_total_jj_2020,
    MAX(total_hospi_2020) AS total_hospi_2020,
    MAX(AVG_duree_hospi_2020) AS AVG_duree_hospi_2020,
    MAX(hospi_total_24h_2021) AS hospi_total_24h_2021,
    MAX(hospi_total_jj_2021) AS hospi_total_jj_2021,
    MAX(total_hospi_2021) AS total_hospi_2021,
    MAX(AVG_duree_hospi_2021) AS AVG_duree_hospi_2021,
    MAX(hospi_total_24h_2022) AS hospi_total_24h_2022,
    MAX(hospi_total_jj_2022) AS hospi_total_jj_2022,
    MAX(total_hospi_2022) AS total_hospi_2022,
    MAX(AVG_duree_hospi_2022) AS AVG_duree_hospi_2022
FROM transposed_data
GROUP BY niveau, cle_unique, pathologie, code_pathologie, nom_pathologie, region, code_region, nom_region
ORDER BY cle_unique


