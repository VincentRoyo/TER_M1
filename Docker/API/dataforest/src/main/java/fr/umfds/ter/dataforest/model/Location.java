package fr.umfds.ter.dataforest.model;

import lombok.Data;

@Data
public class Location {
    private String type;
    private Polygon geometry;
}