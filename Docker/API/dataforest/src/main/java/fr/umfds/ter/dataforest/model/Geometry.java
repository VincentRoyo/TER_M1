package fr.umfds.ter.dataforest.model;

import lombok.Data;

@Data
public class Geometry {
    private String type;
    private Double[] coordinates;
}
