package fr.umfds.ter.dataforest.model;

import lombok.Data;
import org.springframework.data.mongodb.core.mapping.Field;

@Data
public class Circumference {
    private Double value;

    @Field("corrected_value")
    private Double correctedValue;

    @Field("correction_code")
    private String correctionCode;
}
