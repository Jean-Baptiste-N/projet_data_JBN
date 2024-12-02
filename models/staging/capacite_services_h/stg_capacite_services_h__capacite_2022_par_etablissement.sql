with 

source as (

    select * from {{ source('capacite_services_h', 'capacite_2022_par_etablissement') }}

),

renamed as (

    select
        fi,
        an,
        fi_ej,
        rs,
        stj,
        cat,
        dep,
        reg,
        anc_reg,
        espic,
        cominsee,
        grp,
        lit,
        sejhc,
        jou,
        pla,
        sejhp,
        pas,
        sejacc,
        sehem,
        serad,
        sechi

    from source

)

select * from renamed