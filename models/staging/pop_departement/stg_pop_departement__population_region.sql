with 

source as (

    select * from {{ source('pop_departement', 'population_region') }}

),

renamed as (

    select
        code_region,
        region,
        annee,
        population

    from source

)

select * from renamed
