package fr.umfds.ter.dataforest.repository;

import fr.umfds.ter.dataforest.model.*;
import org.springframework.data.mongodb.repository.Aggregation;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;

import java.util.List;

public interface FeatureRepository extends MongoRepository<Feature, String> {
    @Query(value = "{}", fields = "{'type' : 1, 'geometry' :  1, '_id': 0}")
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

            // 2. Élimination des doublons : on garde 1 arbre unique par id
            "{ '$group': { " +
                    "'_id': '$properties.tree.id', " +
                    "'plot_id': { '$first': '$properties.plot.id' }, " +
                    "'species': { '$first': '$properties.tree.species.species' } " +
                    "} }",

            // 3. On compte les espèces à partir des arbres uniques
            "{ '$group': { " +
                    "'_id': { 'plot_id': '$plot_id', 'species': '$species' }, " +
                    "'count_species': { '$sum': 1 } " +
                    "} }",

            // 4. Regroupement par plot pour Shannon
            "{ '$group': { " +
                    "'_id': '$_id.plot_id', " +
                    "'species_counts': { '$push': { 'species': '$_id.species', 'count': '$count_species' } }, " +
                    "'nbTrees': { '$sum': '$count_species' } " +
                    "} }",

            // 5. Calcul p_i
            "{ '$unwind': '$species_counts' }",

            "{ '$project': { " +
                    "'nbTrees': 1, " +
                    "'species': '$species_counts.species', " +
                    "'count': '$species_counts.count', " +
                    "'p_i': { '$divide': [ '$species_counts.count', '$nbTrees' ] } " +
                    "} }",

            // 6. Shannon term
            "{ '$project': { " +
                    "'nbTrees': 1, " +
                    "'shannon_term': { '$multiply': [ '$p_i', { '$ln': '$p_i' } ] } " +
                    "} }",

            // 7. Somme des Shannon terms
            "{ '$group': { " +
                    "'_id': null, " +
                    "'nbTrees': { '$first': '$nbTrees' }, " +
                    "'shannon': { '$sum': '$shannon_term' } " +
                    "} }",

            // 8. Récupération infos plot
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
                    "'idPlot': '$plot_info._id', " +
                    "'forest': '$plot_info.forest', " +
                    "'area': '$plot_info.area', " +
                    "'nbTrees': 1, " +
                    "'shannon': { '$multiply': [ '$shannon', -1 ] }, " +
                    "'density': { '$cond': [ { '$gt': [ '$plot_info.area', 0 ] }, { '$divide': [ '$nbTrees', '$plot_info.area' ] }, null ] } " +
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
                    "'count_species': { '$sum': 1 } " +
                    "} }",

            // 4. Regrouper par sub_plot pour total arbre + liste des espèces
            "{ '$group': { " +
                    "'_id': { 'plot_id': '$_id.plot_id', 'sub_plot_id': '$_id.sub_plot_id' }, " +
                    "'species_counts': { '$push': { 'species': '$_id.species', 'count': '$count_species' } }, " +
                    "'nbTrees': { '$sum': '$count_species' } " +
                    "} }",

            // 5. Calcul des p_i
            "{ '$unwind': '$species_counts' }",
            "{ '$project': { " +
                    "'_id': 1, " +
                    "'nbTrees': 1, " +
                    "'p_i': { '$divide': [ '$species_counts.count', '$nbTrees' ] } " +
                    "} }",

            // 6. Calcul du terme de Shannon
            "{ '$project': { " +
                    "'_id': 1, " +
                    "'nbTrees': 1, " +
                    "'shannon_term': { '$multiply': [ '$p_i', { '$ln': '$p_i' } ] } " +
                    "} }",

            // 7. Calcul final de l’indice de Shannon
            "{ '$group': { " +
                    "'_id': '$_id', " +
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
                    "'density': { '$cond': [ { '$gt': [ '$plotInfo.area', 0 ] }, { '$divide': [ '$nbTrees', '$plotInfo.area' ] }, null ] } " +
                    "} }"
    })
    InfosSubPlot getInfosSubPlotById(String idPlot, Integer idSubPlot);







}
