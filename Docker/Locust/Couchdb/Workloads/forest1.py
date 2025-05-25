from .utils import create_views, get_queries

views_forest1 = {
    "arbres_par_plot_sousplot": {
        "map": "function(doc){ emit([doc.properties.plot.id, doc.properties.plot.sub_plot.id], doc.properties.tree.id); }",
        "reduce": "function(keys, values, rereduce){ return rereduce ? [].concat.apply([], values) : values; }"
    },

    "especes_par_plot_sousplot": {
        "map": "function(doc){ if(doc.properties.tree.species && doc.properties.tree.species.species) emit([doc.properties.plot.id, doc.properties.plot.sub_plot.id], doc.properties.tree.species.species); }",
        "reduce": "function(keys, values, rereduce){ var s = new Set(rereduce ? [].concat.apply([], values) : values); return Array.from(s); }"
    },

    "especes_par_plot": {
        "map": "function(doc){ if(doc.properties.tree.species && doc.properties.tree.species.species) emit([doc.properties.plot.id], doc.properties.tree.species.species); }",
        "reduce": "function(keys, values, rereduce){ var s = new Set(rereduce ? [].concat.apply([], values) : values); return Array.from(s); }"
    },

    "nb_especes_par_plot_sousplot": {
        "map": "function(doc){ if(doc.properties.tree.species && doc.properties.tree.species.species) emit([doc.properties.plot.id, doc.properties.plot.sub_plot.id], doc.properties.tree.species.species); }",
        "reduce": "function(keys, values, rereduce){ var s = {}; (rereduce ? [].concat.apply([], values) : values).forEach(v => s[v] = true); return Object.keys(s).length; }"
    },

    "nb_especes_par_plot": {
        "map": "function(doc){ if(doc.properties.tree.species && doc.properties.tree.species.species) emit([doc.properties.plot.id], doc.properties.tree.species.species); }",
        "reduce": "function(keys, values, rereduce){ var s = {}; (rereduce ? [].concat.apply([], values) : values).forEach(v => s[v] = true); return Object.keys(s).length; }"
    },

    "plots_sousplots_location": {
        "map": "function(doc){ if(doc.properties.plot && doc.properties.plot.location && doc.properties.plot.sub_plot){ emit(doc.properties.plot.id, { location: doc.properties.plot.location, sub_plot: doc.properties.plot.sub_plot }); } }",
        "reduce": "function(keys, values, rereduce){ var loc = values[0].location; var subs = {}; values.forEach(v => subs[v.sub_plot.id] = true); return { location: loc, sub_plots: Object.keys(subs) }; }"
    }
}



def create_views_forest(session, db_url):
    create_views(session, db_url, "forest1", views_forest1)


def get_queries_forest(session, url_base):
    return get_queries(session, url_base, "forest1", list(views_forest1.keys()))
