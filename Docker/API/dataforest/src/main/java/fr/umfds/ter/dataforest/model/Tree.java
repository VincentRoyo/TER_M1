package fr.umfds.ter.dataforest.model;

import lombok.Data;
import org.springframework.data.mongodb.core.mapping.Field;

@Data
public class Tree {
    @Field("field_number")
    private String fieldNumber;

    @Field("id")
    private Integer idTree;

    private Species species;
    private Vernacular vernacular;
}
