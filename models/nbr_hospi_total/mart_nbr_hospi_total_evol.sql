WITH base_data AS (
    SELECT 
        *,
        SUM(nbr_hospi) OVER (PARTITION BY annee, region, pathologie, tranche_age, sexe, code_region, nom_region) AS nbr_hospi1
    FROM {{ref("int_nbr_hospi_total")}}
),
evolution_data AS (
    SELECT 
        bd1.*,
        bd1.nbr_hospi1 - COALESCE(bd2.nbr_hospi1, 0) AS evolution_nbr_hospi1,
        CASE 
            WHEN COALESCE(bd2.nbr_hospi1, 0) = 0 THEN NULL 
            ELSE Round(safe_divide((bd1.nbr_hospi1 - bd2.nbr_hospi1) , bd2.nbr_hospi1), 2)  
        END AS evolution_percent_nbr_hospi1
    FROM base_data bd1
    LEFT JOIN base_data bd2 
        ON bd1.region = bd2.region
        AND bd1.pathologie = bd2.pathologie
        AND bd1.tranche_age = bd2.tranche_age
        AND bd1.sexe = bd2.sexe
        AND bd1.code_region = bd2.code_region
        AND bd1.nom_region = bd2.nom_region
        AND bd1.annee = bd2.annee + 1
)
SELECT * 
FROM evolution_data
ORDER BY region, pathologie, tranche_age, sexe, annee
