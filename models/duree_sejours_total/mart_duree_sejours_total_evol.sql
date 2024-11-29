WITH base_data AS (
    SELECT 
        *,
        SUM(hospi_total_24h) OVER (PARTITION BY annee, region, pathologie, code_region, nom_region) AS hospi_total_24h1
        ,SUM(hospi_total_jj) OVER (PARTITION BY annee, region, pathologie, code_region, nom_region) AS hospi_total_jj1
        ,SUM(total_hospi) OVER (PARTITION BY annee, region, pathologie, code_region, nom_region) AS total_hospi2
        ,AVG(AVG_duree_hospi) OVER (PARTITION BY annee, region, pathologie, code_region, nom_region) AS AVG_duree_hospi1
    FROM {{ref("int_duree_sejours_total")}}
),
evolution_data AS (
    SELECT 
        bd1.*,
        bd1.hospi_total_24h1 - COALESCE(bd2.hospi_total_24h1, 0) AS evolution_hospi_total_24h1,
        CASE 
            WHEN COALESCE(bd2.hospi_total_24h1, 0) = 0 THEN NULL 
            ELSE Round(safe_divide((bd1.hospi_total_24h1 - bd2.hospi_total_24h1) , bd2.hospi_total_24h1), 2)  
        END AS evolution_percent_hospi_total_24h1,
        bd1.hospi_total_jj1 - COALESCE(bd2.hospi_total_jj1, 0) AS evolution_hospi_total_jj1,
        CASE 
            WHEN COALESCE(bd2.hospi_total_jj1, 0) = 0 THEN NULL 
            ELSE Round(safe_divide((bd1.hospi_total_jj1 - bd2.hospi_total_jj1) , bd2.hospi_total_jj1), 2)  
        END AS evolution_percent_hospi_total_jj1,
        bd1.total_hospi2 - COALESCE(bd2.total_hospi2, 0) AS evolution_total_hospi2,
        CASE 
            WHEN COALESCE(bd2.total_hospi2, 0) = 0 THEN NULL 
            ELSE Round(safe_divide((bd1.total_hospi2 - bd2.total_hospi2) , bd2.total_hospi2), 2)  
        END AS evolution_percent_total_hospi2,
        round(bd1.AVG_duree_hospi1 - COALESCE(bd2.AVG_duree_hospi1, 0),2) AS evolution_AVG_duree_hospi1,
        CASE 
            WHEN COALESCE(bd2.AVG_duree_hospi1, 0) = 0 THEN NULL 
            ELSE Round(safe_divide((bd1.AVG_duree_hospi1 - bd2.AVG_duree_hospi1) , bd2.AVG_duree_hospi1), 2)  
        END AS evolution_percent_AVG_duree_hospi1
    FROM base_data bd1
    LEFT JOIN base_data bd2 
        ON bd1.region = bd2.region
        AND bd1.pathologie = bd2.pathologie
        AND bd1.code_region = bd2.code_region
        AND bd1.nom_region = bd2.nom_region
        AND bd1.annee = bd2.annee + 1
)
SELECT * 
FROM evolution_data
ORDER BY region, pathologie, annee
