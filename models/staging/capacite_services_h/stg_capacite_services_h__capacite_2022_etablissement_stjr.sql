with 

source as (

    select * from {{ source('capacite_services_h', 'capacite_2022_etablissement_stjr') }}

),

renamed as (

    select
        fi,
        an,
        fi_ej,
        rs,
        grp,
        stjr,
        cat,
        dep,
        reg,
        espic,
        cominsee,
        disci,
        discipline,
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
        sechi

    from source

)

select * from renamed
