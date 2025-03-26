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

    @Query(value = "{ 'properties.plot.id' : ?0 }",
            fields = "{ 'properties.plot' : 1, 'properties.forest' : 1, 'properties.area' : 1, 'properties.sub_plot' : 1, '_id' : 0 }")
    List<Feature> getPlot(String idPlot);

    @Query(value = "{ 'properties.plot.id' : ?0, 'properties.plot.sub_plot.id' : ?1 }",
            fields = "{ 'properties.plot' : 1, 'properties.forest' : 1, 'properties.area' : 1, '_id' : 0 }")
    List<Feature> getSubPlot(String idPlot, String idSubPlot);


    @Aggregation(pipeline = {
            "{ $match: { 'properties.plot.id': ?0 } }",
            "{ $group: { " +
                    "  _id: { plot_id: '$properties.plot.id', species: '$properties.tree.species.species' }, " +
                    "  count_species: { $sum: 1 } " +
                    "} }",
            "{ $group: { " +
                    "  _id: '$_id.plot_id', " +
                    "  species_counts: { $push: { species: '$_id.species', count: '$count_species' } }, " +
                    "  total_trees: { $sum: '$count_species' } " +
                    "} }",
            "{ $unwind: '$species_counts' }",
            "{ $project: { " +
                    "  p_i: { $divide: ['$species_counts.count', '$total_trees'] } " +
                    "} }",
            "{ $project: { " +
                    "  shannon_term: { $multiply: ['$p_i', { $ln: '$p_i' }] } " +
                    "} }",
            "{ $group: { " +
                    "  _id: null, " +
                    "  shannon_index: { $sum: '$shannon_term' } " +
                    "} }",
            "{ $project: { " +
                    "  _id: 0, " +
                    "  shannon_index: { $multiply: ['$shannon_index', -1] } " +
                    "} }"
    })
    Double findShannonIndexByPlot(String idPlot);

    @Aggregation(pipeline = {
            "{ $match: { 'properties.plot.id' : ?0, 'properties.plot.sub_plot.id' : ?1 } }",
            "{ $group: { " +
                    "  _id: { plot_id: '$properties.plot.id', species: '$properties.tree.species.species' }, " +
                    "  count_species: { $sum: 1 } " +
                    "} }",
            "{ $group: { " +
                    "  _id: '$_id.plot_id', " +
                    "  species_counts: { $push: { species: '$_id.species', count: '$count_species' } }, " +
                    "  total_trees: { $sum: '$count_species' } " +
                    "} }",
            "{ $unwind: '$species_counts' }",
            "{ $project: { " +
                    "  p_i: { $divide: ['$species_counts.count', '$total_trees'] } " +
                    "} }",
            "{ $project: { " +
                    "  shannon_term: { $multiply: ['$p_i', { $ln: '$p_i' }] } " +
                    "} }",
            "{ $group: { " +
                    "  _id: null, " +
                    "  shannon_index: { $sum: '$shannon_term' } " +
                    "} }",
            "{ $project: { " +
                    "  _id: 0, " +
                    "  shannon_index: { $multiply: ['$shannon_index', -1] } " +
                    "} }"
    })
    Double findShannonIndexBySubPlot(String idPlot, String idSubPlot);
}
