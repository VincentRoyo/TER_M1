package fr.umfds.ter.dataforest.model;

import lombok.Data;

@Data
public class SpeciesDistribution {
    private String species;
    private Integer count;
    private Double distribution;
}
