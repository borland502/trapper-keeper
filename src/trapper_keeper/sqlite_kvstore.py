"""https://stackoverflow.com/questions/47237807/use-sqlite-as-a-keyvalue-store"""
import contextlib
import sqlite3
from pathlib import Path


class KeyValueStore(dict):
  """_summary_
  Args:
      dict (_type_): _description_
  """

  def __init__(self, filename: Path):
    """_summary_
    Args:
        filename (_type_, optional): _description_. Defaults to KV_STORE.
    """
    super().__init__()
    self.conn = sqlite3.connect(filename)
    self.conn.execute("CREATE TABLE IF NOT EXISTS kv (key text unique, value text)")

  def __len__(self):
    rows = self.conn.execute("SELECT COUNT(*) FROM kv").fetchone()[0]
    return rows if rows is not None else 0

  def iterkeys(self):
    c = self.conn.cursor()
    for row in c.execute("SELECT key FROM kv"):
      yield row[0]

  def itervalues(self):
    c = self.conn.cursor()
    for row in c.execute("SELECT value FROM kv"):
      yield row[0]

  def iteritems(self):
    c = self.conn.cursor()
    for row in c.execute("SELECT key, value FROM kv"):
      yield row[0], row[1]

  def keys(self):
    return list(self.iterkeys())

  def values(self):
    return list(self.itervalues())

  def items(self):
    return list(self.iteritems())

  def __contains__(self, key):
    return self.conn.execute("SELECT 1 FROM kv WHERE key = ?", (key,)).fetchone() is not None

  def __getitem__(self, key):
    item = self.conn.execute("SELECT value FROM kv WHERE key = ?", (key,)).fetchone()
    if item is None:
      raise KeyError(key)
    return item[0]

  def __setitem__(self, key, value):
    self.conn.execute("REPLACE INTO kv (key, value) VALUES (?,?)", (key, value))

  def __delitem__(self, key):
    if key not in self:
      raise KeyError(key)
    self.conn.execute("DELETE FROM kv WHERE key = ?", (key,))

  def __iter__(self):
    return self.iterkeys()

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.conn.close()
