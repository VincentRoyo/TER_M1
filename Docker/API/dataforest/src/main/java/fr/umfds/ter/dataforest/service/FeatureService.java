package fr.umfds.ter.dataforest.service;

import fr.umfds.ter.dataforest.model.Feature;
import fr.umfds.ter.dataforest.model.InfosPlot;
import fr.umfds.ter.dataforest.model.InfosSubPlot;
import fr.umfds.ter.dataforest.repository.FeatureRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class FeatureService {

    private final FeatureRepository featureRepository;

    public FeatureService(FeatureRepository featureRepository) {
        this.featureRepository = featureRepository;
    }

    public InfosPlot getPlotInfo(String idPlot) {
        List<Feature> features = featureRepository.getPlot(idPlot);
        InfosPlot plot = new InfosPlot();
        Integer nbTrees = features.size();
        Integer area = features.getFirst().getProperties().getPlot().getArea();

        plot.setIdPlot(idPlot);
        plot.setForest(features.getFirst().getProperties().getForest());
        plot.setArea(area);
        plot.setNbTrees(nbTrees);
        plot.setDensity((double) (nbTrees/area));
        plot.setShannon(featureRepository.findShannonIndexByPlot(idPlot));
        return plot;
    }

    public InfosSubPlot getSubPlotInfo(String idPlot, String idSubPlot) {
        List<Feature> features = featureRepository.getSubPlot(idPlot, idSubPlot);
        InfosSubPlot plot = new InfosSubPlot();
        Integer nbTrees = features.size();
        Integer area = features.getFirst().getProperties().getPlot().getArea();

        plot.setIdPlot(idSubPlot);
        plot.setIdPlot(idPlot);
        plot.setForest(features.getFirst().getProperties().getForest());
        plot.setArea(area);
        plot.setNbTrees(nbTrees);
        plot.setDensity((double) (nbTrees/area));
        plot.setShannon(featureRepository.findShannonIndexBySubPlot(idPlot, idSubPlot));
        System.out.println(plot);
        return plot;
    }
}