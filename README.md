# Achbit Plugin Directory

English · [简体中文](./README.zh-CN.md)

The Plugin Marketplace in Achbit Settings reads [plugins.json](./plugins.json) from this repository. Each entry links to the author's source code, license and download for a specific plugin version. Some entries also link to a verification record.

## Download and install a plugin

Open the marketplace, select a plugin and check its author, version and license. Choose **Download** to open the author's download in your browser. If the author provides a ZIP, keep it intact. In Achbit's plugin settings, select the local ZIP, review the preview and confirm installation. Your local Achbit instance manages installation and activation.

## Submit or update a listing

1. Publish the source and its license in a public repository. Record the full Git commit ID for the version you are submitting.
2. Publish a standalone package for that version on your project's release page or through a public download service. A ZIP must contain a supported manifest or `SKILL.md` at its root. Include the entry point, resources and license files the plugin needs.
3. Branch from this directory's `main`, edit `plugins.json` and open a pull request. When updating a listing, keep the directory ID and update the version, pinned source, applicable license link and download URL.
4. Include links to the source and download, along with steps a reviewer can follow to check the package. Maintainers check public access, the relationship between the package and source, the license category and the plugin's entry point. Authors may also submit a record that states what they verified.

### Directory format

The top level is `{ "schemaVersion": 1, "plugins": [...] }`. The last two fields in this table are optional.

| Field | What to provide |
| --- | --- |
| `id`, `name`, `description` | A stable, unique directory ID, a display name and a short description of what the plugin does. |
| `kind` | One of `guidance` (a Skill), `cli`, `service` or `ui`. |
| `author`, `version` | The publisher's name and the plugin version being listed. |
| `sourceCommit`, `sourceUrl` | The full Git commit ID and a URL containing that ID, pointing to the source directory, file or commit. |
| `licenseKind`, `licenseName`, `licenseUrl` | The category, license name and a link to the license text for this version. Choose `open-source` for an open-source license. Choose `source-available` when the source is public under terms that restrict how it may be used or shared beyond what an open-source license permits. |
| `downloadUrl` | A public HTTPS link to the author's package for this exact version. A tagged release asset or a file pinned to a Git commit works. |
| `repositoryUrl` | Optional. The author's project homepage. |
| `verification` | Optional. Use `{"kind":"publisher"}` for a documented publisher identity check. For a documented installation check, use `{"kind":"installation","platform":"macos-arm64","version":"1.2.3"}`, substituting the actual platform and the listed plugin version. Either kind can include an `evidenceUrl` linking to the public record. |

Use HTTPS for external links. The download should work without an account and resolve to the named version. Floating branches and `latest` links can change after review. Include a verification field only when evidence supports the claim. An installation record covers the platform, version and actions it describes.
