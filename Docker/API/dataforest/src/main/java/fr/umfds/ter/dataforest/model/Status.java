package fr.umfds.ter.dataforest.model;

import lombok.Data;
import org.springframework.data.mongodb.core.mapping.Field;

@Data
public class Status {
    @Field("alive_code")
    private Boolean aliveCode;
    @Field("measurement_code")
    private Integer measurementCode;
    private Circumference circumference;
}
