with 

source as (

    select * from {{ source('capacite_services_h', 'capacite_services_dpt_region') }}

),

renamed as (

    select
        cle_unique,
        annee,
        year,
        region,
        code_region,
        nom_region,
        departement,
        code_departement,
        nom_departement,
        service_classification,
        total_lit_hospi_complete,
        total_sejour_hospi_complete,
        total_journee_hospi_complete,
        total_place_hospi_partielle,
        total_sejour_hospi_partielle

    from source

)

select * from renamed
