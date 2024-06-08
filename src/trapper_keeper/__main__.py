"""Trapper Keeper main module."""
from typer import Typer

app = Typer()

@app.command(name="pack", short_help="Pack will create any files which are missing as well as the Keepass database itself.")
def pack_db():
  pass

def unpack_db():
  pass

def repack_db():
  pass
