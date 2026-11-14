import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    'voicecheck', Path(__file__).resolve().parents[1] / 'scripts/check_domain_expert_pronunciation.py'
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def person(locale='zh-CN', text='林栋', address_locale='zh-CN', short='林'):
    return {'id': 'lin_dong',
            'pronunciation': {'text': text, 'locale': locale, 'status': 'PROVISIONAL'},
            'preferred_address': {'label': '林教授', 'spoken_short_name': short,
                                  'locale': address_locale, 'status': 'PROVISIONAL'}}

class Tests(unittest.TestCase):
    def test_valid_full_and_short(self):
        self.assertEqual(m.validate([person()]), [])

    def test_wrong_locale(self):
        self.assertTrue(m.validate([person(locale='en-US')]))

    def test_mixed_full_name(self):
        self.assertTrue(m.validate([person(text='Dong Lin（林栋）')]))

    def test_missing_short_name(self):
        self.assertTrue(m.validate([person(short='')]))

    def test_wrong_short_locale(self):
        self.assertTrue(m.validate([person(address_locale='en-US')]))
