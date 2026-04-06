import json
import os

import jieba
import joblib
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from .view_support import JsonResponse, get_graph, render, settings


# 【必须与最新的 HeavyTextCNN 结构保持完全一致】
class HeavyTextCNN(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_classes):
        super(HeavyTextCNN, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        num_filters = 256
        self.conv1 = nn.Conv2d(1, num_filters, (2, embed_dim))
        self.conv2 = nn.Conv2d(1, num_filters, (3, embed_dim))
        self.conv3 = nn.Conv2d(1, num_filters, (4, embed_dim))
        self.conv4 = nn.Conv2d(1, num_filters, (5, embed_dim))
        self.dropout = nn.Dropout(0.6)
        self.fc1 = nn.Linear(1024, 512)
        self.fc2 = nn.Linear(512, num_classes)

    def forward(self, x):
        x = self.embedding(x).unsqueeze(1)
        x1 = F.max_pool1d(F.relu(self.conv1(x)).squeeze(3), x.size(2) - 1).squeeze(2)
        x2 = F.max_pool1d(F.relu(self.conv2(x)).squeeze(3), x.size(2) - 2).squeeze(2)
        x3 = F.max_pool1d(F.relu(self.conv3(x)).squeeze(3), x.size(2) - 3).squeeze(2)
        x4 = F.max_pool1d(F.relu(self.conv4(x)).squeeze(3), x.size(2) - 4).squeeze(2)
        x = self.dropout(torch.cat((x1, x2, x3, x4), 1))
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        out = self.fc2(x)
        return out


def _deprecated_textcnn_smart_diagnosis(request):
    if request.method == 'GET':
        return render(request, 'wenda/smart_diagnosis.html')

    elif request.method == 'POST':
        import json
        data = json.loads(request.body)
        user_text = data.get('text', '').strip()

        if not user_text:
            return JsonResponse({'status': 'error', 'msg': '请输入您的症状描述'})

        try:
            vocab = joblib.load(os.path.join(settings.BASE_DIR, 'text_vocab.pkl'))
            label_dict = joblib.load(os.path.join(settings.BASE_DIR, 'text_labels.pkl'))
            idx2label = {v: k for k, v in label_dict.items()}

            # 保持和训练一致的停用词过滤
            stop_words = set(
                ["的", "了", "呢", "啊", "怎么", "请问", "医生", "大夫", "患者", "感觉", "最近", "一直", "是什么",
                 "怎么办", "谢谢"])
            words = [w for w in jieba.cut(user_text) if w not in stop_words and len(w.strip()) > 0]

            seq = [vocab.get(w, vocab['<UNK>']) for w in words]
            MAX_LEN = 100
            if len(seq) < MAX_LEN:
                seq += [vocab['<PAD>']] * (MAX_LEN - len(seq))
            else:
                seq = seq[:MAX_LEN]

            input_tensor = torch.tensor([seq], dtype=torch.long)

            VOCAB_SIZE = len(vocab)
            EMBED_DIM = 200
            NUM_CLASSES = len(label_dict)

            model = HeavyTextCNN(VOCAB_SIZE, EMBED_DIM, NUM_CLASSES)
            model.load_state_dict(torch.load(os.path.join(settings.BASE_DIR, 'textcnn_model.pth')))
            model.eval()

            with torch.no_grad():
                outputs = model(input_tensor)

                # 【终极锐化大招】：使用极小的温度系数 (比如 0.1)
                # 这会强制剥夺其他低分候选者的概率，让最高分的疾病暴增到 80%~99%
                temperature = 0.1
                scaled_outputs = outputs / temperature
                probabilities = F.softmax(scaled_outputs, dim=1).squeeze().numpy()

            top3_idx = np.argsort(probabilities)[-3:][::-1]
            results = []

            graph = get_graph()
            for idx in top3_idx:
                disease_name = idx2label[idx]
                prob_val = probabilities[idx]

                drug_query = """
                MATCH (d:disease {name: $disease_name})-[:disease_drug]->(drug:drug)
                RETURN drug.name as d_name
                LIMIT 3
                """
                drug_records = graph.run(drug_query, disease_name=disease_name).data()

                drugs_list = [r['d_name'] for r in drug_records] if drug_records else []
                drug_str = "、".join(drugs_list) if drugs_list else "暂无关联药物，请遵循医嘱"

                results.append({
                    'disease': disease_name,
                    # 如果概率由于温度锐化接近 1.0，展示为 99.9%
                    'probability': round(float(prob_val) * 100, 2),
                    'drugs': drug_str
                })

            return JsonResponse({'status': 'success', 'data': results})

        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': f"模型推理异常: {str(e)}"})


def _lookup_diagnosis_drugs(disease_name):
    try:
        graph = get_graph()
        query = """
        MATCH (d:disease {name: $disease_name})-[:disease_drug]->(drug:drug)
        RETURN drug.name as drug_name
        LIMIT 3
        """
        records = graph.run(query, disease_name=disease_name).data()
        drugs = [record['drug_name'] for record in records if record.get('drug_name')]
        if drugs:
            return '、'.join(drugs)
    except Exception:
        pass
    return '暂无关联用药建议，请结合医生意见进一步判断'


def smart_diagnosis(request):
    if request.method == 'GET':
        return render(request, 'wenda/smart_diagnosis.html')

    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'msg': '仅支持 POST 请求'})

    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'msg': '请求体不是合法的 JSON'})

    user_text = data.get('text', '').strip()
    if not user_text:
        return JsonResponse({'status': 'error', 'msg': '请输入症状描述'})

    try:
        from diagnosis.service import load_diagnosis_service

        service = load_diagnosis_service()
        prediction = service.predict(user_text, top_k=3)

        results = []
        for item in prediction['predictions']:
            results.append({
                'disease': item['disease'],
                'probability': item['probability'],
                'drugs': _lookup_diagnosis_drugs(item['disease']),
            })

        return JsonResponse({
            'status': 'success',
            'data': results,
            'matched_symptoms': prediction['matched_symptoms'],
        })
    except FileNotFoundError:
        return JsonResponse({
            'status': 'error',
            'msg': '诊断模型文件不存在，请先运行 train_symptom_diagnosis.py 训练模型。',
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'msg': f'诊断推理异常: {str(e)}'})
