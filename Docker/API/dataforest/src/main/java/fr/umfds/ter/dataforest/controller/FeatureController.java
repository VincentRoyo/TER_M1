package fr.umfds.ter.dataforest.controller;

import fr.umfds.ter.dataforest.model.Feature;
import fr.umfds.ter.dataforest.model.InfosPlot;
import fr.umfds.ter.dataforest.model.InfosSubPlot;
import fr.umfds.ter.dataforest.model.PlotLocationResponse;
import fr.umfds.ter.dataforest.repository.FeatureRepository;
import fr.umfds.ter.dataforest.service.FeatureService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
public class FeatureController {

    private final FeatureRepository repository;
    private final FeatureService service;

    public FeatureController(FeatureRepository repository, FeatureService service) {
        this.repository = repository;
        this.service = service;
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
        return service.getPlotInfo(idPlot);
    }

    @GetMapping("/infosubplot/{idSubPlot}")
    public InfosSubPlot getInfosSubPlot(@PathVariable String idSubPlot) {
        return service.getSubPlotInfo(idSubPlot);
    }
}
