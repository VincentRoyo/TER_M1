package fr.umfds.ter.dataforest.model;

import lombok.Data;

@Data
public class Point {
    private String type;
    private Double[] coordinates;
}
