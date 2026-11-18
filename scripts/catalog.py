"""Build the public catalog from the bilingual plugin pages. Requires Python 3.8+."""

import argparse
import html
import json
import posixpath
import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl, quote, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
KINDS = {
    'guidance': ('Skills', '技能'),
    'cli': ('CLI tools', '命令行工具'),
    'service': ('Services', '服务'),
    'ui': ('UI extensions', '界面扩展'),
}
REQUIRED = {'Author', 'Version', 'Source', 'License', 'License kind'}
OPTIONAL = {'Repository', 'Verification', 'Verified platform', 'Verified version',
            'Evidence', 'ZIP SHA-256', 'Manifest ID'}
COMMIT = re.compile(r'(?:[a-fA-F0-9]{40}|[a-fA-F0-9]{64})')


def summary(markdown, heading):
    section = re.search(r'^## ' + re.escape(heading) + r'[ \t]*\n(.*?)(?=^## |\Z)', markdown, re.M | re.S)
    if section:
        text = section[1].strip().split('\n\n')[0].strip()
        if text and not text.startswith(('#', '|')):
            return ' '.join(line.strip() for line in text.splitlines())
    raise ValueError('Missing opening description under ## ' + heading)


def link(cell):
    found = re.fullmatch(r'\[([^\[\]]+)\]\((https://[^\s]+)\)', cell)
    if not found:
        raise ValueError('Expected a labeled Markdown HTTPS link: ' + cell)
    label, url = found.groups()
    parsed = urlsplit(url)
    if not label.strip() or not parsed.hostname or parsed.username is not None or parsed.password is not None:
        raise ValueError('Invalid public link: ' + cell)
    return label, url


def release_table(markdown):
    section = re.search(r'^## Release / 版本\s*\n(.*?)(?=^## |\Z)', markdown, re.M | re.S)
    if not section:
        raise ValueError('Missing ## Release / 版本')
    rows = [line.strip() for line in section[1].splitlines() if line.strip()]
    if len(rows) < 2 or not re.fullmatch(r'\|\s*:?-+:?\s*\|\s*:?-+:?\s*\|', rows[1]):
        raise ValueError('Expected a two-column release table')
    fields = {}
    for row in rows[2:]:
        match = re.fullmatch(r'\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|', row)
        if not match:
            raise ValueError('Invalid release table row: ' + row)
        key, value = match.groups()
        if key in fields or key not in REQUIRED | OPTIONAL or not value.strip():
            raise ValueError('Duplicate, empty or unknown release field: ' + key)
        fields[key] = value
    missing = REQUIRED - fields.keys()
    if missing:
        raise ValueError('Missing release fields: ' + ', '.join(sorted(missing)))
    return fields


def check_download(url):
    parsed = urlsplit(url)
    parts = unquote(parsed.path).strip('/').split('/')
    if parsed.hostname == 'github.com':
        if parts[2:4] == ['releases', 'latest']:
            raise ValueError('Use a versioned release asset')
        ref = parts[3:] if parts[2:3] in (['raw'], ['blob'], ['archive']) else []
    elif parsed.hostname == 'raw.githubusercontent.com':
        ref = parts[2:]
    else:
        return
    if ref and (ref[0] in {'HEAD', 'main', 'master'} or ref[:2] == ['refs', 'heads']):
        raise ValueError('Use a fixed download revision')


def read_plugin(path):
    kind, plugin_id = path.parent.name, path.stem
    if kind not in KINDS or not plugin_id.strip():
        raise ValueError('Use plugins/<kind>/<id>.md')
    md = path.read_text(encoding='utf-8')
    title = re.match(r'# ([^\n]+)\n', md)
    if not title or not title[1].strip():
        raise ValueError('Missing plugin title')
    en, zh = summary(md, 'English'), summary(md, '简体中文')
    fields = release_table(md)
    version, download = link(fields['Version'])
    check_download(download)
    _, source = link(fields['Source'])
    parsed = urlsplit(source)
    segments = unquote(parsed.path).split('/') + [v for _, v in parse_qsl(parsed.query)]
    commits = {s.lower() for s in segments if COMMIT.fullmatch(s)}
    if len(commits) != 1:
        raise ValueError('Source link must identify one full Git commit')
    license_name, license_url = link(fields['License'])
    if fields['License kind'] not in ('source-available', 'open-source'):
        raise ValueError('Unknown license category')
    data = dict(id=plugin_id, name=title[1].strip(), kind=kind, description=en, descriptionZhCN=zh, author=fields['Author'],
                version=version, sourceCommit=commits.pop(), sourceUrl=source)
    if 'Repository' in fields:
        data['repositoryUrl'] = link(fields['Repository'])[1]
    data.update(licenseKind=fields['License kind'], licenseName=license_name,
                licenseUrl=license_url, downloadUrl=download)
    if 'Verification' in fields:
        mark = {'kind': fields['Verification']}
        if mark['kind'] not in ('publisher', 'installation'):
            raise ValueError('Unknown verification kind')
        for label, key in [('Verified platform', 'platform'), ('Verified version', 'version')]:
            if label in fields:
                mark[key] = fields[label]
        if mark['kind'] == 'installation' and (not mark.get('platform') or mark.get('version') != version):
            raise ValueError('Installation verification requires the tested platform and listed version')
        if 'Evidence' in fields:
            mark['evidenceUrl'] = link(fields['Evidence'])[1]
        data['verification'] = mark
    elif {'Verified platform', 'Verified version', 'Evidence'} & fields.keys():
        raise ValueError('Supply a verification kind for the verification record')
    if {'Manifest ID', 'ZIP SHA-256'} & fields.keys():
        digest = fields.get('ZIP SHA-256', '')
        if not re.fullmatch('[0-9a-f]{64}', digest) or not fields.get('Manifest ID'):
            raise ValueError('Direct install requires lowercase ZIP SHA-256 and exact manifest ID')
        data['install'] = {'sha256': digest, 'manifestId': fields['Manifest ID']}
    return data, (en, zh)


def table_text(s):
    # The summaries are plain text. Preserve their punctuation inside a Markdown table.
    return re.sub(r'([\\|\[\]_*~`])', r'\\\1', html.escape(s, quote=False))


PAGE_SIZE = 25
GENERATED_PAGE = '<!-- Generated by scripts/catalog.py: category continuation -->'
CONTINUATION = re.compile(r'page-(?:[2-9]|[1-9][0-9]+)(?:\.zh-CN)?\.md')


def category_path(kind, page, lang):
    suffix = '.zh-CN.md' if lang else '.md'
    base = Path('categories')
    return base / (kind + suffix) if page == 1 else base / kind / f'page-{page}{suffix}'


def category_page(kind, plugins, lang, page, page_count):
    current = category_path(kind, page, lang)

    def href(target):
        relative = posixpath.relpath(target.as_posix(), current.parent.as_posix())
        return relative if relative.startswith('../') else './' + relative

    language = '.zh-CN' if lang else ''
    other_language = href(category_path(kind, page, not lang))
    switcher = (f'[English]({other_language}) · 简体中文' if lang else
                f'English · [简体中文]({other_language})')
    home = '插件目录' if lang else 'Plugin directory'
    home_path = href(Path(f'README{language}.md'))
    lines = [GENERATED_PAGE, ''] if page > 1 else []
    lines += ['# ' + KINDS[kind][lang], '', switcher, '', f'[{home}]({home_path})', '']
    if plugins:
        lines += ['| 插件 | 用途 |' if lang else '| Plugin | What it does |', '| --- | --- |']
        for plugin, descriptions in plugins:
            name = table_text(plugin['name'])
            target = href(Path('plugins') / kind / (quote(plugin['id'], safe='') + '.md'))
            lines.append(f"| [{name}]({target}) | {table_text(descriptions[lang])} |")
    else:
        submit = '提交首个插件' if lang else 'Submit the first plugin'
        message = '此分类暂未收录插件。' if lang else 'No plugins listed yet.'
        lines.append(f'{message} [{submit}]({href(Path(f"CONTRIBUTING{language}.md"))})')
    if page_count > 1:
        links = []
        if page > 1:
            previous = '上一页' if lang else 'Previous'
            links.append(f'[{previous}]({href(category_path(kind, page - 1, lang))})')
        links.append(f'第 {page} 页，共 {page_count} 页' if lang else f'Page {page} of {page_count}')
        if page < page_count:
            following = '下一页' if lang else 'Next'
            links.append(f'[{following}]({href(category_path(kind, page + 1, lang))})')
        lines += ['', ' · '.join(links)]
    return '\n'.join(lines) + '\n'


def generate(root):
    groups = {kind: [] for kind in KINDS}
    seen = set()
    for path in sorted((root / 'plugins').rglob('*.md')):
        try:
            if len(path.relative_to(root / 'plugins').parts) != 2:
                raise ValueError('Expected plugins/<kind>/<id>.md')
            data, descriptions = read_plugin(path)
            if data['id'] in seen:
                raise ValueError('Duplicate directory ID: ' + data['id'])
        except ValueError as exc:
            raise ValueError(f'{path.relative_to(root)}: {exc}') from exc
        seen.add(data['id'])
        groups[data['kind']].append((data, descriptions))
    outputs, entries = {}, []
    for kind, items in groups.items():
        items.sort(key=lambda item: (item[0]['name'].casefold(), item[0]['id']))
        entries.extend(data for data, _ in items)
        page_count = max(1, (len(items) + PAGE_SIZE - 1) // PAGE_SIZE)
        for page in range(1, page_count + 1):
            page_items = items[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]
            for lang in (0, 1):
                outputs[root / category_path(kind, page, lang)] = category_page(kind, page_items, lang, page, page_count)
    outputs[root / 'plugins.json'] = json.dumps({'schemaVersion': 1, 'plugins': entries},
                                                ensure_ascii=False, indent=2) + '\n'
    return outputs


def continuation_changes(root, outputs):
    """Find obsolete owned pages and protect hand-written files at new page paths."""
    obsolete = []
    for kind in KINDS:
        folder = root / 'categories' / kind
        if folder.is_symlink():
            if any(page.parent == folder for page in outputs):
                raise ValueError(f'Category output directory is a symbolic link: {folder.relative_to(root)}')
            continue
        for page in sorted(folder.glob('page-*.md')):
            if not CONTINUATION.fullmatch(page.name):
                continue
            owned = False
            if page.is_file() and not page.is_symlink():
                with page.open('rb') as reader:
                    owned = reader.readline(len(GENERATED_PAGE) + 2).rstrip(b'\r\n') == GENERATED_PAGE.encode('ascii')
            if page in outputs and not owned:
                raise ValueError(f'Category page path is already in use: {page.relative_to(root)}')
            if owned and page not in outputs:
                obsolete.append(page)
    return obsolete


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Report generated files that need updating')
    args = parser.parse_args()
    try:
        outputs = generate(ROOT)
        obsolete = continuation_changes(ROOT, outputs)
    except ValueError as exc:
        sys.exit(str(exc))
    stale = []
    for path, content in outputs.items():
        if path.is_file() and path.read_bytes() == content.encode('utf-8'):
            continue
        if args.check:
            stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content.encode('utf-8'))
    for path in obsolete:
        if args.check:
            stale.append(str(path.relative_to(ROOT)))
        else:
            path.unlink()
    if stale:
        sys.exit('Run python3 scripts/catalog.py to update: ' + ', '.join(stale))


if __name__ == '__main__':
    main()
