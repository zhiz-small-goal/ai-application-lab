import json
from pathlib import Path

from urllib.parse import urlparse, parse_qs

from collections import Counter


# 获取指定带 Airbus 的 RUL，以及它们的 hostname
airbus_urls = []
hostnames = []

with open(Path("./company_crawl.log"), "r") as file:
    for line in file:
        if "Saved Airbus" in line:
            url = line.split(" from ", 1)[1].strip()

            airbus_urls.append(url)

            parsed_url = urlparse(url)
            hostnames.append(parsed_url.hostname)


airbus_url_path = Path("hostname_counts.txt")


# print(len(hostnames))

# 统计每个域名数量分别是多少
hostname_counts = {}

for hostname in hostnames:
    if hostname not in hostname_counts:
        hostname_counts[hostname] = 1

    else:
        hostname_counts[hostname] += 1

# print(len(hostname_counts))
sort_hostname = sorted(hostname_counts.items(), key=lambda item: item[1], reverse=True)

hostname_list = []

for hostname in sort_hostname:
    hostname_list.append(str(hostname))

# print(type(hostname_list[0]))

airbus_url_path.write_text(
    "\n".join(hostname_list),
    encoding="utf-8"
)

# 获取 discover_from_url 匹配 response_url，表示重定向多少次
transition_counts = {}

airbus_provenance_dir = Path("comapny_provenance")
for provenance_path in airbus_provenance_dir.iterdir():
    if "Airbus" not in provenance_path.name:
        continue

    provenance = json.loads(
        provenance_path.read_text(encoding="utf-8")
    )

    discovered_from_url = provenance["discovered_from_url"]
    response_url = provenance["response_url"]

    transition = (
        discovered_from_url,
        response_url,
    )

    # Is not discovered from url with original page
    if discovered_from_url is None:
        parent_hostname = "START"
    else:
        parent_hostname = urlparse(
            discovered_from_url
        ).hostname

    child_hostname = urlparse(
        response_url
    ).hostname

    transition = (
        parent_hostname,
        child_hostname,
    )

    if transition not in transition_counts:
        transition_counts[transition] = 1
    else:
        transition_counts[transition] += 1

sorted_transitions = sorted(
    transition_counts.items(),
    key=lambda item: item[1],
    reverse=True,
)

# 把重定向次数保存到文件
transition_lines = []

for transition, count in sorted_transitions:
    parent_hostname, child_hostname = transition

    transition_lines.append(
        f"{parent_hostname} -> {child_hostname}: {count}"
    )

transition_path = Path("transition.txt")
transition_path.write_text(
    "\n".join(transition_lines),
    encoding="utf-8",
)

# 找出跑脚本前就存在的文件
saved_url_counts = Counter(airbus_urls)

provenance_url_counts = Counter()

for provenance_path in airbus_provenance_dir.iterdir():
    if "Airbus" not in provenance_path.name:
        continue

    provenance = json.loads(
        provenance_path.read_text(encoding="utf-8")
    )

    provenance_url_counts[
        provenance["response_url"]
    ] += 1

extra_provenance = (
    provenance_url_counts
    - saved_url_counts
)

# print(extra_provenance)

# 定位语言界面数量，分析出 www.ach.airbus.com 的域名扩展的原因是语言不同
# 语言获取相同的 node_id
language_counts = {}
node_languages = {}
path_languages = {}

target_hostname = "www.ach.airbus.com"

for url in airbus_urls:
    parsed_url = urlparse(url)

    if parsed_url.hostname != target_hostname:
        continue

    # print(parsed_url.path, parsed_url.query)

    parts = parsed_url.path.strip("/").split("/")

    if not parts or parts == [""]:
        continue

    language = parts[0]

    if language not in language_counts:
        language_counts[language] = 1
    else:
        language_counts[language] += 1

    if len(parts) >= 3 and parts[1] == "node":
        node_id = parts[2]

        if node_id not in node_languages:
            node_languages[node_id] = set()

        node_languages[node_id].add(language)

        continue

    
    normalized_path = "/" + "/".join(parts[1:])

    if normalized_path not in path_languages:
        path_languages[normalized_path] = set()

    path_languages[normalized_path].add(language)

# print(language_counts)
# print(len(node_languages))
# print(node_languages)

# print(len(path_languages))
# print(path_languages)


target_hostname = "www.aircraft.airbus.com"

# for url in airbus_urls:
#     parsed_url = urlparse(url)

#     if parsed_url.hostname != target_hostname:
#         continue

#     print(parsed_url.path, parsed_url.query)
# 根据 parsed_url.path/query 的输出结果，看到很
# 多 news 的path，查看哪个父域名延伸出多少条带 ”/en/newsroom/news/“子域名
parent_counts = {}

for provenance_path in airbus_provenance_dir.iterdir():
    if "Airbus" not in provenance_path.name:
        continue

    provenance = json.loads(
        provenance_path.read_text(encoding="utf-8")
    )

    response_url = provenance["response_url"]
    discovered_from_url = provenance["discovered_from_url"]

    parsed_response = urlparse(response_url)

    if parsed_response.hostname != target_hostname:
        continue

    if not parsed_response.path.startswith("/en/newsroom/news/"):
        continue

    if discovered_from_url is None:
        continue

    if discovered_from_url not in parent_counts:
        parent_counts[discovered_from_url] = 1
    else:
        parent_counts[discovered_from_url] += 1


sort_parent_counts = sorted(
    parent_counts.items(),
    key=lambda item: item[1],
    reverse=True,
)

# print(sort_parent_counts)

# 上一步输出发现 page=9、page=10 没出现，现在寻找
# page=8、9、10、11 各自成为多少个 provenance child 的 discovered_from_url

# page_child_counts = {}

# for provenance_path in airbus_provenance_dir.iterdir():
#     if "Airbus" not in provenance_path.name:
#         continue

#     provenance = json.loads(
#         provenance_path.read_text(encoding="utf-8")
#     )

#     discovered_from_url = provenance["discovered_from_url"]

#     if discovered_from_url is None:
#         continue

#     parsed_parent = urlparse(discovered_from_url)

#     if parsed_parent.hostname != "www.aircraft.airbus.com":
#         continue

#     if parsed_parent.path != "/en/newsroom/stories":
#         continue

#     query = parse_qs(parsed_parent.query)

#     if "page" not in query:
#         continue

#     page = query["page"][0]

#     if page not in {"8", "9", "10", "11"}:
#         continue

#     if discovered_from_url not in page_child_counts:
#         page_child_counts[discovered_from_url] = 1
#     else:
#         page_child_counts[discovered_from_url] += 1

# sort_page_child_counts = sorted(
#     page_child_counts.items(),
#     key=lambda item: item[1],
#     reverse=True,
# )

# print(sort_page_child_counts)

target_hostname = "www.airbus.com"

new_parent_counts = {}

for url in airbus_urls:
    parsed_url = urlparse(url)

    if parsed_url.hostname != target_hostname:
        continue

    # print(
    #     parsed_url.path,
    #     parsed_url.query,
    # )

for provenance_path in airbus_provenance_dir.iterdir():
    if "Airbus" not in provenance_path.name:
        continue

    provenance = json.loads(
        provenance_path.read_text(encoding="utf-8")
    )

    discovered_from_url = provenance["discovered_from_url"]

    if discovered_from_url is None:
        continue

    response_url = provenance["response_url"]

    parsed_response = urlparse(response_url)
    print(parsed_response.hostname, parsed_response.path)

    if parsed_response.hostname != "www.airbus.com":
        continue

    if not parsed_response.path.startswith("/en/newsroom/press-releases/"):
        continue

    if discovered_from_url not in new_parent_counts:
        new_parent_counts[discovered_from_url] = 1
    else:
        new_parent_counts[discovered_from_url] += 1

sort_new_parents = sorted(
    new_parent_counts.items(),
    key=lambda item: item[1],
    reverse=True,
)

# print(sort_new_parents)

target_parent = (
    "https://www.airbus.com/en/newsroom/press-releases"
    "?subsidiaries%5BCommercial%20Aircraft%5D=Commercial%20Aircraft"
    "&langcode%5Ben%5D=en"
    "&sort_bef_combine=search_api_relevance_DESC"
    "&page=23"
)

date_counts = {}

for provenance_path in airbus_provenance_dir.iterdir():
    if "Airbus" not in provenance_path.name:
        continue

    provenance = json.loads(
        provenance_path.read_text(encoding="utf-8")
    )

    if provenance["discovered_from_url"] != target_parent:
        continue

    response_url = provenance["response_url"]
    parsed_response = urlparse(response_url)

    prefix = "/en/newsroom/press-releases/"

    if not parsed_response.path.startswith(prefix):
        continue

    slug = parsed_response.path.removeprefix(prefix)

    date = slug[:7]

    if date not in date_counts:
        date_counts[date] = 1
    else:
        date_counts[date] += 1

print(date_counts)