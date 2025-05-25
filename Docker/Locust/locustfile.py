from Api.locust_api import ApiUser
from Mongo.locust_mongo import MongoUser
from Couchdb.locust_couchdb import CouchdbUser
from locust import events

@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument(
        "--query-count",
        type=int,
        default=0,
        help="Nombre de fois à exécuter chaque requête définie dans le workload"
    )

