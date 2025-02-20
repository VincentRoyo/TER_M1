package fr.umfds.ter.dataforest.repository;

import fr.umfds.ter.dataforest.model.Feature;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;

import java.util.List;

public interface FeatureRepository extends MongoRepository<Feature, String> {
    @Query(value = "{}", fields = "{'type' : 1, 'geometry' :  1, '_id': 0}")
    List<Feature> findAllGeojson();
}
