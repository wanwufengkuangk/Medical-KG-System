import json
import requests

from .view_support import HttpResponse, JsonResponse, get_graph, is_ajax, render


RELATION_LABELS = {
    'disease_symptom': '症状',
    'disease_drug': '药物',
    'dept_contain_disease': '科室',
    'disease_check': '检查',
}

def analysis_view(request):
    """大屏可视化分析展示视图"""
    context = {
        'entity_counts': "{}",
        'dept_names': "[]",
        'dept_values': "[]",
        'macro_nodes': "[]",
        'macro_links': "[]",
        'quality_data': "{}"  # 新增这一行
    }

    try:
        graph = get_graph()
        # 1. 统计四大核心指标 (使用你图中的真实标签)
        d_count = graph.run("MATCH (n:disease) RETURN count(n)").evaluate() or 0
        s_count = graph.run("MATCH (n:symptom) RETURN count(n)").evaluate() or 0
        dr_count = graph.run("MATCH (n:drug) RETURN count(n)").evaluate() or 0
        r_count = graph.run("MATCH ()-[r]->() RETURN count(r)").evaluate() or 0

        context['entity_counts'] = json.dumps({
            'disease': d_count, 'symptom': s_count,
            'drug': dr_count, 'relation': r_count
        })

        # 2. 统计科室包含的疾病数量 TOP 8 (使用你图中的 dept_contain_disease 关系)
        dept_query = """
        MATCH (n)-[r:dept_contain_disease]->(d:disease)
        RETURN n.name as dept, count(d) as num
        ORDER BY num DESC LIMIT 8
        """
        dept_res = graph.run(dept_query).data()
        if dept_res:
            context['dept_names'] = json.dumps([x['dept'] for x in dept_res])
            context['dept_values'] = json.dumps([x['num'] for x in dept_res])

        # 3. 抽取全局图谱关系网 (限制 60 条，防止前端卡死)
        # 抽取疾病与症状、药物的关系
        macro_query = """
        MATCH (s:disease)-[r]->(t)
        WHERE type(r) IN ['disease_symptom', 'disease_drug']
        RETURN s.name as source, t.name as target, type(r) as rel_type
        LIMIT 60
        """
        macro_res = graph.run(macro_query).data()

        # 新增2
        # ---------- 新增：4. 知识图谱质量评估 ----------
        # 1. 关系完整性：有多少疾病包含了“症状”信息？
        total_disease = d_count if d_count > 0 else 1  # 避免除0报错
        has_sym_disease = graph.run("MATCH (d:disease)-[:disease_symptom]->() RETURN count(DISTINCT d)").evaluate() or 0
        completeness_rate = round((has_sym_disease / total_disease) * 100, 1)

        # 2. 孤立节点检测：没有任何关系边连接的“废弃”节点
        isolated_nodes = graph.run("MATCH (n) WHERE NOT (n)--() RETURN count(n)").evaluate() or 0

        # 3. 属性一致性/完整性：缺失“简介(brief)”的核心疾病数量
        missing_brief = graph.run(
            "MATCH (d:disease) WHERE d.brief IS NULL OR d.brief = '' RETURN count(d)").evaluate() or 0

        # 打包传给前端
        context['quality_data'] = json.dumps({
            'completeness': completeness_rate,
            'isolated': isolated_nodes,
            'missing_brief': missing_brief
        })
        # -----------------------------------------------
        nodes_set = set()
        links = []
        for record in macro_res:
            nodes_set.add(record['source'])
            nodes_set.add(record['target'])
            # 翻译一下英文关系，让大屏显示中文
            rel_name = "症状" if record['rel_type'] == "disease_symptom" else "药物"
            links.append({
                'source': record['source'],
                'target': record['target'],
                'type': rel_name
            })

        # 根据名字长度简单区分一下节点大小，让图谱有层次感
        nodes = [{'name': n, 'symbolSize': 35 if len(n) <= 4 else 20} for n in nodes_set]

        context['macro_nodes'] = json.dumps(nodes, ensure_ascii=False)
        context['macro_links'] = json.dumps(links, ensure_ascii=False)

    except Exception as e:
        print(f"大屏数据查询出错 (不影响页面打开): {e}")

    return render(request, 'wenda/analysis.html', context)


def analysis_graph_search(request):
    """大屏图谱的实时搜索接口"""
    keyword = request.GET.get('keyword', '').strip()

    # 默认返回空结构
    nodes = []
    links = []

    if keyword:
        try:
            graph = get_graph()
            # Cypher查询：查找名字包含关键词的节点，并找出它们的一度关系
            # 使用参数化查询，避免把用户输入直接拼进 Cypher。
            query = """
            MATCH (n)-[r]-(m)
            WHERE n.name CONTAINS $keyword
            RETURN n.name as source, m.name as target, type(r) as rel_type, labels(n) as n_labels, labels(m) as m_labels
            LIMIT 50
            """
            result = graph.run(query, keyword=keyword).data()

            nodes_set = set()
            for row in result:
                nodes_set.add(row['source'])
                nodes_set.add(row['target'])

                rel_name = RELATION_LABELS.get(row['rel_type'], row['rel_type'])

                links.append({
                    'source': row['source'],
                    'target': row['target'],
                    'type': rel_name
                })

            # 构造节点，稍微区分一下大小
            for n in nodes_set:
                # 如果节点名字就是搜索词，把它变大一点作为中心
                is_center = (n == keyword)
                nodes.append({
                    'name': n,
                    'symbolSize': 50 if is_center else 30,
                    'itemStyle': {'color': '#ff4d4f' if is_center else None}  # 中心节点标红
                })

        except Exception as e:
            print(f"图谱搜索报错: {e}")

    return JsonResponse({'nodes': nodes, 'links': links})


# 新增4
def deepseek_ask(request):
    """
    DeepSeek 智能问答接口
    """
    if is_ajax(request) or request.method == 'GET':  # 兼容 GET 请求方便测试
        user_question = request.GET.get('question', '').strip()

        if not user_question:
            return HttpResponse(json.dumps({'answer': "请先输入您的问题。"}, ensure_ascii=False),
                                content_type='application/json')

        try:
            system_prompt = """
            你是一名专业的全科医生助手。你的任务是基于用户的描述提供医疗建议。
            请注意：
            1. 回答要温柔、专业、条理清晰。
            2. 如果涉及具体用药，请提醒用户“遵医嘱”。
            3. 回答长度控制在300字以内，不要长篇大论。
            """

            response = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers={
                    "Authorization": "Bearer sk-a704deae10844d958d0aaa34904a97df",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_question},
                    ],
                    "stream": False,
                },
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()

            choices = payload.get("choices") or []
            ai_answer = ""
            if choices:
                ai_answer = (choices[0].get("message") or {}).get("content", "").strip()
            if not ai_answer:
                ai_answer = "抱歉，AI医生暂时没有生成有效回复，请稍后再试。"

            return HttpResponse(json.dumps({'answer': ai_answer}, ensure_ascii=False), content_type='application/json')

        except Exception as e:
            print(f"DeepSeek 调用报错: {e}")
            return HttpResponse(json.dumps({'answer': "抱歉，AI医生暂时掉线了，请稍后再试。"}, ensure_ascii=False),
                                content_type='application/json')

    else:
        return render(request, 'wenda/404.html')
