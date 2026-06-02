# 测试用例 DeepSeek 优化工具

本仓库提供基于 DeepSeek API 的 Word 测试用例处理脚本。

## 环境准备

```bash
pip install -r requirements.txt
export DEEPSEEK_API_KEY="sk-xxxx"
```

## optimize_test_cases.py（推荐）

结合《需求规格.docx》中对应功能模块的“处理流程”，站在**系统测试**角度重写
《系统测试用例.docx》中每个用例的“操作过程及数据”“预期结果”“实际结果”。

特性（与需求一一对应）：

1. 仅重写每一步的三列内容，不修改用例标题/编号/描述/前置条件/模块名称/测试类型等标识信息；
2. 站在系统测试角度编写步骤与观察结果，拉通各配置项/硬件设备体现端到端功能；
3. 不修改备注、测试结论、测试人员、日期等其它任何内容；
4. 不改变表格结构与样式（步骤行数量不变，保留单元格段落/run 格式）；
5. 大模型角色设定为资深测试专家；
6. 每个用例都将其对应功能模块的完整需求（功能描述/处理流程/性能需求/异常处理）作为依据；
7. 每个用例步骤数与原用例一致且不超过 8 步。

用法：

```bash
# 默认读取 系统测试用例.docx 与 需求规格.docx，另存为 系统测试用例_优化.docx
python3 optimize_test_cases.py

# 自定义输入/输出
python3 optimize_test_cases.py --cases 系统测试用例.docx --spec 需求规格.docx -o 系统测试用例_优化.docx

# 仅解析并打印用例与提示词，不调用 API、不写文件
python3 optimize_test_cases.py --dry-run
```

脚本会按用例所属“模块名称”中的编码（如 `SRS_XHMN_XHCJ_MNXHCJ`）自动匹配需求规格中的功能模块。

## fill_actual_results.py

仅依据每一步的“操作过程及数据”和“预期结果”重写“实际结果”列。

```bash
python3 fill_actual_results.py A.docx -o A_filled.docx
python3 fill_actual_results.py A.docx --dry-run
```
