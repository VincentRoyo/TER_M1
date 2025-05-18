package fr.umfds.ter.dataforest.repository;

import fr.umfds.ter.dataforest.model.*;
import org.springframework.data.mongodb.repository.Aggregation;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;

import java.util.List;

public interface FeatureRepository extends MongoRepository<Feature, String> {
    @Query(value = "{}", fields = "{'type' : 1, 'geometry' :  1, 'properties.tree': 1, '_id': 0}")
    List<Feature> findAllGeojson();

    @Aggregation(pipeline = {
            "{ $group: { " +
                    "  _id: '$properties.plot.id', " +
                    "  location: { $first: '$properties.plot.location' }, " +
                    "  sub_plots: { $addToSet: '$properties.plot.sub_plot' } " +
                    "} }",
            "{ $project: { '_id': 0, 'plot_id': '$_id', 'location': 1, 'sub_plots': 1 } }"
    })
    List<PlotLocationResponse> findAllPlotsWithLocation();

    @Aggregation(pipeline = {
            // 1. On filtre sur le plot ciblé
            "{ '$match': { 'properties.plot.id': ?0 } }",

            // 2. Élimination des doublons : un arbre unique par id
            "{ '$group': { " +
                    "'_id': '$properties.tree.id', " +
                    "'plot_id': { '$first': '$properties.plot.id' }, " +
                    "'species': { '$first': '$properties.tree.species.species' } " +
                    "} }",

            // 3. On compte les espèces
            "{ '$group': { " +
                    "'_id': { 'plot_id': '$plot_id', 'species': '$species' }, " +
                    "'count_species': { '$sum': 1 } " +
                    "} }",

            // 4. Regroupement par plot pour calculs
            "{ '$group': { " +
                    "'_id': '$_id.plot_id', " +
                    "'species_counts': { '$push': { 'species': '$_id.species', 'count': '$count_species' } }, " +
                    "'nbTrees': { '$sum': '$count_species' } " +
                    "} }",

            // 5. Calcul des p_i
            "{ '$unwind': '$species_counts' }",

            "{ '$addFields': { " +
                    "'species_counts.p_i': { '$divide': [ '$species_counts.count', '$nbTrees' ] } " +
                    "} }",

            // 6. Shannon term
            "{ '$addFields': { " +
                    "'species_counts.shannon_term': { '$multiply': [ '$species_counts.p_i', { '$ln': '$species_counts.p_i' } ] } " +
                    "} }",

            // 7. Regroupement à nouveau pour somme et distribution
            "{ '$group': { " +
                    "'_id': '$_id', " +
                    "'nbTrees': { '$first': '$nbTrees' }, " +
                    "'species_distribution': { '$push': { " +
                    "'species': '$species_counts.species', " +
                    "'count': '$species_counts.count', " +
                    "'distribution': '$species_counts.p_i' " +
                    "} }, " +
                    "'shannon': { '$sum': '$species_counts.shannon_term' } " +
                    "} }",

            // 8. Récupération des infos plot
            "{ '$lookup': { " +
                    "'from': 'forest1', " +
                    "'pipeline': [" +
                    "{ '$match': { 'properties.plot.id': ?0 } }, " +
                    "{ '$group': { " +
                    "'_id': '$properties.plot.id', " +
                    "'forest': { '$first': '$properties.forest' }, " +
                    "'area': { '$first': '$properties.plot.area' } " +
                    "} }" +
                    "], " +
                    "'as': 'plot_info' " +
                    "} }",

            // 9. Fusion
            "{ '$unwind': '$plot_info' }",

            // 10. Projection finale
            "{ '$project': { " +
                    "'idPlot': '$_id', " +
                    "'forest': '$plot_info.forest', " +
                    "'area': '$plot_info.area', " +
                    "'nbTrees': 1, " +
                    "'shannon': { '$multiply': [ '$shannon', -1 ] }, " +
                    "'density': { '$cond': [ { '$gt': [ '$plot_info.area', 0 ] }, { '$divide': [ '$nbTrees', '$plot_info.area' ] }, null ] }, " +
                    "'species_distribution': 1 " +
                    "} }"
    })
    InfosPlot getInfosPlotById(String idPlot);


    @Aggregation(pipeline = {
            // 1. Filtrer par plot.id ET sub_plot.id
            "{ '$match': { 'properties.plot.id': ?0, 'properties.plot.sub_plot.id': ?1 } }",

            // 2. Grouper par arbre unique pour éviter doublons
            "{ '$group': { " +
                    "'_id': '$properties.tree.id', " +
                    "'plot_id': { '$first': '$properties.plot.id' }, " +
                    "'sub_plot_id': { '$first': '$properties.plot.sub_plot.id' }, " +
                    "'species': { '$first': '$properties.tree.species.species' } " +
                    "} }",

            // 3. Compter les arbres uniques par espèce
            "{ '$group': { " +
                    "'_id': { 'plot_id': '$plot_id', 'sub_plot_id': '$sub_plot_id', 'species': '$species' }, " +
                    "'count': { '$sum': 1 } " +
                    "} }",

            // 4. Regrouper par subplot avec total arbres et tableau espèces
            "{ '$group': { " +
                    "'_id': { 'plot_id': '$_id.plot_id', 'sub_plot_id': '$_id.sub_plot_id' }, " +
                    "'species_distribution': { '$push': { 'species': '$_id.species', 'count': '$count' } }, " +
                    "'nbTrees': { '$sum': '$count' } " +
                    "} }",

            // 5. Calcul des p_i pour chaque espèce
            "{ '$unwind': '$species_distribution' }",
            "{ '$addFields': { " +
                    "'species_distribution.distribution': { '$divide': [ '$species_distribution.count', '$nbTrees' ] } " +
                    "} }",

            // 6. Regrouper à nouveau pour récupérer tableau complet
            "{ '$group': { " +
                    "'_id': '$_id', " +
                    "'species_distribution': { '$push': '$species_distribution' }, " +
                    "'nbTrees': { '$first': '$nbTrees' } " +
                    "} }",

            // 7. Calcul Shannon
            "{ '$unwind': '$species_distribution' }",
            "{ '$project': { " +
                    "'_id': 1, " +
                    "'nbTrees': 1, " +
                    "'species_distribution': 1, " +
                    "'shannon_term': { '$multiply': [ '$species_distribution.distribution', { '$ln': '$species_distribution.distribution' } ] } " +
                    "} }",

            "{ '$group': { " +
                    "'_id': '$_id', " +
                    "'species_distribution': { '$push': '$species_distribution' }, " +
                    "'nbTrees': { '$first': '$nbTrees' }, " +
                    "'shannon': { '$sum': '$shannon_term' } " +
                    "} }",

            // 8. Lookup pour récupérer forest et area depuis le PLOT parent
            "{ '$lookup': { " +
                    "'from': 'forest1', " +
                    "'pipeline': [ " +
                    "{ '$match': { 'properties.plot.id': ?0 } }, " +
                    "{ '$group': { " +
                    "'_id': null, " +
                    "'forest': { '$first': '$properties.forest' }, " +
                    "'area': { '$first': '$properties.plot.area' } " +
                    "} } " +
                    "], " +
                    "'as': 'plotInfo' " +
                    "} }",

            // 9. Unwind de l’info du plot
            "{ '$unwind': '$plotInfo' }",

            // 10. Projection finale vers InfosSubPlot
            "{ '$project': { " +
                    "'idPlot': '$_id.plot_id', " +
                    "'idSubPlot': '$_id.sub_plot_id', " +
                    "'forest': '$plotInfo.forest', " +
                    "'area': '$plotInfo.area', " +
                    "'nbTrees': 1, " +
                    "'shannon': { '$multiply': [ '$shannon', -1 ] }, " +
                    "'density': { '$cond': [ { '$gt': [ '$plotInfo.area', 0 ] }, { '$divide': [ '$nbTrees', '$plotInfo.area' ] }, null ] }, " +
                    "'species_distribution': 1 " +
                    "} }"
    })
    InfosSubPlot getInfosSubPlotById(String idPlot, Integer idSubPlot);
}
