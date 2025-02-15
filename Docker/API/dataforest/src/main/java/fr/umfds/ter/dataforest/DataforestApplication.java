package fr.umfds.ter.dataforest;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(
		scanBasePackages = {
				"fr.umfds.ter.dataforest.controller",
				"fr.umfds.ter.dataforest.model",
				"fr.umfds.ter.dataforest.view"
		}
)
public class DataforestApplication {

	public static void main(String[] args) {
		SpringApplication.run(DataforestApplication.class, args);
	}

}
