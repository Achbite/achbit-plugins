# Achbit 插件目录

Achbit 设置中的「插件市场」读取本仓库的 [plugins.json](./plugins.json)。插件由作者发布。目录提供源码、许可证、固定版本下载和已有的核验记录。

## 下载与安装

在市场中选择插件，查看作者、版本和许可证，然后点击下载。作者提供 ZIP 时可保留压缩包，在 Achbit 的插件设置中选取本地 ZIP，预览后确认安装。网络目录只用于浏览和下载，安装及启用由本地实例管理。

## 提交或更新条目

1. 在作者的公开源码仓库标明许可证，并记录本次发布使用的完整 Git 提交 ID。
2. 在作者仓库或公开下载服务发布该版本的独立安装包。ZIP 根目录放入受支持的 manifest 或 `SKILL.md`，并包含所需入口、资源及授权文件。
3. 从本仓库的 `main` 创建分支并修改 `plugins.json`，以 Pull Request 提交。更新时沿用已有的目录 ID，替换版本、固定源码、许可链接和下载地址。
4. 在 PR 说明中列出源码、下载和验证步骤。维护者复查公开访问、源代码与发布包的对应关系、许可证类型及实际插件入口。作者可以同时提交明确范围的验证记录。

目录格式为 `{ "schemaVersion": 1, "plugins": [...] }`。条目字段如下。

| 字段 | 内容 |
| --- | --- |
| `id`、`name`、`description` | 唯一且稳定的目录 ID、显示名称、简明用途 |
| `kind` | `guidance`（Skill）、`cli`、`service` 或 `ui` |
| `author`、`version` | 发布者署名和本条目对应的插件版本 |
| `sourceCommit`、`sourceUrl` | 完整 Git 提交 ID，以及 URL 中含该 ID 的源码目录、文件或提交链接 |
| `licenseKind`、`licenseName`、`licenseUrl` | `open-source` 或 `source-available`、许可证名称、该版本适用的许可证原文链接。可以阅读源码但许可存在使用限制的项目应根据实际条款选择 `source-available` |
| `downloadUrl` | 指向固定版本安装包的公开 HTTPS 链接。可使用发布版本的资产或固定 Git 提交中的文件 |
| `repositoryUrl` | 可选，作者项目主页 |
| `verification` | 可选。有可核查依据后才填写。发布者身份核验使用 `{"kind":"publisher"}`。安装核验使用 `{"kind":"installation","platform":"macos-arm64","version":"插件版本"}`；平台和插件版本均必填。两者均可使用 `evidenceUrl` 提供公开记录 |

条目中的外部链接使用 HTTPS。下载地址应能匿名取得指定版本；提交可核实链接时避免使用浮动分支或 latest 指针。对安装的验证只说明记录中列出的平台、版本与操作。
