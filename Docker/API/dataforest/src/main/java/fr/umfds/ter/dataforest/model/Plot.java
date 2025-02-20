package fr.umfds.ter.dataforest.model;

import lombok.Data;
import org.springframework.data.mongodb.core.mapping.Field;

@Data
public class Plot {

    @Field("id")
    private String idPlot;

    private Integer area;

    @Field("sub_plot")
    private Integer subPlot; //MAPPER POUR AVOIR L'OBJET SOUS PLOT QUI EST UN PLOT ?
}
