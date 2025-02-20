package fr.umfds.ter.dataforest.controller;

import fr.umfds.ter.dataforest.model.Feature;
import fr.umfds.ter.dataforest.model.PlotLocationResponse;
import fr.umfds.ter.dataforest.repository.FeatureRepository;
import org.springframework.web.bind.annotation.GetMapping;
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

}
