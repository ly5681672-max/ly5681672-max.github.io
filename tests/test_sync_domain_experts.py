import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    'domain_sync',
    Path(__file__).resolve().parents[1] / 'scripts/sync_domain_experts.py'
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SyncTests(unittest.TestCase):
    def test_bilingual_expert_name_identity(self):
        expert = {'id': 'cao_yueqiang', 'name': 'Yueqiang Cao（曹约强）',
                  'orcid': '0000-0002-1036-4049', 'openalex_author_id': 'A5084047416'}
        rows = {'results': [{'id': 'https://openalex.org/A5084047416',
                            'display_name': 'Yueqiang Cao',
                            'orcid': 'https://orcid.org/0000-0002-1036-4049',
                            'observed_orcids': []}]}
        from unittest.mock import patch
        with patch.object(module, 'fetch_json', return_value=rows):
            self.assertEqual(module.get_author_id(expert), 'A5084047416')

    def test_priority_journal_shortlist(self):
        self.assertIn('nature catalysis', module.PRIORITY_JOURNALS)
        self.assertNotIn('arxiv', module.PRIORITY_JOURNALS)

    def test_doi_validation(self):
        self.assertEqual(
            module.normalize_doi('https://doi.org/10.1038/S41929-026-01479-X'),
            '10.1038/s41929-026-01479-x'
        )
        self.assertIsNone(module.normalize_doi(''))
        self.assertIsNone(module.normalize_doi('arxiv:123'))

    def test_subject_relevance(self):
        self.assertEqual(module.match_relevance(
            'Knowledge graphs in heterogeneous catalysis', '', 'ai'
        )['relevance'], '高')
        self.assertIsNone(module.match_relevance('Machine learning for stock markets', '', 'ai'))
        self.assertEqual(module.match_relevance(
            'Titanium silicalite catalysts for epoxidation', '', 'epox'
        )['relevance'], '高')
        self.assertIsNone(module.match_relevance('Lithium ion battery cathodes', '', 'epox'))

    def test_abstract_reconstruction(self):
        self.assertEqual(module.reconstruct_abstract(
            {'science': [1], 'Open': [0]}
        ), 'Open science')

    def test_accented_surname(self):
        self.assertEqual(module.fold_name('Copéret'), 'coperet')
        self.assertEqual(module.fold_name('López'), 'lopez')


if __name__ == '__main__':
    unittest.main()
