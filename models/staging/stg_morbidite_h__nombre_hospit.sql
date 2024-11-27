with

    source as (select * from {{ source("morbidite_h", "nombre_hospit") }}),

    renamed as (

        select
            departement as niveau,
            sexe,
            year,
            pathologie,
            code_pathologie,
            nom_pathologie,
            region,
            code_region,
            nom_region,
            age,
            code_age,
            tranche_age,
            nbr_hospi,
            cle_unique

        from source

    )

select *
from renamed
