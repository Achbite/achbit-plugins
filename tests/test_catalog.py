import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote

from scripts.catalog import generate

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / 'templates/plugin.md').read_text(encoding='utf-8')


class CatalogTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

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

    def test_category_pagination_preserves_all_entries_and_relative_navigation_in_both_languages(self):
        def add_items(start, end):
            for i in range(start, end):
                self.add('ui', f'item {i:02}', TEMPLATE.replace('# Plugin name', f'# Item {i:02}'))

        def targets(page):
            links = re.findall(r'\[[^]]+\]\(([^)]+)\)', outputs[page])
            return [(page.parent / unquote(link)).resolve() for link in links]

        add_items(0, 25)
        outputs = generate(self.root)
        self.assertFalse(any(path.parent.parent == self.root / 'categories' for path in outputs))
        add_items(25, 51)
        outputs = generate(self.root)
        categories = self.root / 'categories'
        expected = sorted((self.root / 'plugins/ui').glob('*.md'))
        for suffix, other in [('', '.zh-CN'), ('.zh-CN', '')]:
            pages = [categories / f'ui{suffix}.md', categories / f'ui/page-2{suffix}.md',
                     categories / f'ui/page-3{suffix}.md']
            for index, page in enumerate(pages):
                with self.subTest(page=page.name):
                    linked = targets(page)
                    plugins = [path for path in linked if path.parent == self.root / 'plugins/ui']
                    self.assertEqual(plugins, expected[index * 25:(index + 1) * 25])
                    paired = page.with_name(('ui' if index == 0 else f'page-{index + 1}') + other + '.md')
                    navigation = [paired, self.root / f'README{suffix}.md']
                    if index:
                        navigation.append(pages[index - 1])
                    if index < len(pages) - 1:
                        navigation.append(pages[index + 1])
                    self.assertCountEqual([path for path in linked if path not in plugins], navigation)
        self.assertEqual(len(json.loads(outputs[self.root / 'plugins.json'])['plugins']), 51)

    def test_shrinking_catalog_reports_and_removes_only_its_generated_continuations(self):
        for i in range(26):
            extra = self.add('service', f'service-{i:02}')
        (self.root / 'scripts').mkdir()
        tool = self.root / 'scripts/catalog.py'
        shutil.copy(ROOT / 'scripts/catalog.py', tool)
        command = [sys.executable, str(tool)]
        subprocess.run(command, check=True)
        category = self.root / 'categories/service'
        generated = [category / 'page-2.md', category / 'page-2.zh-CN.md']
        manual = [category / 'notes.md', category / 'page-9.md']
        for path in manual:
            path.write_text('# Maintainer notes\n', encoding='utf-8')
        extra.unlink()
        result = subprocess.run(command + ['--check'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        for path in generated:
            self.assertIn(str(path.relative_to(self.root)), result.stderr)
            self.assertTrue(path.is_file())
        subprocess.run(command, check=True)
        subprocess.run(command + ['--check'], check=True)
        self.assertFalse(any(path.exists() for path in generated))
        for path in manual:
            self.assertEqual(path.read_text(encoding='utf-8'), '# Maintainer notes\n')
        # A manually authored page at a newly needed path must also survive generation.
        generated[0].write_text('# Maintainer notes\n', encoding='utf-8')
        self.add('service', 'new-plugin')
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(str(generated[0].relative_to(self.root)), result.stderr)
        self.assertEqual(generated[0].read_text(encoding='utf-8'), '# Maintainer notes\n')


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
