from app import app
import models
import os

path = os.path.dirname(os.path.realpath(__file__))
name = path.split("/")[-1]

@app.cli.group(name = name)
def cli():
    """commands for blueprint"""
    pass

@cli.command("sync_parents")
def sync():
    """Sync parents from TC to QBO"""
    with app.test_request_context():
        models.sync_parents()
cli.add_command(sync)
