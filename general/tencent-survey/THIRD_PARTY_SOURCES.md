# Third-party sources and attribution for `tencent-survey`

This file is generated during public packaging to keep upstream references visible. Verify upstream licenses before redistributing modified scripts or templates.

## Source/license lines found in the skill files

- `├── references/           # 工具参考文档`
- `│   ├── get_survey.md     # get_survey 工具参考`
- `│   ├── create_survey.md  # create_survey 工具参考`
- `│   ├── update_question.md# update_question 工具参考`
- `│   └── list_answers.md   # list_answers 工具参考`
- `| 工具 | 说明 | 参考文档 |`
- `homepage: https://wj.qq.com`
- `| 工具名称 | 功能说明 | 参考文档 |`
- `> 参考文档中的参数说明应与 MCP 工具 Schema 保持一致。如有冲突，以 `mcporter list tencent-survey` 返回的 Schema 为准。`
- `参考文档：`references/get_survey.md``
- `参考文档：`references/create_survey.md``
- `3. 按问卷文本语法组织 `text` 内容（语法详见参考文档）`
- `参考文档：`references/update_question.md``
- `4. 参考返回的 `text` 字段了解当前问卷的 DSL 格式`
- `参考文档：`references/update_logic.md``
- `参考文档：`references/list_answers.md``
- `- **text 字段（DSL 格式）**：`get_survey` 返回的 `text` 字段是纯文本 DSL 格式的问卷内容，可作为 `update_question` 的参考`
- `- **survey_dsl 字段**：`get_survey` 返回的 `survey_dsl` 包含当前自定义逻辑代码（`code`）和错误信息（`errors`），作为 `update_logic` 的参考`
- `3. **阅读参考文档**：`references/` 目录下包含所有工具的参数说明`
- `# create_survey 工具参考`
- `> 📖 语法详细参考：`
- `| `invalid_text_format` | 文本内容格式错误 | 检查 text 语法是否正确，参考上方语法说明 |`
- `# get_survey 工具参考`
- `| `text` | string | 纯文本格式的问卷内容（DSL 格式），包含标题、引导语和所有题目。可直接用于 `update_question` 等工具的参考 |`
- `| `survey_dsl.code` | string | 当前自定义逻辑代码（DSL 脚本），可作为 `update_logic` 的参考。为空字符串时表示未设置逻辑 |`
- `5. **text 字段**：返回纯文本 DSL 格式的问卷内容，包含标题和所有题目。该字段可作为 `update_question` 工具的参考，了解当前问卷的文本结构`
- `6. **survey_dsl 字段**：返回当前问卷的自定义逻辑代码（`code`）和错误信息（`errors`）。`code` 可作为 `update_logic` 工具的参考，了解当前已设置的逻辑规则。追加逻辑时需在原有 `code` 基础上修改`
- `# list_answers 工具参考`
- `# update_logic 工具参考`
- `| **内容替换** | `replace "<文本>" in <题目> title with <来源>` | 将题目标题中的指定文本替换为另一题的回答 |`
- `| **自动填充** | `set <题目> = <来源>` | 自动填充文本题内容 |`
- `| `invalid_dsl_syntax` | DSL 语法错误 | 检查 DSL 代码语法是否正确，参考语法文档 |`
- `# update_question 工具参考`
- `> 完整语法参考：`references/create_survey.md` 中的「text 文本语法详解」章节。`
