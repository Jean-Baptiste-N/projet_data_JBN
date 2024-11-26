with 

source as (

    select * from {{ source('morbidite_h', 'tableau_3') }}

),

renamed as (

    select
        Niveau as departement,
        SEXE as sexe,
        PATHOLOGIE as pathologie,
        SPLIT(PATHOLOGIE, "-")[SAFE_OFFSET(0)] AS code_pathologie,
        SPLIT(PATHOLOGIE, "-")[SAFE_OFFSET(1)] AS nom_pathologie,
        ANNEE as annee,
        "ZONE" as "zone",
        "Moins d'un an" as tranche_age_0_1,
        "1 à 4 ans" as tranche_age_1_4,
        "5 à 14 ans" as tranche_age_5_14,
        "15 à 24 ans"as tranche_age_15_24,
        "25 à 34 ans"as tranche_age_25_34,
        "35 à 44 ans"as tranche_age_35_44,
        "45 à 54 ans"as tranche_age_45_54,
        "55 à 64 ans"as tranche_age_55_64,
        "65 à 74 ans"as tranche_age_65_74,
        "75 à 84 ans"as tranche_age_75_84,
        "85 ans et plus" as tranche_age_85_et_plus,
        "Taux brut tous age en %mille" as tx_brut_tt_age_pour_mille,
        "Taux standardisé tous ages en %mille" as tx_standard_tt_age_pour_mille ,
        "Indice comparatif tous ages en %" as indice_comparatif_tt_age_percent,

    from source

)

select * from renamed
-- code generation failed!