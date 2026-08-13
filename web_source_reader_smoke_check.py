import httpx
from openai import OpenAI
import os

from web_source_reader import read_web_source
from evidence_extractor import extract_evidence, select_candidate_text
from company_screening import screen_company

from time import perf_counter


seeds = [
    {
        "company": "湖南银行股份有限公司",
        "source_url": (
            "https://www.hunan-bank.com/96599/2025-11/21/"
            "article_2025112118011847442.shtml?sessionid="
        ),
    },
    # {
    #     "company": "浙江农村商业联合银行股份有限公司",
    #     "source_url": (
    #         "https://www.zj96596.com/zj96596/2026-07/03/"
    #         "article_2026070316205561696.shtml"
    #     ),
    # },
    # {
    #     "company": "中国第一汽车集团有限公司",
    #     "source_url": (
    #         "https://www.aliyun.com/customer-stories/"
    #         "automotive-2025-faw"
    #     ),
    # },
]


SCREENING_RULES = """
你正在执行第一轮公司筛选。

目标：
根据当前提供的证据，判断这家公司是否值得继续投入下一轮调查成本。

规则：
- 只能使用提供的证据进行判断。
- 必须区分事实（facts）、推断（inferences）和未知信息（unknowns）。
- 不得把推断写成事实。
- 不得猜测证据没有支持的信息。
- 每一条推断都必须能够被一条或多条提供的证据合理支持。
- 不得在推断中自行加入证据未说明的公司背景、所有权属性、资源优势或其他外部事实。

- KEEP：已有足够正面证据，值得继续调查。
- UNCERTAIN：当前证据不足、冲突或关键情况未知。
- REJECT：必须存在具有实际意义的负面证据。
- 缺少正面证据本身不能作为 REJECT 的理由。

- 单个岗位的学历、经验、薪资或个人适配程度，不能直接用于淘汰整家公司。
- 单个招聘岗位本身也不自动支持 KEEP。
- 但如果招聘信息明确对应真实业务流程、具体 AI 职责、系统集成、模型部署或其他实际 AI 工作，
  可以将其视为公司存在明确 AI 能力投入或应用方向的正面证据，并据此支持 KEEP。
- 仅仅在岗位名称或职位描述中泛泛出现“AI”“大模型”“智能化”等词语，不足以单独支持 KEEP。

- 已有 AI 团队、软件研发能力或 AI 项目不能作为 REJECT 的理由。
- 已有真实 AI 项目可以支持继续调查，但不能自动推出存在个人可捕获机会。

- missing_evidence 应优先服务于下一轮机会调查，包括：
  尚未解决的业务流程、
  内部与外部 AI 能力边界、
  采购或供应商关系、
  新增 AI 项目、
  现实个人进入路径、
  可能的 PoC 机会。
- 除非与“是否值得继续调查”直接相关，否则不要默认转向通用投资尽调。

- 所有自然语言输出使用中文。
"""


extraction_rules = """
你正在为第一轮公司筛选提取 Evidence。

只提取与以下问题直接相关的事实：
- 公司正在进行的 AI / 大模型 /数字化项目或采购；
- AI 进入了什么业务流程
- 公司为 AI / 数字化投入了什么资源和预算；
- 项目产生了什么可观察或可量化结果；
- 招聘、采购、供应商或系统集成信息中，能够反映 AI 能力投入或供给结构的事实。

忽略与上述判断无直接关系的行政或程序性信息，例如：
- 投标人一般资格条件；
- 报名方式；
- 开标地点；
- 保证金；
- 联系方式；
- 银行账户；
- 招标文件售价；

supporting_text 必须是 raw_text 中连续、逐字存在的原文片段。

禁止：
- 使用“...”或“…”连接多个不连续原文片段；
- 删除中间内容后把多个片段拼成一个 supporting_text；
- 对 supporting_text 进行改写、总结或重组

如果一个 evidence_text 需要多个不连续原文片段才能支持，
必须拆成多个独立的 EvidenceCandidate。

一条 EvidenceCandidate 应优先表达一个能够由单个连续原文片段直接支持的事实。

Evidence 必须由原文直接支持。
不得把推断写成事实。
优先保留少量、互不重复、高信息价值的 Evidence。
"""


model = "deepseek-v4-flash"


llm_client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)




with httpx.Client() as client:
    for seed in seeds:
        start_time = perf_counter()

        print(f"\nCompany: {seed["company"]}")

        print("Start get web source text...")
        raw_text = read_web_source(
            url=seed["source_url"],
            client=client,
        )

        print("get web soruce text end...")
        read_web_time = perf_counter() - start_time
        print("read_web_time: ", read_web_time)


        print("\n\nstart select candidate text...")
        candidate_text = select_candidate_text(
            raw_text=raw_text,
        )
        print("\n select candidate text end.")
        print("\nselect candidate text: ", candidate_text)
        select_text_time = perf_counter() - read_web_time
        print("\n select candidate time: ", select_text_time)


        print("\n\nStart extraction evidence...")
        extraction_result = extract_evidence(
            raw_text=raw_text,
            extraction_rules=extraction_rules,
            client=llm_client,
            model=model,
            llm_input_text=candidate_text,
        )


        print("Start screening company...\n")
        evidence = [
            item.evidence_text
            for item in extraction_result.evidence
        ]
        screening_result = screen_company(
            company=seed["company"],
            evidence=evidence,
            screening_rules=SCREENING_RULES,
            client=llm_client,
            model=model,
        )

        screen_company_elapsed_time = perf_counter() - select_text_time

        print(f"Evidence extraction: {screen_company_elapsed_time}s")
        print(f"公司筛选结果是：\n\n{screening_result}\n\n")
        

print("End")


