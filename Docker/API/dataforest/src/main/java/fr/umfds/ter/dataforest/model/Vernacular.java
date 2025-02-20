package fr.umfds.ter.dataforest.model;

import lombok.Data;
import org.springframework.data.mongodb.core.mapping.Field;

@Data
public class Vernacular {
    @Field("id")
    private Integer idVernacular;

    private String name;

    @Field("commercial_species")
    private Boolean commercialSpecies;
}
