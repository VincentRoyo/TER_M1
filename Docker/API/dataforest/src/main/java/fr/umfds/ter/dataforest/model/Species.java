package fr.umfds.ter.dataforest.model;

import lombok.Data;

@Data
public class Species {
    private String family;
    private String genus;
    private String species;
    private String source;
    private Boolean certainty;
}
