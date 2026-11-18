# Contributing a plugin

English · [简体中文](./CONTRIBUTING.zh-CN.md) · [Directory](./README.md)

External contributors open a pull request that adds or updates one plugin’s Markdown page. A maintainer reviews the source and the author’s package, runs `python3 scripts/catalog.py` on the PR branch, commits the generated category pages under `categories/` and the index `plugins.json`, and merges the approved listing.

## Write your plugin page

Copy the [template](./templates/plugin.md) to `plugins/<kind>/<id>.md`. Choose `guidance`, `cli`, `service` or `ui`. Use a stable directory ID such as `text-echo`. The package has its own manifest ID. For updates, edit the existing page.

Use the plugin’s display name as the title. Under **English** and **简体中文**, start with a plain-text paragraph explaining what the plugin does. Those paragraphs appear in the directory. Follow with instructions or an example that helps a reader try the plugin.

Keep the template’s **Release / 版本** field names and fill in these details.

| Field | What to provide |
| --- | --- |
| Author and Version | The publisher’s name and a public HTTPS link to the author’s package for this exact plugin version. Use the version as the link text. |
| Source | The reviewed source at its full Git commit ID. Put the ID in the URL path or a query parameter. |
| License and License kind | Link the license name to the terms for this version. Use `open-source` or `source-available` as applicable. |
| Repository | Optional link to the author’s project. |
| ZIP SHA-256 and Manifest ID | For direct installation, give the same ZIP’s SHA-256 in 64 lowercase hexadecimal characters and its exact ID from `achbit-cli plugins inspect`. Download-only entries can omit both. |
| Verification | Optional. Use `publisher` for a documented publisher check. Use `installation` for an observed install, with **Verified platform** and **Verified version** matching the listed release. **Evidence** can link to the record. |

## Where links and files go

- Relative Markdown links start at the page containing the link. For example, in [the Text Echo page](./plugins/guidance/text-echo.md), `../../verification/0.7.84-macos-arm64.md` reaches [the directory’s installation record](./verification/0.7.84-macos-arm64.md). In a release table, the optional **Evidence** link uses the record’s public HTTPS URL at its reviewed commit.
- Keep source, license text, screenshots and demos in the author’s repository. Link to the reviewed commit or fixed release over HTTPS. Publish the ZIP as an asset of the author’s versioned release and put that URL in **Version**. The central directory accepts listing pages and references. [Example author ZIP](https://github.com/Achbite/Achbit/releases/download/0.7.85/text-echo-0.7.84.zip)

## Maintainer review

The generator assigns up to 25 listings to each category page. For example, the UI category starts at `categories/ui.md` and continues at `categories/ui/page-2.md` when needed. Chinese pages use the `.zh-CN.md` suffix. Contributors only choose the plugin kind.

Compare the linked release package with the stated source and license. For direct-install entries, hash the downloaded ZIP and inspect that file’s manifest ID. Check any verification claim against its stated scope. After updating the generated files on the PR branch, you can optionally run `python3 scripts/catalog.py --check` to check for stale output.
