# testing import
import unittest

# project imports
from command.loader import Loader

class loaderTests(unittest.TestCase):
    def test_create(self):
        loader = Loader()
        self.assertIsNotNone(loader)

    def test_loader_import(self):
        loader = Loader()
        loader.scan()
        self.assertGreater(loader.handlers,0)

    def test_loader_call(self):
        loader = Loader()
        loader.scan()
        f = loader.handlers['manage.status']
        self.assertIsNotNone(f())