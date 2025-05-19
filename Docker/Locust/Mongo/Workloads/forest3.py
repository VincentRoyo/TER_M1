def get_queries(collection):
    return {
        "arbres_par_plot_sousplot": lambda: collection.aggregate([
            { "$unwind": "$properties.trees.features" },
            { "$group": {
                "_id": {
                    "plot": "$properties.plot.id",
                    "sub_plot": "$properties.trees.features.properties.sub_plot_id"
                },
                "trees": { "$push": "$properties.trees.features.properties.tree_id" }
            }}
        ]),

        "especes_par_plot_sousplot": lambda: collection.aggregate([
            { "$unwind": "$properties.trees.features" },
            { "$group": {
                "_id": {
                    "plot": "$properties.plot.id",
                    "sub_plot": "$properties.trees.features.properties.sub_plot_id"
                },
                "species": { "$addToSet": "$properties.trees.features.properties.tree_species_species" }
            }}
        ]),

        "especes_par_plot": lambda: collection.aggregate([
            { "$unwind": "$properties.trees.features" },
            { "$group": {
                "_id": "$properties.plot.id",
                "species": { "$addToSet": "$properties.trees.features.properties.tree_species_species" }
            }}
        ]),

        "nb_especes_par_plot_sousplot": lambda: collection.aggregate([
            { "$unwind": "$properties.trees.features" },
            { "$group": {
                "_id": {
                    "plot": "$properties.plot.id",
                    "sub_plot": "$properties.trees.features.properties.sub_plot_id"
                },
                "species_set": { "$addToSet": "$properties.trees.features.properties.tree_species_species" }
            }},
            { "$project": {
                "plot_id": "$_id.plot",
                "sub_plot": "$_id.sub_plot",
                "species_count": { "$size": "$species_set" }
            }}
        ]),

        "nb_especes_par_plot": lambda: collection.aggregate([
            { "$unwind": "$properties.trees.features" },
            { "$group": {
                "_id": "$properties.plot.id",
                "species_set": { "$addToSet": "$properties.trees.features.properties.tree_species_species" }
            }},
            { "$project": {
                "plot_id": "$_id",
                "species_count": { "$size": "$species_set" }
            }}
        ]),

        "plots_sousplots_location": lambda: collection.aggregate([
            { "$group": {
                "_id": "$properties.plot.id",
                "location": { "$first": "$geometry.coordinates" },
                "sub_plots": { "$addToSet": "$properties.sub_plots" }
            }},
            { "$project": {
                "plot_id": "$_id",
                "location": 1,
                "sub_plots": 1
            }}
        ])
    }

