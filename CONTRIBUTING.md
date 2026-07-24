# 枝枝AI学习仓库

## 仓库用途
1，展现枝枝个人成长
2，方便后续复习整理

## Git 提交信息规范（Conventional Commits + Angular）

- 采用格式：
   <type>(<scope>): <subject>
   [空行]
   [可选 body]
   [空行]
   [可选 footer]

- 解析：
  - type：本次提交的类别，必须填写
  - scope：受影响的模块/范围，可选
  - subject：一句话描述「做了什么」，使用祈使语气英文动词（add/fix/refactor/...）
  - body：补充「为什么这么做」、「重要细节」
  - footer：BREAKING CHANGE、关联Issue（如Close #12）


- 常用 type：
  - `feat`           新增功能或重要内容
  - `fix`            修复错误（包括文档、示例中的错误）
  - `docs`           仅修改文档（Markdown、注释）
  - `refactor`       重构示例代码，不改变行为
  - `chore`          其他与学习内容无关的杂项
  - `test`           补充/修改测试
  - `style`          代码风格/格式调整（不影响逻辑）
  - `build`          构建系统或依赖项调整（Cmake、工具链）
  - `ci`             CI/CD 配置变更
  - `perf`           性能优化
  - `revert`         回滚某次提交

- 可选扩展类型（按需启用）：

`deps`               依赖升级/降级（也可归入 build/chore）
`security`           安全相关变更
`i18n`               国际化/本地化变更
`release`            发布相关（如自动生成的发版提交）
`wip`                work in progress，仅用于本地临时提交，不建议推送

- scope 示例：
  - `heap`           堆、存储期相关内容
  - `pointer`        指针与智能指针
  - `build`          构建相关
  - `core`           核心C++代码（主要练习代码）
  - `vscode`         VSCode配置（.vscode目录的文件）
  - `git`            Git相关（.gitignore、钩子等）
  - `docs`           文档与学习日志
  - `tests`          测试代码
  - `ci`             持续集成配置
  - `examples`       示例或演示代码

- 示例：
  - `docs(heap): 修正存储期的定义，贴近标准术语`
  - `fix(example): 修复 double delete 示例中的错误`
  - `feat(pointer): 增加 shared_ptr/unique_ptr 对比示例`
  - `feat(core): add Student struct and GPA calculation`
  - `fix(console): handle UTF-8 output for Chinese text`
  - `refactor(main): extract menu loop to run_menu()`
  - `docs(docs): add learning log for 2025-12-05`
  - `chore(script): rename learning log script to zhiz-learning-log`
  - `chore(git): ignore generated exe binaries`


## 贡献流程

1. 发现问题或想补充内容
   - 优先检查 notes/ 中是否已有相关小节，避免重复。
   - 如是修正定义，优先修改“权威定义”所在位置。

2. 修改与自测
   - 对文档：检查术语一致性、链接是否正确。
   - 对代码：确保示例可以在 README 指定环境中编译运行。

3. 提交
   - 使用约定的 commit 信息格式（见上文）。
   - 每个 commit 尽量聚焦一个主题（例如“修正文档定义”“补充示例”分成两个提交）。

4. （可选）Pull Request
   - 若未来对外开放贡献：在此说明 PR 模板、评审预期等。
