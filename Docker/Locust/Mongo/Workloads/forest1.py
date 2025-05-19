def get_queries(collection):
    return {
        "arbres_par_plot_sousplot": lambda: collection.aggregate([
            {
                "$group": {
                    "_id": {
                        "plot": "$properties.plot.id",
                        "sub_plot": "$properties.plot.sub_plot"
                    },
                    "trees": { "$push": "$properties.tree.id" }
                }
            }
        ]),

        "especes_par_plot_sousplot": lambda: collection.aggregate([
            {
                "$group": {
                    "_id": {
                        "plot": "$properties.plot.id",
                        "sub_plot": "$properties.plot.sub_plot"
                    },
                    "species": { "$addToSet": "$properties.tree.species.species" }
                }
            }
        ]),

        "especes_par_plot": lambda: collection.aggregate([
            {
                "$group": {
                    "_id": { "plot": "$properties.plot.id" },
                    "species": { "$addToSet": "$properties.tree.species.species" }
                }
            }
        ]),

        "nb_especes_par_plot_sousplot": lambda: collection.aggregate([
            {
                "$group": {
                    "_id": {
                        "plot": "$properties.plot.id",
                        "sub_plot": "$properties.plot.sub_plot.id"
                    },
                    "species_set": { "$addToSet": "$properties.tree.species.species" }
                }
            },
            {
                "$project": {
                    "plot_id": "$_id.plot",
                    "sub_plot": "$_id.sub_plot",
                    "species_count": { "$size": "$species_set" }
                }
            }
        ]),

        "nb_especes_par_plot": lambda: collection.aggregate([
            {
                "$group": {
                    "_id": "$properties.plot.id",
                    "species_set": { "$addToSet": "$properties.tree.species.species" }
                }
            },
            {
                "$project": {
                    "plot_id": "$_id",
                    "species_count": { "$size": "$species_set" }
                }
            }
        ]),

        "plots_sousplots_location": lambda: collection.aggregate([
            {
                "$group": {
                    "_id": "$properties.plot.id",
                    "location": { "$first": "$properties.plot.location" },
                    "sub_plots": { "$addToSet": "$properties.plot.sub_plot" }
                }
            },
            {
                "$project": {
                    "plot_id": "$_id",
                    "location": 1,
                    "sub_plots": 1
                }
            }
        ])
    }

