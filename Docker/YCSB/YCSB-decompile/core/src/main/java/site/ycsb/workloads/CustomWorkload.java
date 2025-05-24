package site.ycsb.workloads;

import site.ycsb.ByteIterator;
import site.ycsb.DB;
import site.ycsb.WorkloadException;

import java.io.BufferedReader;
import java.io.FileReader;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Set;
import java.util.Vector;

/**
 * Custom workload that reads real _id values from a file instead of generating userXXXX keys.
 */
public class CustomWorkload extends CoreWorkload {

  private List<String> keys = new ArrayList<>();
  private Iterator<String> keyIterator;
  private Properties properties;
  private List<String> fieldNamesLocal;


  @Override
  public void init(Properties p) throws WorkloadException {
    super.init(p);

    this.properties = p;

    String keyFile = p.getProperty("customkey.file");
    table = p.getProperty("collection");

    if (table == null) {
      throw new WorkloadException("Missing required property: collection");
    }

    if (keyFile == null) {
      throw new WorkloadException("Missing required property: customkey.file");
    }

    try (BufferedReader reader = new BufferedReader(new FileReader(keyFile))) {
      String line;
      while ((line = reader.readLine()) != null) {
        keys.add(line.trim());
      }
    } catch (Exception e) {
      throw new WorkloadException("Error reading customkey.file: " + e.getMessage());
    }

    Collections.shuffle(keys);
    keyIterator = keys.iterator();

    int fieldcount = Integer.parseInt(p.getProperty("fieldcount", "10"));
    String fieldnameprefix = p.getProperty("fieldnameprefix", "field");
    fieldNamesLocal = new ArrayList<>();
    for (int i = 0; i < fieldcount; i++) {
    fieldNamesLocal.add(fieldnameprefix + i);
    }
  }

  @Override
  public boolean doInsert(DB db, Object threadstate) {
    return true;
  }

  @Override
  public boolean doTransaction(DB db, Object threadstate) {
    String operation = operationchooser.nextString();
    if(operation == null) {
      return false;
    }

    switch (operation) {
      case "READ":
        doCustomTransactionRead(db);
        break;
      case "SCAN":
        doCustomTransactionScan(db);
      default:
        break;
    }
    return true;
  }

   private void doCustomTransactionRead(DB db) {
    if (!keyIterator.hasNext()) {
      keyIterator = keys.iterator();
    }

    String keyname = keyIterator.next();
    Set<String> fields = null;

    boolean readallfields = Boolean.parseBoolean(properties.getProperty("readallfields", "true"));
    boolean readallfieldsbyname = Boolean.parseBoolean(properties.getProperty("readallfieldsbyname", "false"));
    boolean dataintegrity = Boolean.parseBoolean(properties.getProperty("dataintegrity", "false"));

    if (!readallfields) {
      int fieldIndex = fieldchooser.nextValue().intValue();
      String fieldname = fieldNamesLocal.get(fieldIndex);
      fields = new HashSet<>();
      fields.add(fieldname);
    } else if (dataintegrity || readallfieldsbyname) {
      fields = new HashSet<>(fieldNamesLocal);
    }

    Map<String, ByteIterator> result = new HashMap<>();
    db.read(table, keyname, fields, result);

    if (dataintegrity) {
      verifyRow(keyname, (HashMap<String, ByteIterator>) result);
    }
  }

  private void doCustomTransactionScan(DB db) {

    String startkeyname = keyIterator.next();
    int len = scanlength.nextValue().intValue();

    HashSet<String> fields = null;

    if (!readallfields) {
      // read a random field
      String fieldname = fieldNamesLocal.get(fieldchooser.nextValue().intValue());

      fields = new HashSet<String>();
      fields.add(fieldname);
    }

    db.scan(table, startkeyname, len, fields, new Vector<HashMap<String, ByteIterator>>());
  }
}