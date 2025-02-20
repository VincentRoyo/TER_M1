package fr.umfds.ter.dataforest.model;

import lombok.Data;

@Data
public class Polygon {
    private String type;
    private Double[][] coordinates;
}
