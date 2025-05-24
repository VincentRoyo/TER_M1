package site.ycsb.db;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Set;
import java.util.Vector;

import org.lightcouch.CouchDbClient;
import org.lightcouch.CouchDbProperties;
import org.lightcouch.Document;
import org.lightcouch.View;
import org.lightcouch.NoDocumentException;

import com.google.gson.JsonObject;
import site.ycsb.ByteArrayByteIterator;
import site.ycsb.ByteIterator;
import site.ycsb.DB;
import site.ycsb.DBException;
import site.ycsb.Status;

/**
 * CouchClient is a YCSB client for CouchDB. This class is responsible for 
 * managing database connections and performing CRUD operations on CouchDB.
 */
public class CouchClient extends DB {

  private CouchDbClient dbClient;
  private int batchSize;
  private List<JsonObject> batchInsertList;

  @Override
  public void init() throws DBException {
    CouchDbProperties properties = new CouchDbProperties();
    Properties props = getProperties();
    properties.setHost(props.getProperty("couchdb.host", "127.0.0.1"));
    properties.setPort(Integer.parseInt(props.getProperty("couchdb.port", "5984")));
    properties.setDbName(props.getProperty("couchdb.dbname", "forest1"));
    properties.setCreateDbIfNotExist(true);
    properties.setProtocol(props.getProperty("couchdb.protocol", "http"));
    properties.setUsername(props.getProperty("couchdb.username", "admin"));
    properties.setPassword(props.getProperty("couchdb.password", "password"));
    batchInsertList = new ArrayList<JsonObject>();
    batchSize = Integer.parseInt(props.getProperty("batchsize", "1000"));
    dbClient = new CouchDbClient(properties);
    super.init();
  }


  @Override
  public Status read(String table, String key, Set<String> fields, Map<String, ByteIterator> result) {
    try {
      JsonObject found = dbClient.find(JsonObject.class, key);
      if (null == found) {
        return Status.NOT_FOUND;
      }    
      if (fields != null) {
        JsonObject jsonObject = new JsonObject();
        jsonObject.add("_id", found.get("id"));
        jsonObject.add("_rev", found.get("_rev"));
        for (String field : fields) {
          jsonObject.add(field, found.get(field));
        }
        result.put(found.get("_id").toString(), new ByteArrayByteIterator(jsonObject.toString().getBytes()));
      }
    } catch (NoDocumentException e) {
      return Status.NOT_FOUND;
    }
    return Status.OK;
  }

  @Override
  public Status scan(String table, String startkey, int recordcount, Set<String> fields,
                     Vector<HashMap<String, ByteIterator>> result) {
    View view = dbClient.view("_all_docs").startKeyDocId(startkey).limit(recordcount).includeDocs(true);
    HashMap<String, ByteIterator> resultMap = new HashMap<String, ByteIterator>();
    List<JsonObject> list = view.query(JsonObject.class);

    if (fields != null) {
      for (JsonObject doc : list) {
        JsonObject jsonObject = new JsonObject();
        jsonObject.add("_id", doc.get("_id"));
        jsonObject.add("_rev", doc.get("_rev"));
        for (String field : fields) {
          jsonObject.add(field, doc.get(field));
        }
        resultMap.put(doc.get("_id").toString(), new ByteArrayByteIterator(jsonObject.toString().getBytes()));
      }
      result.add(resultMap);
    }

    return Status.OK;
  }

  @Override
  public Status update(String table, String key, Map<String, ByteIterator> values) {
    JsonObject jsonObject = dbClient.find(JsonObject.class, key);
    if (null == jsonObject) {
      return Status.NOT_FOUND;
    }
    for (Map.Entry<String, ByteIterator> entry : values.entrySet()) {
      jsonObject.addProperty(entry.getKey(), entry.getValue().toString());
    }
    dbClient.update(jsonObject);
    return Status.OK;
  }

  @Override
  public Status insert(String table, String key, Map<String, ByteIterator> values) {
    JsonObject jsonObject = new JsonObject();
    jsonObject.addProperty("_id", key);
    for (Map.Entry<String, ByteIterator> entry : values.entrySet()) {
      jsonObject.addProperty(entry.getKey(), entry.getValue().toString());
    }
    if (batchSize == 1) {
      dbClient.save(jsonObject);
    } else {
      batchInsertList.add(jsonObject);
      if (batchInsertList.size() == batchSize) {
        dbClient.bulk(batchInsertList, true);
        batchInsertList.clear();
      }
    }
    return Status.OK;
  }

  @Override
  public Status delete(String table, String key) {
    dbClient.remove(dbClient.find(Document.class, key));
    return Status.OK;
  }
}
