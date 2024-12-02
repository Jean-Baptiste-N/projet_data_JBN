-- With stjr1 as (
--     SELECT
--         t1.*,
--         t2.stjr
--     FROM {{ref('stg_capacite_services_h__capacite_2022_par_services')}} t1
--     LEFT JOIN (
--         SELECT DISTINCT FI, AN, stjr
--         FROM {{ref('stg_capacite_services_h__capacite_2021_service_stjr')}}
--         WHERE AN = 2021
--     ) t2
--     ON t1.fi = t2.FI
--     WHERE t1.an >= 2018 AND t1.an < 2022
-- ),
--  stjr2 as (
--     SELECT
--         t1.*,
--         t2.stjr
--     FROM {{ref('stg_capacite_services_h__capacite_2022_par_services')}} t1
--     LEFT JOIN (
--         SELECT DISTINCT fi, an, stjr
--         FROM {{ref('stg_capacite_services_h__capacite_2022_etablissement_stjr')}}
--         WHERE AN = 2022
--     ) t2
--     ON CAST(t1.fi AS STRING) = t2.fi
--     WHERE t1.an = 2022
--  ),
-- join_stjr as (
-- SELECT *
-- FROM stjr1
-- UNION ALL
-- SELECT *
-- FROM stjr2
-- )

SELECT
fi as id_etablissement,
an as annee,
rs as nom_etablissement,
stj as statut_juridique,
cat as categ_etablissement,
dep as departement,
SPLIT(dep, " - ")[SAFE_OFFSET(0)] AS code_departement,
SPLIT(dep, " - ")[SAFE_OFFSET(1)] AS nom_departement,
reg as region,
SPLIT(reg, " - ")[SAFE_OFFSET(0)] AS code_region,
SPLIT(reg, " - ")[SAFE_OFFSET(1)] AS nom_region,
-- stjr as statut_entite,
espic as code_espic,
DISCI as discipline_equipement,
DISCIPLINE as service_medical,
LIT as lit_hospi_complete,
SEJHC as sejour_hospi_complete,
JOU as journee_hospi_complete,
PLA as place_hospi_partielle,
SEJHP as sejour_hospi_partielle,
PAS as passage_urgence,
SEJACC as sejour_accouchement,
SEHEM as seance_hemodyalise,
SERAD as seance_radiotherapie,
SECHI as seance_chimio,
cle_unique
FROM {{ref('stg_capacite_services_h__capacite_2022_par_services')}}
WHERE an >= 2018