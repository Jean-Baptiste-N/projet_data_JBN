with 

source as (

    select * from {{ source('capacite_services_h', 'capacite_2021_service_stjr') }}

),

renamed as (

    select
        an,
        fi,
        fi_ej,
        stjr,
        disci,
        lit,
        sejhc,
        jou,
        pla,
        sejhp,
        pas,
        sejacc,
        ivg,
        sehem,
        serad,
        sechi,
        discipline

    from source

)

select * from renamed
