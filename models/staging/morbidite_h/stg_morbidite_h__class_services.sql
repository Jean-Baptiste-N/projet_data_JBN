with 

source as (

    select * from {{ source('morbidite_h', 'class_services') }}

),

renamed as (

    select
        pathologie,
        classification

    from source

)

select * from renamed
