package fr.umfds.ter.dataforest.model;

import lombok.Data;
import org.springframework.data.mongodb.core.mapping.Document;

@Document(collection = "forest1")
@Data
public class Feature {
    private String type;
    private Geometry geometry;
    private Properties properties;
}
