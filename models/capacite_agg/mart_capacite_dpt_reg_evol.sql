    WITH base_data AS (
    SELECT
        annee,
        year,
        region,
        code_region,
        nom_region,
        service_medical,
        service_classification,
        lit_hospi_complete,
        sejour_hospi_complete,
        journee_hospi_complete,
        place_hospi_partielle,
        sejour_hospi_partielle,
        passage_urgence
        ,AVG(lit_hospi_complete) OVER (PARTITION BY annee, region, code_region, nom_region, service_medical, service_classification) AS lit_hospi_complete1
        ,AVG(sejour_hospi_complete) OVER (PARTITION BY annee, region, code_region, nom_region, service_medical, service_classification) AS sejour_hospi_complete1
        ,AVG(journee_hospi_complete) OVER (PARTITION BY annee, region, code_region, nom_region, service_medical, service_classification) AS journee_hospi_complete1
        ,AVG(place_hospi_partielle) OVER (PARTITION BY annee, region, code_region, nom_region, service_medical, service_classification) AS place_hospi_partielle1
        ,AVG(sejour_hospi_partielle) OVER (PARTITION BY annee, region, code_region, nom_region, service_medical, service_classification) AS sejour_hospi_partielle1
        ,AVG(passage_urgence) OVER (PARTITION BY annee, region, code_region, nom_region, service_medical, service_classification) AS passage_urgence1
    FROM {{ref("mart_capacite_dpt_reg")}}
),
evolution_data AS (
    SELECT 
        bd1.*,
        round(bd1.lit_hospi_complete1 - COALESCE(bd2.lit_hospi_complete1, 0),2) AS evolution_lit_hospi_complete1,
        CASE 
            WHEN COALESCE(bd2.lit_hospi_complete1, 0) = 0 THEN NULL 
            ELSE Round(safe_divide((bd1.lit_hospi_complete1 - bd2.lit_hospi_complete1) , bd2.lit_hospi_complete1), 2)  
        END AS evolution_percent_lit_hospi_complete1,
        round(bd1.sejour_hospi_complete1 - COALESCE(bd2.sejour_hospi_complete1, 0),2) AS evolution_sejour_hospi_complete1,
        CASE 
            WHEN COALESCE(bd2.sejour_hospi_complete1, 0) = 0 THEN NULL 
            ELSE Round(safe_divide((bd1.sejour_hospi_complete1 - bd2.sejour_hospi_complete1) , bd2.sejour_hospi_complete1), 2)  
        END AS evolution_percent_sejour_hospi_complete1,
        round(bd1.journee_hospi_complete1 - COALESCE(bd2.journee_hospi_complete1, 0),2) AS evolution_journee_hospi_complete1,
        CASE 
            WHEN COALESCE(bd2.journee_hospi_complete1, 0) = 0 THEN NULL 
            ELSE Round(safe_divide((bd1.journee_hospi_complete1 - bd2.journee_hospi_complete1) , bd2.journee_hospi_complete1), 2)  
        END AS evolution_percent_journee_hospi_complete1,
        round(bd1.place_hospi_partielle1 - COALESCE(bd2.place_hospi_partielle1, 0),2) AS evolution_place_hospi_partielle1,
        CASE 
            WHEN COALESCE(bd2.place_hospi_partielle1, 0) = 0 THEN NULL 
            ELSE Round(safe_divide((bd1.place_hospi_partielle1 - bd2.place_hospi_partielle1) , bd2.place_hospi_partielle1), 2)  
        END AS evolution_percent_place_hospi_partielle1,
        round(bd1.sejour_hospi_partielle1 - COALESCE(bd2.sejour_hospi_partielle1, 0),2) AS evolution_sejour_hospi_partielle1,
        CASE 
            WHEN COALESCE(bd2.sejour_hospi_partielle1, 0) = 0 THEN NULL 
            ELSE Round(safe_divide((bd1.sejour_hospi_partielle1 - bd2.sejour_hospi_partielle1) , bd2.sejour_hospi_partielle1), 2)  
        END AS evolution_percent_sejour_hospi_partielle1,
        round(bd1.passage_urgence1 - COALESCE(bd2.passage_urgence1, 0),2) AS evolution_passage_urgence1,
        CASE 
            WHEN COALESCE(bd2.passage_urgence1, 0) = 0 THEN NULL 
            ELSE Round(safe_divide((bd1.passage_urgence1 - bd2.passage_urgence1) , bd2.passage_urgence1), 2)  
        END AS evolution_percent_passage_urgence1
    FROM base_data bd1
    LEFT JOIN base_data bd2 
        ON bd1.region = bd2.region
        AND bd1.code_region = bd2.code_region
        AND bd1.nom_region = bd2.nom_region
        AND bd1.service_medical = bd2.service_medical
        AND bd1.service_classification = bd2.service_classification
        AND bd1.annee = bd2.annee + 1
)
SELECT *,
    CONCAT(region , "_" , annee , "_" , service_classification) as cle_unique
FROM evolution_data
ORDER BY region, annee