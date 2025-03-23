package fr.umfds.ter.dataforest.model;

import lombok.Data;

@Data
public class InfosSubPlot {

    private String idSubPlot;
    private String idPlot;
    private String forest;
    private Integer area;
    private Integer nbTrees;
    private Double density;
    private Double shannon;
}
