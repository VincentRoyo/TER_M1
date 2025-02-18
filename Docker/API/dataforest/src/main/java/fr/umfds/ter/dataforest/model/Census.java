package fr.umfds.ter.dataforest.model;

import lombok.Data;
import org.springframework.data.mongodb.core.mapping.Field;

@Data
public class Census {
    private Integer year;
    private String date;

    @Field("date_certainty")
    private Boolean dateCertainty;
}
