/**
 * Binding CouchDB for YCSB using RestClient.
 */
package site.ycsb.webservice.rest;

import site.ycsb.*;
import java.util.*;

/**
 * YCSB binding for CouchDB using RestClient.
 */
public class CouchDBRestBinding extends DB {
  private RestClient client;
  private String dbName;

  @Override
  public void init() {
    dbName = getProperties().getProperty("couchdb.dbname", "forest1");

    client = new RestClient();
    client.setProperties(getProperties());
    try {
      client.init();
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public Status insert(String table, String key, Map<String, ByteIterator> values) {
    Map<String, ByteIterator> dataMap = new HashMap<>();
    Map<String, Object> doc = new HashMap<>();
    doc.put("_id", key);
    for (Map.Entry<String, ByteIterator> entry : values.entrySet()) {
      doc.put(entry.getKey(), entry.getValue().toString());
    }
    try {
      String json = new com.fasterxml.jackson.databind.ObjectMapper().writeValueAsString(doc);
      dataMap.put("data", new StringByteIterator(json));
      return client.insert(table, "/" + dbName + "/" + key, dataMap);
    } catch (Exception e) {
      e.printStackTrace();
      return Status.ERROR;
    }
  }

  @Override
  public Status read(String table, String key, Set<String> fields, Map<String, ByteIterator> result) {
    return client.read(table, "/" + dbName + "/" + key, fields, result);
  }

  @Override
  public Status delete(String table, String key) {
    try {
      Map<String, ByteIterator> result = new HashMap<>();
      Status readStatus = client.read(table, "/" + dbName + "/" + key, null, result);
      if (readStatus != Status.OK) {
        return readStatus;
      }
      String body = result.get("response").toString();
      String rev = new com.fasterxml.jackson.databind.ObjectMapper().readTree(body).get("_rev").asText();
      return client.delete(table, "/" + dbName + "/" + key + "?rev=" + rev);
    } catch (Exception e) {
      e.printStackTrace();
      return Status.ERROR;
    }
  }

  @Override
  public Status update(String table, String key, Map<String, ByteIterator> values) {
    try {
      Map<String, ByteIterator> result = new HashMap<>();
      Status readStatus = client.read(table, "/" + dbName + "/" + key, null, result);
      if (readStatus != Status.OK) {
        return readStatus;
      }
      String body = result.get("response").toString();
      Map<String, Object> doc = new com.fasterxml.jackson.databind.ObjectMapper().readValue(body, HashMap.class);
      for (Map.Entry<String, ByteIterator> entry : values.entrySet()) {
        doc.put(entry.getKey(), entry.getValue().toString());
      }
      String updatedJson = new com.fasterxml.jackson.databind.ObjectMapper().writeValueAsString(doc);
      Map<String, ByteIterator> payload = new HashMap<>();
      payload.put("data", new StringByteIterator(updatedJson));
      return client.update(table, "/" + dbName + "/" + key, payload);
    } catch (Exception e) {
      e.printStackTrace();
      return Status.ERROR;
    }
  }

  @Override
  public Status scan(String table, String startkey, int recordcount, Set<String> fields,
                     Vector<HashMap<String, ByteIterator>> result) {
    try {
      String uri = "/" + dbName + "/_all_docs?include_docs=true&startkey=\"" + startkey + "\"&limit=" + recordcount;
      Map<String, ByteIterator> response = new HashMap<>();
      Status status = client.read(table, uri, null, response);
      if (status != Status.OK) {
        return status;
      }

      String json = response.get("response").toString();
      com.fasterxml.jackson.databind.JsonNode root = new com.fasterxml.jackson.databind.ObjectMapper().readTree(json);
      for (com.fasterxml.jackson.databind.JsonNode row : root.get("rows")) {
        com.fasterxml.jackson.databind.JsonNode doc = row.get("doc");
        HashMap<String, ByteIterator> rowMap = new HashMap<>();
        for (Iterator<String> it = doc.fieldNames(); it.hasNext();) {
          String field = it.next();
          if (!field.startsWith("_") && (fields == null || fields.contains(field))) {
            rowMap.put(field, new StringByteIterator(doc.get(field).asText()));
          }
        }
        result.add(rowMap);
      }
      return Status.OK;
    } catch (Exception e) {
      e.printStackTrace();
      return Status.ERROR;
    }
  }

  @Override
  public void cleanup() throws DBException {}

}
