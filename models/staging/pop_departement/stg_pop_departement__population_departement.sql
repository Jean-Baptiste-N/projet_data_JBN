with 

source as (

    select * from {{ source('pop_departement', 'population_departement') }}

),

renamed as (

    select
        nom_departement,
        code_departement,
        code_region,
        region,
        annee,
        population

    from source

)

select * from renamed
