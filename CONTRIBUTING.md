# Contributing a plugin

English · [简体中文](./CONTRIBUTING.zh-CN.md) · [Directory](./README.md)

Check the [open pull requests](https://github.com/Achbite/achbit-plugins/pulls) for an existing submission. For a new listing, copy [the template](./templates/plugin.md) to `plugins/<kind>/<id>.md`. Choose `guidance`, `cli`, `service` or `ui` for the kind and a stable, lowercase directory ID such as `text-echo`. Keep that ID when updating a release. The directory ID identifies the listing. The package can have its own, different manifest ID.

## Write the page

Use the plugin's display name as the title. Under **English** and **简体中文**, describe what a reader can actually do with the plugin. The first paragraph in each language appears in its category table. The index uses the English summary for `description` and the Chinese one for `descriptionZhCN`. Use plain text for those paragraphs. The rest of each section can include Markdown links, configuration steps, screenshots or an example of a first run.

The **Release / 版本** table supplies the common release facts for both languages. Keep its field names as shown in the template.

| Field | What to enter |
| --- | --- |
| Author | The publisher's public name. |
| Version | A Markdown link with the plugin version as the label. Link to the author's anonymously accessible package for that exact version, such as a tagged release asset. |
| Source | A link to the reviewed source directory, file or commit. Include the full Git commit ID in the path or a query parameter. |
| License | A link with the license name as its label, pointing to the terms applicable to this version. |
| License kind | Use `open-source` for an open-source license. Use `source-available` for publicly readable code published under other terms. |
| Repository | Optional link to the author's project. |
| ZIP SHA-256 and Manifest ID | Optional pair for direct installation in clients that support it. Record the 64 lowercase hex characters of the exact downloadable ZIP and the case-sensitive ID returned by `achbit-cli plugins inspect`, including any spaces. |
| Verification | Optional `publisher` or `installation` for a documented publisher identity or installation check. Installation requires separate **Verified platform** and **Verified version** rows with the tested platform and the listed plugin version. An **Evidence** row can link to the record. |

Use public HTTPS links. A package published on the author's release page can carry its own plugin version. A standalone ZIP includes its manifest or `SKILL.md` at the root plus the necessary entry points, resources and license files. When supplying direct-install fields, download the archive, hash those bytes and inspect that same archive. A digest identifies the bytes. An installation verification describes a separate observation with a stated version and platform. Download-only entries can omit the pair.

## Open a pull request

1. Update the plugin page, including its English and Chinese sections, in one pull request. For a new release, check the source, license, download and any optional installation or verification facts against the new version.
2. From the repository root, run `python3 scripts/catalog.py`. This generates the alphabetical category pages and the schema-version-1 `plugins.json`. Include the generated changes in the PR. Run `python3 scripts/catalog.py --check` to confirm they match the pages. The generator uses the Python standard library.
3. Describe how a maintainer can obtain the package, compare it to the source and reproduce any verification you claim. Include the plugin page and its generated changes. The [pull request template](./.github/PULL_REQUEST_TEMPLATE.md) lists the review points.
