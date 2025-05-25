def create_views(session, db_url, design_name, views_dict):
    """
    Crée ou met à jour un design doc pour une base CouchDB.

    Args:
        session: session requests
        db_url: URL complète vers la base (ex: http://.../forest1)
        design_name: nom du design doc (ex: "forest1")
        views_dict: dictionnaire des vues
    """
    design_doc = {
        "_id": f"_design/{design_name}",
        "language": "javascript",
        "views": views_dict
    }

    resp = session.get(f"{db_url}/_design/{design_name}")
    if resp.status_code == 200:
        design_doc["_rev"] = resp.json().get("_rev")

    session.put(f"{db_url}/_design/{design_name}", json=design_doc)


def get_queries(session, url_base, design_name, view_names):
    """
    Prépare les fonctions d'appel à chaque vue avec reduce + group par défaut.

    Args:
        session: session requests
        url_base: URL de la base (ex: http://.../forest1)
        design_name: nom du design doc (ex: "forest1")
        view_names: liste des noms de vues

    Returns:
        dict {view_name: lambda de requête}
    """
    def view(view_name, reduce=True, group=True, params=None):
        options = {
            "reduce": str(reduce).lower(),
            "group": str(group).lower(),
            "stale": "ok"
        }
        if params:
            options.update(params)
        return lambda: session.get(f"{url_base}/_design/{design_name}/_view/{view_name}", params=options)

    return {name: view(name) for name in view_names}

