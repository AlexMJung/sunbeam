import unittest
import models
import flask
from app import app, db
import os

blueprint_name = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]

class TestCase(unittest.TestCase):
    def test_parent_parents_from_tc(self):
        parents = models.Parent.parents_from_tc(278)
        print parents
