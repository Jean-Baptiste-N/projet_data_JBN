WITH base_data AS (
    SELECT 
        *
        ,AVG(tx_brut_tt_age_pour_mille) OVER (PARTITION BY annee, region, pathologie, code_region, nom_region) AS tx_brut_tt_age_pour_mille1
        ,AVG(tx_standard_tt_age_pour_mille) OVER (PARTITION BY annee, region, pathologie, code_region, nom_region) AS tx_standard_tt_age_pour_mille2
        ,AVG(indice_comparatif_tt_age_percent) OVER (PARTITION BY annee, region, pathologie, code_region, nom_region) AS indice_comparatif_tt_age_percent1
    FROM {{ref("int_taux_recours_total")}}
),
evolution_data AS (
    SELECT 
        bd1.*,
        round(bd1.tx_brut_tt_age_pour_mille1 - COALESCE(bd2.tx_brut_tt_age_pour_mille1, 0),2) AS evolution_tx_brut_tt_age_pour_mille1,
        CASE 
            WHEN COALESCE(bd2.tx_brut_tt_age_pour_mille1, 0) = 0 THEN NULL 
            ELSE Round(safe_divide((bd1.tx_brut_tt_age_pour_mille1 - bd2.tx_brut_tt_age_pour_mille1) , bd2.tx_brut_tt_age_pour_mille1), 2)  
        END AS evolution_percent_tx_brut_tt_age_pour_mille1,
        round(bd1.tx_standard_tt_age_pour_mille2 - COALESCE(bd2.tx_standard_tt_age_pour_mille2, 0),2) AS evolution_tx_standard_tt_age_pour_mille2,
        CASE 
            WHEN COALESCE(bd2.tx_standard_tt_age_pour_mille2, 0) = 0 THEN NULL 
            ELSE Round(safe_divide((bd1.tx_standard_tt_age_pour_mille2 - bd2.tx_standard_tt_age_pour_mille2) , bd2.tx_standard_tt_age_pour_mille2), 2)  
        END AS evolution_percent_tx_standard_tt_age_pour_mille2,
        round(bd1.indice_comparatif_tt_age_percent1 - COALESCE(bd2.indice_comparatif_tt_age_percent1, 0),2) AS evolution_indice_comparatif_tt_age_percent1,
        CASE 
            WHEN COALESCE(bd2.indice_comparatif_tt_age_percent1, 0) = 0 THEN NULL 
            ELSE Round(safe_divide((bd1.indice_comparatif_tt_age_percent1 - bd2.indice_comparatif_tt_age_percent1) , bd2.indice_comparatif_tt_age_percent1), 2)  
        END AS evolution_percent_indice_comparatif_tt_age_percent1
    FROM base_data bd1
    LEFT JOIN base_data bd2 
        ON bd1.region = bd2.region
        AND bd1.pathologie = bd2.pathologie
        AND bd1.code_region = bd2.code_region
        AND bd1.nom_region = bd2.nom_region
        AND bd1.sexe = bd2.sexe
        AND bd1.annee = bd2.annee + 1
)
SELECT * 
FROM evolution_data
ORDER BY region, pathologie, annee
