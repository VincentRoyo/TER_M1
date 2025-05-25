from .utils import create_views, get_queries

views_forest3 = {
    "arbres_par_plot_sousplot": {
        "map": "function(doc){ if(doc.type==='Feature' && doc.properties && doc.properties.trees){ doc.properties.trees.features.forEach(function(tree){ emit([doc.properties.plot.id, tree.properties.sub_plot_id], tree.properties.tree_id); }); } }",
        "reduce": "function(keys, values, rereduce){ return rereduce ? [].concat.apply([], values) : Array.from(new Set(values)); }"
    },

    "especes_par_plot_sousplot": {
        "map": "function(doc){ if(doc.type==='Feature' && doc.properties && doc.properties.trees){ doc.properties.trees.features.forEach(function(tree){ emit([doc.properties.plot.id, tree.properties.sub_plot_id], tree.properties.tree_species_species); }); } }",
        "reduce": "function(keys, values, rereduce){ var s = {}; (rereduce ? [].concat.apply([], values) : values).forEach(function(x){ s[x] = true; }); return Object.keys(s); }"
    },

    "especes_par_plot": {
        "map": "function(doc){ if(doc.type==='Feature' && doc.properties && doc.properties.trees){ doc.properties.trees.features.forEach(function(tree){ emit(doc.properties.plot.id, tree.properties.tree_species_species); }); } }",
        "reduce": "function(keys, values, rereduce){ var s = {}; (rereduce ? [].concat.apply([], values) : values).forEach(function(x){ s[x] = true; }); return Object.keys(s); }"
    },

    "nb_especes_par_plot_sousplot": {
        "map": "function(doc){ if(doc.type==='Feature' && doc.properties && doc.properties.trees){ doc.properties.trees.features.forEach(function(tree){ emit([doc.properties.plot.id, tree.properties.sub_plot_id], tree.properties.tree_species_species); }); } }",
        "reduce": "function(keys, values, rereduce){ var s = {}; (rereduce ? [].concat.apply([], values) : values).forEach(function(x){ s[x] = true; }); return Object.keys(s).length; }"
    },

    "nb_especes_par_plot": {
        "map": "function(doc){ if(doc.type==='Feature' && doc.properties && doc.properties.trees){ doc.properties.trees.features.forEach(function(tree){ emit(doc.properties.plot.id, tree.properties.tree_species_species); }); } }",
        "reduce": "function(keys, values, rereduce){ var s = {}; (rereduce ? [].concat.apply([], values) : values).forEach(function(x){ s[x] = true; }); return Object.keys(s).length; }"
    },

    "plots_sousplots_location": {
        "map": "function(doc){ if(doc.type==='Feature' && doc.properties && doc.properties.plot && doc.properties.trees){ var subs = {}; doc.properties.trees.features.forEach(function(tree){ subs[tree.properties.sub_plot_id] = true; }); emit(doc.properties.plot.id, { location: doc.properties.plot.location, sub_plots: Object.keys(subs) }); } }",
        "reduce": "function(keys, values, rereduce){ var loc = values[0].location; var all = {}; values.forEach(function(v){ v.sub_plots.forEach(function(s){ all[s] = true; }); }); return { location: loc, sub_plots: Object.keys(all) }; }"
    }
}

def create_views_forest(session, db_url):
    create_views(session, db_url, "forest3", views_forest3)


def get_queries_forest(session, url_base):
    return get_queries(session, url_base, "forest3", list(views_forest3.keys()))
