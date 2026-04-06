from datetime import timedelta

from django.utils import timezone

from .models import Doctor, Feedback, Question, Reply, User


def admin_dashboard_context(request):
    if not request.path.startswith("/admin/"):
        return {}

    try:
        today = timezone.localdate()
        seven_days_ago = today - timedelta(days=6)
        pending_doctors = Doctor.objects.filter(confirmed=-1).count()
        approved_doctors = Doctor.objects.filter(confirmed=1).count()
        total_users = User.objects.count()
        total_questions = Question.objects.count()
        total_replies = Reply.objects.count()
        total_feedback = Feedback.objects.count()
        questions_last_7_days = Question.objects.filter(date__gte=seven_days_ago).count()
        replies_last_7_days = Reply.objects.filter(date__gte=seven_days_ago).count()
        feedback_last_7_days = Feedback.objects.filter(date__gte=seven_days_ago).count()
        total_doctors = Doctor.objects.count()
        today_questions = Question.objects.filter(date=today).count()
        today_replies = Reply.objects.filter(date=today).count()
        today_feedback = Feedback.objects.filter(date=today).count()
        unanswered_questions = Question.objects.filter(reply__isnull=True).distinct().count()
        recent_pending_doctors = list(
            Doctor.objects.filter(confirmed=-1).order_by("-id").values(
                "id", "user_name", "name", "hospital", "department"
            )[:5]
        )
        recent_feedback_queryset = Feedback.objects.order_by("-date", "-time")[:5]
        recent_feedback = list(
            recent_feedback_queryset.values("id", "feedback_type", "user_role", "contact", "content")
        )
        high_priority_feedback = 0
        for feedback in Feedback.objects.only("feedback_type", "content"):
            text = f"{feedback.feedback_type} {feedback.content}".lower()
            if any(keyword in text for keyword in ("报错", "错误", "异常", "故障", "无法", "失败", "bug")):
                high_priority_feedback += 1
        recent_questions = list(
            Question.objects.select_related("user").order_by("-date", "-time").values(
                "id", "title", "user__user_name", "date"
            )[:5]
        )
    except Exception:
        return {}

    return {
        "admin_dashboard_metrics": {
            "pending_doctors": pending_doctors,
            "approved_doctors": approved_doctors,
            "total_users": total_users,
            "total_questions": total_questions,
            "total_replies": total_replies,
            "total_feedback": total_feedback,
            "questions_last_7_days": questions_last_7_days,
            "replies_last_7_days": replies_last_7_days,
            "feedback_last_7_days": feedback_last_7_days,
            "total_doctors": total_doctors,
            "today_questions": today_questions,
            "today_replies": today_replies,
            "today_feedback": today_feedback,
            "unanswered_questions": unanswered_questions,
            "high_priority_feedback": high_priority_feedback,
        },
        "admin_dashboard_recent": {
            "pending_doctors": recent_pending_doctors,
            "feedback": recent_feedback,
            "questions": recent_questions,
        },
        "admin_dashboard_timeline": {
            "today": str(today),
            "window_start": str(seven_days_ago),
        },
    }
