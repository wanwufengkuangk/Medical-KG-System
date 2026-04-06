import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from django.test import RequestFactory, SimpleTestCase


PROJECT_DIR = Path(__file__).resolve().parents[1]
project_dir_str = str(PROJECT_DIR)
if project_dir_str not in sys.path:
    sys.path.append(project_dir_str)

from diagnosis.pipeline import LexiconMatcher, augment_with_symptoms, normalize_question_text
from wenda import views_analysis, views_diagnosis


class DiagnosisPipelineTests(unittest.TestCase):
    def test_lexicon_matcher_prefers_longer_terms(self):
        matcher = LexiconMatcher(["头痛", "偏头痛", "腹痛"])
        matches = matcher.extract_matches("最近偏头痛还伴随腹痛")
        self.assertEqual(matches[0], "偏头痛")
        self.assertIn("头痛", matches)
        self.assertIn("腹痛", matches)

    def test_normalize_question_text_cleans_whitespace_and_numbers(self):
        normalized = normalize_question_text(" 发热39.5度\n咳嗽3天 ")
        self.assertEqual(normalized, "发热0度 咳嗽0天")

    def test_augment_with_symptoms_appends_matched_terms(self):
        matcher = LexiconMatcher(["发热", "咳嗽", "胸闷"])
        model_text, matched = augment_with_symptoms("发热 咳嗽", matcher, max_hints=2)
        self.assertEqual(matched, ["发热", "咳嗽"])
        self.assertIn("发热", model_text)
        self.assertIn("咳嗽", model_text)


class AnalysisViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("wenda.views_analysis.get_graph")
    def test_analysis_graph_search_uses_parameterized_query_and_translates_links(self, mock_get_graph):
        mock_graph = Mock()
        mock_graph.run.return_value.data.return_value = [
            {"source": "感冒", "target": "发热", "rel_type": "disease_symptom"},
            {"source": "感冒", "target": "板蓝根", "rel_type": "disease_drug"},
        ]
        mock_get_graph.return_value = mock_graph
        request = self.factory.get("/analysis/search/", {"keyword": "感冒"})

        response = views_analysis.analysis_graph_search(request)

        payload = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["links"][0]["type"], "症状")
        self.assertEqual(payload["links"][1]["type"], "药物")
        args, kwargs = mock_graph.run.call_args
        self.assertEqual(kwargs["keyword"], "感冒")
        self.assertIn("CONTAINS $keyword", args[0])

    @patch("wenda.views_analysis.requests.post")
    def test_deepseek_ask_returns_model_answer(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "建议先休息，多喝水，如症状加重及时就医。"}}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        request = self.factory.get("/deepseek/ask/", {"question": "我发烧咳嗽怎么办"})

        response = views_analysis.deepseek_ask(request)

        payload = json.loads(response.content)
        self.assertIn("建议先休息", payload["answer"])
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["json"]["model"], "deepseek-chat")
        self.assertEqual(kwargs["json"]["messages"][1]["content"], "我发烧咳嗽怎么办")


class DiagnosisViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_smart_diagnosis_rejects_invalid_json(self):
        request = self.factory.post(
            "/smart_diagnosis/",
            data="{not-json}",
            content_type="application/json",
        )

        response = views_diagnosis.smart_diagnosis(request)

        payload = json.loads(response.content)
        self.assertEqual(payload["status"], "error")
        self.assertIn("JSON", payload["msg"])

    def test_smart_diagnosis_requires_text(self):
        request = self.factory.post(
            "/smart_diagnosis/",
            data=json.dumps({"text": "   "}),
            content_type="application/json",
        )

        response = views_diagnosis.smart_diagnosis(request)

        payload = json.loads(response.content)
        self.assertEqual(payload, {"status": "error", "msg": "请输入症状描述"})

    @patch("wenda.views_diagnosis._lookup_diagnosis_drugs", return_value="对乙酰氨基酚")
    @patch("diagnosis.service.load_diagnosis_service")
    def test_smart_diagnosis_formats_prediction_payload(self, mock_loader, _mock_drug_lookup):
        mock_service = Mock()
        mock_service.predict.return_value = {
            "matched_symptoms": ["发热", "咳嗽"],
            "predictions": [{"disease": "感冒", "probability": 92.5}],
        }
        mock_loader.return_value = mock_service
        request = self.factory.post(
            "/smart_diagnosis/",
            data=json.dumps({"text": "发热咳嗽两天"}),
            content_type="application/json",
        )

        response = views_diagnosis.smart_diagnosis(request)

        payload = json.loads(response.content)
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["matched_symptoms"], ["发热", "咳嗽"])
        self.assertEqual(
            payload["data"],
            [{"disease": "感冒", "probability": 92.5, "drugs": "对乙酰氨基酚"}],
        )
        mock_service.predict.assert_called_once_with("发热咳嗽两天", top_k=3)


if __name__ == "__main__":
    unittest.main()
