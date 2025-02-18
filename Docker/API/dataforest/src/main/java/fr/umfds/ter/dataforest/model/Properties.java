package fr.umfds.ter.dataforest.model;

import lombok.Data;

import java.util.List;

@Data
public class Properties {
    private String forest;
    private Plot plot;
    private Tree tree;
    private List<Measurement> measurements;
}
