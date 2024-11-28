with 

source as (

    select * from {{ source('morbidite_h', 'duree_sejours') }}

),

renamed as (

    select
        departement as niveau,
        annee,
        year,
        pathologie,
        code_pathologie,
        nom_pathologie,
        region,
        code_region,
        nom_region,
        hospi_prog_24h,
        hospi_autres_24h,
        hospi_total_24h,
        hospi_1j,
        hospi_2j,
        hospi_3j,
        hospi_4j,
        hospi_5j,
        hospi_6j,
        hospi_7j,
        hospi_8j,
        hospi_9j,
        hospi_10j_19j,
        hospi_20j_29j,
        hospi_30j,
        total_hospi,
        avg_duree_hospi,
        cle_unique

    from source

)

select * from renamed
