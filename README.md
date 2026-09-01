# 信息处理系统 v0.1

## 1.项目目前解决什么问题？
- 目前主要功能是：尽可能去掉网页内容中跟判断目标无关的上下文，同时尽可能保留完成判断所需要的关键 Evidence。

## 2.我是如何实现这个功能的？
- 第一步对原始网页内容进行 Trafilatura 处理，提取网页主要正文，并尽量去除导航、页脚、模板等无关内容；
- 第二步将处理后的网页正文进行 Chunk 切分，并结合 Query 使用 Reranker 对 Chunk 进行相关性排序，得到 Top_K 高相关内容。
- 第三步通过 Evaluation 对处理后的结果进行比较，检查 Parser 是否保留关键 Evidence，以及减少网页文本后是否明显影响 Retrieval 找回关键 Evidence 的能力。
- 当前主要使用 Evidence Preservation、Recall@K 和 Compression Ratio 作为评估指标。

## 3.我是如何验证方案的可靠性的？
- 第一步选取 7 个样本覆盖以下边界：
  - 局部集中 Evidence
  - 高 Evidence 密度
  - 跨主题、分散 Evidence
  - 结构化采购内容
  - 高模板噪声
  - 首尾远距离 Evidence
  - 非正文结构 Evidence（title / list / table / aside 等）
- 第二步 BeautifulSoup baseline -> Reference_text, Trafilatura candidate parser -> parser_text.
BeautifulSoup 作为对照基线，Trafilatura 作为候选方案与之对比。
- 第三步输出 Evaluation 结果为 CSV 表格。
- 第四步比较两种 html 的处理方案，判断是：相同变量下，Trafilatura 能减少更多文本量，并在大多数样本中保留关键 Evidence；对于 Parser 成功保留下来的 Evidence，它的 Top_K Retrieval 表现与 Reference baseline 基本接近。
- 第五步对比后选 Trafilatura 方案，但是发现该方案会导致 <aside> 中的 Evidence 丢失。
- 第六步让 GPT 设计 4 个隔离变量测试，并查阅 Trafilatura 官方源码/实现规则。
- 第七步得出结论：Trafilatura 默认删除 <aside>。
- 第八步再检查少量真实网页，并没有发现关键 Evidence 落入 <aside>.
- 现在 Trafilatura 的文本压缩收益高，并且测试中暂时没有发现大量关键 Evidence 落入 <aside>, 所以暂时接受 Trafilatura 默认删除 <aside>.

## 4.项目边界与已知缺陷。
- 目前 Trafilatura 默认删除 <aside>.
- 当前 Chunk 的算法是 固定长度 + 200 字符 overlap，还没跟其他 Chunking 策略比较过。
- 目前主要是处理网页数据。
- 现在的 parser_recall 只针对 Parser 成功保留的 Evidence 进行计算，所以不能单独反映 Parser 删除 Evidence 带来的端到端损失，因为看不见已经删掉的 Evidence。

## 5.如何运行
### 5.1 环境
- 当前项目主要使用 Python 运行。
建议首先创建虚拟环境：
```
py -m venv .venv
.venv\Scripts\activate
```

安装项目依赖：`pip install -r requirements.txt`

- 项目使用 `BAAI/bge-reranker-v2-m3` 作为当前 Reranker。首次运行时，FlagEmbedding 会下载对应模型，因此需要能够访问模型下载源。

### 5.2 Evaluation 输入
- 主要 Evaluation 使用两类输入：
`evaluation_samples/ Frozen HTML 样本`
`evaluation_data/ parser_evaluation_expected_evidence_v0.1.json`

- JSON Dataset 中保存 Query、Sample 信息以及 Expected Evidence。
- Expected Evidence 的位置不直接写死在 Dataset 中，而是在运行 Evaluation 时根据 reference_text 自动定位。

### 5.3 运行测试
- 在项目根目录执行：`python -m pytest -q`
- 当前主要自动化测试覆盖：
  - Chunk 切分及 overlap 行为；
  - Chunk 对 Evidence 的覆盖判断；
  - Recall 计算；
  - Reference Evidence 到 Parser Text 的位置映射；
  - Parser 删除 Evidence 时的 Mapping Failure；
  - 空白字符差异下的 Evidence Mapping。

### 5.4 运行 Evaluation
- 在项目根目录执行：`python run_evaluation.py`
- 运行流程：
Frozen HTML
-> BeautifulSoup Reference Text
-> Trafilatura Parser Text
-> Expected Evidence Mapping
-> Chunking
-> Query + Chunk
-> Reranker
-> Top-K
-> Evaluation

- 当前 Evaluation 主要输出：
  - `expected_evidence_count`
  - `parser_preserved_evidence_count`
  - `reference_recall`
  - `parser_recall`
  - `parser_compression_ratio`

- Evaluation 完成后结果写入：`results/evaluation_results.csv`
- 当前主要通过 Evidence Preservation、Recall@K和 Compression Ratio 判断 Parser 是否在减少网页文本的同时保留完成判断所需要的关键 Evidence。