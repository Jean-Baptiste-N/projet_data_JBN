WITH population as (
    SELECT
    CAST(code_departement as INT64) as code_region
    ,nom_departement as region
    ,CONCAT(code_departement ," - ", nom_departement) as cle_region
    ,annee
    ,population
    FROM {{ref("stg_pop_departement__population_departement")}}
    UNION ALL
    SELECT
    code_region
    ,region
    ,CONCAT(code_region ," - ", region) as cle_region
    ,annee
    ,population
    FROM {{ref("stg_pop_departement__population_region")}}    
)    
    SELECT 
    t1.*
    ,t2.population
FROM {{ref("class_join_total_morbidite")}} t1
LEFT JOIN population as t2
ON t1.annee = t2.annee AND t1.region = t2.cle_region
