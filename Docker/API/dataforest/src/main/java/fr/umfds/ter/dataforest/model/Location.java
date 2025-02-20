package fr.umfds.ter.dataforest.model;

import lombok.Data;
import org.springframework.data.mongodb.core.mapping.Field;

@Data
public class Location {
    private String type;
    private Polygon geometry;
}