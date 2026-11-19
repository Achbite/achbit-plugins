# 插件投稿指南

[English](./CONTRIBUTING.md) · 简体中文 · [插件目录](./README.zh-CN.md)

外部贡献者只需新增或更新一份插件 Markdown 说明页，并发起 PR。维护者审核源码和作者发布的安装包，在 PR 分支运行 `python3 scripts/catalog.py`，提交生成的 `categories/` 分类页和 `plugins.json` 索引，审核通过后合并收录。

## 编写插件页

将[模板](./templates/plugin.md)复制到 `plugins/<kind>/<id>.md`。分类可选 `guidance`、`cli`、`service` 或 `ui`。目录 ID 使用稳定名称，例如 `text-echo`。安装包有自己的清单 ID。发布新版本时更新原页面即可。

用插件显示名称作标题。在 **English** 和 **简体中文** 两节中，用自己的话各写一段纯文本介绍插件用途，供目录展示。后面可以写配置、用法或首次使用示例。引用第三方截图、演示和徽标时，链接到发布方的原始页面。

你保留自己对投稿内容享有的著作权。向目录提交原创代码或文字，即表示按本仓库的 MIT 许可证提供该内容。请只提交你有权按这些条款授权的材料。通过链接引用的插件包和第三方材料继续适用各自的条款。[MIT 许可证原文](./LICENSE)

沿用模板中 **Release / 版本** 表的字段名称，填写以下资料。

| 字段 | 填写内容 |
| --- | --- |
| Author 和 Version | 作者署名，以及作者发布的该版本安装包的公开 HTTPS 链接。链接文字为插件版本号。 |
| Source | 已核对的源码链接，路径或查询参数中包含完整 Git 提交 ID。 |
| License 和 License kind | 使用插件的许可证名称或 SPDX 标识，链接到已审核提交或发行版本中实际适用的条款。根据条款授予的权利填写 `open-source` 或 `source-available`。 |
| Repository | 可选，作者的项目主页。 |
| ZIP SHA-256 和 Manifest ID | 提供直接安装时，填入同一份 ZIP 的 SHA-256（64 位小写十六进制）和 `achbit-cli plugins inspect` 读出的完整清单 ID。仅提供下载的条目可省略这两项。 |
| Verification | 可选。已核实发布者身份时填 `publisher`。实际验证过安装时填 `installation`，并以 **Verified platform**、**Verified version** 写明实测平台与对应的条目版本。**Evidence** 可链接核验记录。 |

## 文件与链接放在哪里

- Markdown 相对链接从写下这条链接的页面算起。例如，在 [Text Echo 说明页](./plugins/guidance/text-echo.md) 中，`../../verification/0.7.84-macos-arm64.md` 指向[本目录的安装记录](./verification/0.7.84-macos-arm64.md)。若在版本表的 **Evidence** 字段引用该记录，请填写指向已审核提交的公开 HTTPS 链接。
- 源码、许可证原文和版本资产保存在发布方仓库，说明页使用指向固定提交或版本的公开 HTTPS 链接。ZIP 由作者作为带版本的 Release 附件发布，**Version** 字段填附件链接。中央目录只收录插件说明及引用。[作者 ZIP 实例](https://github.com/Achbite/Achbit/releases/download/0.7.85/text-echo-0.7.84.zip)

## 维护者审核

每个分类页最多展示 25 个插件，生成器按数量自动分页。例如，界面插件的分类首页为 `categories/ui.md`，需要续页时从 `categories/ui/page-2.md` 开始，中文页使用 `.zh-CN.md` 后缀。投稿人只需选择插件分类。

对照声明的源码和许可核对发布包，检查包内是否附有条款要求随包保留的许可文本、版权声明和第三方声明。许可证缺失或与包内内容冲突时，先请发布者在 PR 中澄清，再行合并。提供直接安装时，计算下载 ZIP 的摘要，并读取同一文件的清单 ID。若条目带有核验声明，请核对其记录所覆盖的平台、版本或发布者身份。将生成结果提交到 PR 分支后，可按需运行 `python3 scripts/catalog.py --check` 检查是否有过期输出。
