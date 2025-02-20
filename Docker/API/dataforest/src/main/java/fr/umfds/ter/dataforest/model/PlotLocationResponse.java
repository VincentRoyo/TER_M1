package fr.umfds.ter.dataforest.model;

import lombok.Data;

@Data
public class PlotLocationResponse {
    private String plot_id;
    private Location location;
    private SubPlot[] sub_plots;
}
