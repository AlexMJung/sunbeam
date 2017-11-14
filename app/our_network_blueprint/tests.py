import unittest
import models
import flask
from app import app, db
import os

blueprint_name = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]

class TestCase(unittest.TestCase):
    def test(self):
        pass
