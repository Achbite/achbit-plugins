# 插件投稿指南

[English](./CONTRIBUTING.md) · 简体中文 · [插件目录](./README.zh-CN.md)

先查看[正在审核的 PR](https://github.com/Achbite/achbit-plugins/pulls)，确认是否已有人投稿。要新增条目，将[模板](./templates/plugin.md)复制到 `plugins/<kind>/<id>.md`。分类可选 `guidance`、`cli`、`service`、`ui`。目录 ID 使用稳定的小写名称，例如 `text-echo`，更新版本时沿用。目录 ID 用来识别条目，安装包清单可以使用自己的 ID。

## 编写说明页

标题填写插件的显示名称。在 **English** 和 **简体中文** 两节中介绍插件能做什么。每种语言的第一段会显示在对应的分类表里，英文首段写入应用索引的 `description`，中文首段写入 `descriptionZhCN`。首段使用纯文本。后续内容可使用 Markdown 链接、配置步骤、截图或首次使用示例。

**Release / 版本** 表格供中英文共用。请沿用模板里的字段名。

| 字段 | 内容 |
| --- | --- |
| Author | 发布者的公开署名。 |
| Version | Markdown 链接，文字为插件版本。链接应能匿名下载作者发布的该版本安装包，例如带版本标签的 Release 附件。 |
| Source | 指向已核对的源码目录、文件或提交，在路径或查询参数中包含完整 Git 提交 ID。 |
| License | 链接文字为许可证名称，指向该版本适用的许可证原文。 |
| License kind | 使用开源许可证时选择 `open-source`。源码允许公开阅读但适用其他许可条款时，选择 `source-available`。 |
| Repository | 可选，作者项目主页链接。 |
| ZIP SHA-256 和 Manifest ID | 支持直接安装的客户端可使用这对选填字段。填写可下载 ZIP 原始字节的 SHA-256（64 位小写十六进制），以及 `achbit-cli plugins inspect` 实际返回的 ID，保留大小写和空格。 |
| Verification | 可选。有发布者身份核验依据时填 `publisher`，有实际安装核验记录时填 `installation`。安装核验须另填 **Verified platform** 和 **Verified version** 两行，注明实际平台和与条目相同的插件版本。可在 **Evidence** 行链接核验记录。 |

外部地址使用公开的 HTTPS 链接。作者发布页所附的插件包可以有独立版本。独立 ZIP 根目录需包含受支持的清单文件或 `SKILL.md`，包内附上必需的入口、资源和许可证文件。提供直接安装资料时，请实际下载安装包，计算摘要，用同一份 ZIP 检查清单 ID。摘要用于辨认文件内容。安装核验则记录某平台、某版本的一次实际操作。仅提供下载的条目可以省略安装资料。

## 提交 Pull Request

1. 在同一个 PR 中更新插件页面的英文、中文说明。更换版本时，请重新核对源码、许可证、下载链接以及可选的安装资料和核验记录。
2. 在仓库根目录运行 `python3 scripts/catalog.py`，生成按名称排序的分类页和 schema 版本为 1 的 `plugins.json`。将生成结果随说明页一起提交。运行 `python3 scripts/catalog.py --check` 可核对生成结果。脚本仅使用 Python 标准库。
3. 在 PR 说明中写清如何下载安装包、如何与源码比对，以及如何复现条目声称的核验结果。PR 中包含该插件页面和相应生成改动。审核事项见 [PR 模板](./.github/PULL_REQUEST_TEMPLATE.md)。
