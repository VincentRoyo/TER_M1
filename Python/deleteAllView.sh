#!/bin/bash

# Vérifie que le nom de base est passé en argument
if [ -z "$1" ]; then
  echo "Usage: $0 nombase"
  exit 1
fi

DB="$1"
USER="admin"
PASS="pwd"
HOST="127.0.0.1:5984"

# Récupérer les IDs et révisions des documents de design
response=$(curl -s -u $USER:$PASS "http://$HOST/$DB/_all_docs?startkey=\"_design/\"&endkey=\"_design0\"&include_docs=false")

# Parcours des résultats avec Python pour supprimer
python3 -c "
import json
data = json.loads('''$response''')
for row in data.get('rows', []):
    print(f\"{row['id']} {row['value']['rev']}\")
" | while read id rev; do
  echo "Deleting $id (rev $rev) from $DB"
  curl -s -X DELETE "http://$USER:$PASS@$HOST/$DB/$id?rev=$rev"
done

