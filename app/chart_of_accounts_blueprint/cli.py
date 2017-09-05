from app import app, db
import os

path = os.path.dirname(os.path.realpath(__file__))
name = path.split("/")[-1]

@app.cli.group(name = name)
def cli():
    """commands for blueprint"""
    pass

# @cli.command("some_command")
# def some_command():
#     """Some description"""
#     pass
# cli.add_command(sync)
