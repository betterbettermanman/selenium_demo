import requests

"""
{"id": "018a4062-998e-740f-a149-20c5165a8c4d", "name": "习近平总书记关于全面深化改革的重要论述", "teacher": "李鹏", "status": "0"}, {"id": "018b65ed-ca80-76cf-b6e0-0fc8035fe69b", "name": "习近平总书记关于国有企业改革发展和党的建设重要论述", "teacher": "杜国功", "status": "0"}, {"id": "018a4062-5d02-76f8-829e-31d55a8ce867", "name": "习近平总书记关于社会建设的重要论述", "teacher": "王道勇", "status": "0"}
"""

targets = {
    # "习近平外交思想": "高祖贵",
    # "习近平新时代中国特色社会主义经济思想": "谢鲁江",
    # "习近平法治思想": "杨伟东",
    # "习近平总书记关于科技创新的重要论述": "刘东超",
    # "习近平文化思想": "高志前",
    # "习近平总书记关于公共安全与应急管理重要论述": "曹海峰",
    "习近平总书记关于全面深化改革的重要论述": "李鹏",
    "习近平总书记关于国有企业改革发展和党的建设重要论述": "杜国功",
    "习近平总书记关于社会建设的重要论述": "王道勇",
}


def method(results, courseName, speaker):
    # courseName = "习近平新时代中国特色社会主义经济思想"
    # speaker = "谢鲁江"
    url = f"https://api.scgb.gov.cn/api/services/app/course/site/getCoursePublicPage?maxResultCount=24&skipCount=0&pageIndex=1&filterString={courseName}&contentId=&orderByType=&tagName=&year="
    headers = {
        "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJPcmdhbklkIjoiMDE5ODMxMDAtZGI1NS03N2VjLTgxMjgtODk3MWIzOGNmNzljIiwiQ2xpZW50VHlwZSI6IiIsIk9yZ2FuTmFtZSI6IuiLj-WNl-Wwj-WtpiIsIkFzc2Vzc1R5cGUiOjAsIlVzZXJJZCI6IjAxOTgzZmExLTRkZmEtNzcwNC05NTM2LTRmYWRkNmU1ZTE4MCIsIk9yZ2FuUGF0aCI6IjJjNTUxYTczLTViNDEtMTFlZC05NTFhLTBjOWQ5MjY1MDRmMyxjMWJmNjBjNS01YjQxLTExZWQtOTUxYS0wYzlkOTI2NTA0ZjMsMDE4YTQ1YmMtZWVmNi03NzFmLTkzZGEtMzU2NDIyYzRkNTAyLGNkNGFlNWI0LTQxOTctNGUzNC1iNGVmLWNiMmVkNzg4YzNmYiwwMThjYWFhMy1lZDMzLTdkNDAtYmFhMy1iZjRlYTU3NzQ2ZTAsMDE5ODI2NDAtY2Y0YS03ZmQ1LWFiNDMtNzk4M2VmMDJiNmYwLDAxOTgzMTAwLWRiNTUtNzdlYy04MTI4LTg5NzFiMzhjZjc5YyIsImV4cCI6MTc1NjMwMDU2MSwidXNlcm5hbWUiOiJiMmQyZGQ2OGZhMTljNTIxIn0.a9sUdegssdLyec4gpK05WsXy3yRXngFKVEoqj7FiajE"
    }
    response = requests.get(url, headers=headers)
    # print(response.json()['result']['records'])
    records = response.json()['result']['records']
    for record in records:
        if record['speaker'] == speaker:
            results.append({
                "id": record['id'],
                "name": record['name'],
                "teacher": speaker,
                "status": "0"
            })

    # print(results)


results = []
for key, value in targets.items():
    method(results, key, value)
print(results)

"""
{'id': '018b07db-49f7-7008-9efb-9f14d2575e79', 'name': '习近平外交思想（二）', 'teacher': '高祖贵', 'status': '0'}, {'id': '018b07db-49f7-7008-9ef8-d957a62e59d3', 'name': '习近平外交思想（四）', 'teacher': '高祖贵', 'status': '0'}, {'id': '018b07db-49f7-7008-9ef5-ab175f8d2d79', 'name': '习近平外交思想（三）', 'teacher': '高祖贵', 'status': '0'}, {'id': '018b07db-49f7-7008-9ef2-0aff50a2fc38', 'name': '习近平外交思想（一）', 'teacher': '高祖贵', 'status': '0'}

"""
