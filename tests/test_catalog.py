import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.catalog import generate

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / 'templates/plugin.md').read_text(encoding='utf-8')


class CatalogTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def add(self, kind, plugin_id, markdown=TEMPLATE):
        path = self.root / 'plugins' / kind / (plugin_id + '.md')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown, encoding='utf-8')
        return path

    def test_download_only_and_bilingual_browse(self):
        self.add('service', 'z-item', TEMPLATE.replace('# Plugin name', '# Zeta'))
        self.add('service', 'A plugin', TEMPLATE.replace('# Plugin name', '# Alpha'))
        outputs = generate(self.root)
        document = json.loads(outputs[self.root / 'plugins.json'])
        self.assertEqual(document['schemaVersion'], 1)
        self.assertEqual([p['name'] for p in document['plugins']], ['Alpha', 'Zeta'])
        entry = document['plugins'][0]
        self.assertNotIn('verification', entry)
        self.assertNotIn('install', entry)
        self.assertIn(entry['description'], outputs[self.root / 'categories/service.md'])
        self.assertIn(entry['descriptionZhCN'], outputs[self.root / 'categories/service.zh-CN.md'])
        self.assertIn('../plugins/service/A%20plugin.md', outputs[self.root / 'categories/service.md'])
        self.assertIn('提交首个插件', outputs[self.root / 'categories/cli.zh-CN.md'])

    def test_install_digest_and_manifest_are_paired_and_separate_from_verification(self):
        fields = ['| Manifest ID | Text Echo Declarative Skill |', '| ZIP SHA-256 | ' + 'a' * 64 + ' |']
        path = self.add('guidance', 'echo', TEMPLATE + '\n'.join(fields) + '\n')
        entry, = json.loads(generate(self.root)[self.root / 'plugins.json'])['plugins']
        self.assertEqual(entry['install'], {'sha256': 'a' * 64, 'manifestId': 'Text Echo Declarative Skill'})
        self.assertNotIn('verification', entry)
        for rows in [[fields[0]], [fields[1]], [fields[0], '| ZIP SHA-256 | invalid |']]:
            with self.subTest(rows=rows):
                path.write_text(TEMPLATE + '\n'.join(rows) + '\n')
                with self.assertRaisesRegex(ValueError, 'Direct install requires'):
                    generate(self.root)

    def test_directory_identity_license_source_and_verification_scope(self):
        path = self.add('cli', 'same-id')
        other = self.add('ui', 'same-id')
        with self.assertRaisesRegex(ValueError, 'Duplicate directory ID'):
            generate(self.root)
        other.unlink()
        for bad in [
            TEMPLATE.replace('## 简体中文', '## Translation pending'),
            TEMPLATE.replace('0123456789abcdef0123456789abcdef01234567', 'main'),
            TEMPLATE.replace('| open-source |', '| unlicensed |'),
            TEMPLATE.replace('https://example.org/releases/1.2.3/plugin.zip',
                             'https://github.com/example/plugin/releases/latest/download/plugin.zip'),
            TEMPLATE + '| Verification | installation |\n| Verified platform | macos-arm64 |\n| Verified version | 0.1.0 |\n',
        ]:
            with self.subTest(page=bad):
                path.write_text(bad)
                with self.assertRaises(ValueError):
                    generate(self.root)

    def test_check_reports_stale_generated_files_without_writing(self):
        self.add('ui', 'example')
        (self.root / 'scripts').mkdir()
        tool = self.root / 'scripts/catalog.py'
        shutil.copy(ROOT / 'scripts/catalog.py', tool)
        subprocess.run([sys.executable, str(tool)], check=True)
        generated = self.root / 'categories/ui.md'
        generated.write_text('outdated\n')
        result = subprocess.run([sys.executable, str(tool), '--check'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('categories/ui.md', result.stderr)
        self.assertEqual(generated.read_text(), 'outdated\n')


if __name__ == '__main__':
    unittest.main()
