import os

from openai import OpenAI

from openai_summarizer import summarize_with_openai
from text_analysis import summarize_text_file
from company_screening import screen_company
from evidence_extractor import extract_evidence

from pathlib import Path


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


company = "江苏省电子口岸有限公司"


raw_text = """
  江苏省电子口岸有限公司针对人工制单成本高、效率低、合规风险大等痛点，依托AI大模型技术，打造报关单AI智能制单与智能通关大模型平台。平台具有数据闭环驱动，无缝对接标准，权威安全保障三大优势，实现从“手动录入”到“AI秒级生成”跨越，制单效率提升4-5倍，单日制单量提升5-10倍，为我省外贸企业便利化通关提供专业助力。
"""


extraction_rules = """
You extract grounded evidence from the provided raw source text.

Rules:
- Use only information directly supported by raw_text.
- evidence_text must describe a concise factual claim directly supported by raw_text.
- Do not add assumptions, explanations, conclusions, or external knowledge.
- supporting_text must be copied directly from raw_text.
- Do not rewrite or paraphrase supporting_text.
- If raw_text does not support a claim, do not generate it.
"""


model = "deepseek-v4-flash"


client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)


def deepseek_summarizer(text: str) -> str:
    return summarize_with_openai(
        text=text,
        client=client,
        model="deepseek-v4-flash",
    )


print("Extracting evidence...")
extraction_result = extract_evidence(
    raw_text=raw_text,
    extraction_rules=extraction_rules,
    client=client,
    model="deepseek-v4-flash",
)
print("Evidence extraction complete.")

evidence = [
    item.evidence_text
    for item in extraction_result.evidence
]

print("Screening company...")
screening_result = screen_company(
    company=company,
    evidence=evidence,
    screening_rules=SCREENING_RULES,
    client=client,
    model=model,
)
print("Company screening complete.")


print(extraction_result)
print(f"\n\n\n{screening_result}")


