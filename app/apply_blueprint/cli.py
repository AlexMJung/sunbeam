from app import app, db
import os
import csv
import models
import ast
import click

path = os.path.dirname(os.path.realpath(__file__))
name = path.split("/")[-1]

@app.cli.group(name = name)
def cli():
    """commands for blueprint"""
    pass

@cli.command("seed_from_csvs")
def seed_from_csvs():
    """Seed from CSV"""
    seeds = []
    for f in [f for f in os.listdir("{0}/seeds/".format(path))]:
        parts = f.split(".")
        if parts[1] == os.environ['APP_CONFIG_MODE']:
            model_name = parts[0]
            with open("{0}/seeds/{1}".format(path, f), 'rb') as f:
                click.echo("Seeding {0}".format(model_name))
                for d in csv.DictReader(f):
                    seeds.append(populate(eval("models.{0}()".format(model_name)), d))
    db.session.add_all(seeds)
    db.session.commit()
cli.add_command(seed_from_csvs)

def populate(seed, dict):
    for k in dict.keys():
        try:
            setattr(seed, k, ast.literal_eval("{0}".format(dict[k])))
        except Exception as e:
            setattr(seed, k, ast.literal_eval("\"{0}\"".format(dict[k])))
    return seed
