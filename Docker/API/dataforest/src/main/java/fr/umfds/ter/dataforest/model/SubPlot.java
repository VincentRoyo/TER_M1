package fr.umfds.ter.dataforest.model;

import lombok.Data;
import org.springframework.data.mongodb.core.mapping.Field;

@Data
public class SubPlot {
    @Field("id")
    private Integer idSubPlot;
    private Location location;
}
