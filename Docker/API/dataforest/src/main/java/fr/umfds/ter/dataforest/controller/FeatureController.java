package fr.umfds.ter.dataforest.controller;

import fr.umfds.ter.dataforest.model.*;
import fr.umfds.ter.dataforest.repository.FeatureRepository;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
public class FeatureController {

    private final FeatureRepository repository;

    public FeatureController(FeatureRepository repository) {
        this.repository = repository;
    }

    @GetMapping("/all")
    public List<Feature> getAll() {
        return repository.findAll();
    }

    @GetMapping("/allgeo")
    public List<Feature> getAllGeo() {
        return repository.findAllGeojson();
    }

    @GetMapping("/geoplot")
    public List<PlotLocationResponse> getGeoPlot() {
        return repository.findAllPlotsWithLocation();
    }

    @GetMapping("/infoplot/{idPlot}")
    public InfosPlot getInfosPlot(@PathVariable String idPlot) {
        return repository.getInfosPlotById(idPlot);
    }

    @GetMapping("/infoplot/{idPlot}/{idSubPlot}")
    public InfosSubPlot getInfosSubPlot(@PathVariable String idPlot, @PathVariable Integer idSubPlot) {
        return repository.getInfosSubPlotById(idPlot, idSubPlot);
    }

}
