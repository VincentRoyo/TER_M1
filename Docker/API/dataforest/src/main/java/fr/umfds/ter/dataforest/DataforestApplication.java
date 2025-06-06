package fr.umfds.ter.dataforest;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.mongodb.repository.config.EnableMongoRepositories;

@SpringBootApplication(
		scanBasePackages = {"fr.umfds.ter.dataforest"}
)
@EnableMongoRepositories
public class DataforestApplication {

	public static void main(String[] args) {
		SpringApplication.run(DataforestApplication.class, args);

		//ROUTE POUR RECUPERER LES DONNEES GEOJSON SEULEMENT DONC LES DONNEES MAIS SANS LE PROPERTIES
	}

}
