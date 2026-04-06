from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from .models import Doctor, Feedback, Question, Reply, User


def infer_feedback_priority(obj):
    text = f"{obj.feedback_type} {obj.content}".lower()
    high_keywords = ("报错", "错误", "异常", "故障", "无法", "失败", "bug")
    medium_keywords = ("建议", "优化", "改进", "体验", "不方便")
    if any(keyword in text for keyword in high_keywords):
        return "high"
    if any(keyword in text for keyword in medium_keywords):
        return "medium"
    return "normal"


class FeedbackPriorityFilter(admin.SimpleListFilter):
    title = _("处理优先级")
    parameter_name = "priority_level"

    def lookups(self, request, model_admin):
        return (
            ("high", "高优先级"),
            ("medium", "中优先级"),
            ("normal", "常规"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        matching_ids = [item.id for item in queryset if infer_feedback_priority(item) == value]
        return queryset.filter(id__in=matching_ids)


class QuestionReplyStatusFilter(admin.SimpleListFilter):
    title = _("回复状态")
    parameter_name = "reply_status"

    def lookups(self, request, model_admin):
        return (
            ("pending", "待处理"),
            ("replied", "已回复"),
            ("rich", "回复充分"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "pending":
            return queryset.filter(reply__isnull=True).distinct()
        if value == "replied":
            return queryset.filter(reply__isnull=False).distinct()
        if value == "rich":
            rich_ids = [item.id for item in queryset if item.reply_set.count() >= 3]
            return queryset.filter(id__in=rich_ids)
        return queryset


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    fieldsets = (
        ("账号信息", {"fields": ("user_name", "mail", "password")}),
        ("个人信息", {"fields": ("name", "birth", "tel")}),
        ("执业信息", {"fields": ("hospital_region", "hospital", "department", "certificate")}),
        ("审核辅助", {"fields": ("profile_completeness_panel", "review_recommendation"), "classes": ("wide",)}),
        ("审核状态", {"fields": ("confirmed",), "description": "建议优先处理待审核医生，已通过记录仅做维护性更新。"}),
    )
    list_display = (
        "user_name",
        "name",
        "hospital",
        "department",
        "review_status_badge",
        "profile_completeness_badge",
        "contact_summary",
    )
    list_display_links = ("user_name", "name")
    list_filter = ("confirmed", "hospital_region", "department")
    search_fields = ("name", "hospital", "user_name", "department")
    ordering = ("-confirmed", "user_name")
    list_per_page = 15
    actions = ("approve_selected_doctors", "mark_selected_pending_review")
    readonly_fields = ("profile_completeness_panel", "review_recommendation")

    def review_status_badge(self, obj):
        if obj.confirmed == 1:
            css_class = "mc-badge-success"
            label = "已通过"
        elif obj.confirmed == -1:
            css_class = "mc-badge-warning"
            label = "待审核"
        else:
            css_class = "mc-badge-muted"
            label = "未提交"
        return format_html('<span class="mc-badge {}">{}</span>', css_class, label)

    review_status_badge.short_description = "审核状态"

    def contact_summary(self, obj):
        tel = obj.tel or "未填写电话"
        mail = obj.mail or "未填写邮箱"
        return format_html(
            '<div class="mc-admin-stack"><strong>{}</strong><span>{}</span></div>',
            tel,
            mail,
        )

    contact_summary.short_description = "联系方式"

    def profile_completeness_badge(self, obj):
        fields = [obj.name, obj.hospital_region, obj.hospital, obj.department, obj.certificate, obj.tel]
        completed = sum(1 for value in fields if value)
        if completed >= 5:
            css_class = "mc-badge-success"
            label = "完整"
        elif completed >= 3:
            css_class = "mc-badge-warning"
            label = "待补充"
        else:
            css_class = "mc-badge-muted"
            label = "信息少"
        return format_html('<span class="mc-badge {}">{}</span>', css_class, label)

    profile_completeness_badge.short_description = "资料完整度"

    def profile_completeness_panel(self, obj):
        fields = [
            ("姓名", obj.name),
            ("联系电话", obj.tel),
            ("地区", obj.hospital_region),
            ("医院", obj.hospital),
            ("科室", obj.department),
            ("执业证书", obj.certificate),
        ]
        rows = []
        for label, value in fields:
            status = "已填写" if value else "未填写"
            badge = "mc-badge-success" if value else "mc-badge-muted"
            rows.append(
                f'<div class="mc-review-row"><strong>{label}</strong><span class="mc-badge {badge}">{status}</span></div>'
            )
        return format_html('<div class="mc-review-panel">{}</div>', "".join(rows))

    profile_completeness_panel.short_description = "资料检查"

    def review_recommendation(self, obj):
        fields = [obj.name, obj.hospital_region, obj.hospital, obj.department, obj.certificate, obj.tel]
        completed = sum(1 for value in fields if value)
        if completed >= 5:
            text = "资料较完整，可优先进入通过审核。"
            badge = "mc-badge-success"
        elif completed >= 3:
            text = "资料基本可用，建议补齐后再决定。"
            badge = "mc-badge-warning"
        else:
            text = "关键信息较少，建议先补充资料。"
            badge = "mc-badge-danger"
        return format_html(
            '<div class="mc-review-note"><span class="mc-badge {}">审核建议</span><p>{}</p></div>',
            badge,
            text,
        )

    review_recommendation.short_description = "审核建议"

    def changelist_view(self, request, extra_context=None):
        if request.GET:
            return super().changelist_view(request, extra_context=extra_context)
        return HttpResponseRedirect(f"{request.path}?confirmed__exact=-1")

    def approve_selected_doctors(self, request, queryset):
        updated = queryset.update(confirmed=1)
        self.message_user(request, f"已批量通过 {updated} 条医生记录。")

    approve_selected_doctors.short_description = "批量设为已通过"

    def mark_selected_pending_review(self, request, queryset):
        updated = queryset.update(confirmed=-1)
        self.message_user(request, f"已批量设为待审核 {updated} 条医生记录。")

    mark_selected_pending_review.short_description = "批量设为待审核"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        ("账号信息", {"fields": ("user_name", "mail", "password")}),
        ("个人资料", {"fields": ("birth", "tel")}),
    )
    list_display = ("user_name", "mail", "birth", "tel")
    search_fields = ("user_name", "mail", "tel")
    ordering = ("user_name",)
    list_per_page = 15


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = (
        ("提问信息", {"fields": ("title", "user", "date", "time"), "description": "优先关注未回复问题和最近新增问题。"}),
        ("提问内容", {"fields": ("content",)}),
        ("巡检辅助", {"fields": ("reply_summary_panel", "reply_links_panel"), "classes": ("wide",)}),
    )
    list_display = ("id", "title", "user", "reply_count", "reply_status_badge", "latest_reply_link", "date", "time")
    list_display_links = ("id", "title")
    search_fields = ("title", "content", "user__user_name")
    list_filter = (QuestionReplyStatusFilter, "date")
    ordering = ("-date", "-time")
    list_per_page = 15
    readonly_fields = ("date", "time", "reply_summary_panel", "reply_links_panel")

    def reply_count(self, obj):
        return obj.reply_set.count()

    reply_count.short_description = "回复数"

    def reply_status_badge(self, obj):
        count = obj.reply_set.count()
        if count >= 3:
            css_class = "mc-badge-success"
            label = "回复充分"
        elif count >= 1:
            css_class = "mc-badge-warning"
            label = "已回复"
        else:
            css_class = "mc-badge-danger"
            label = "待处理"
        return format_html('<span class="mc-badge {}">{}</span>', css_class, label)

    reply_status_badge.short_description = "回复状态"

    def latest_reply_link(self, obj):
        latest_reply = obj.reply_set.order_by("-date", "-time", "-id").first()
        if not latest_reply:
            return format_html('<span class="mc-text-soft">暂无回复</span>')
        url = reverse("admin:wenda_reply_change", args=[latest_reply.id])
        return format_html('<a class="mc-inline-link" href="{}">查看最新回复</a>', url)

    latest_reply_link.short_description = "快捷入口"

    def reply_summary_panel(self, obj):
        replies = obj.reply_set.order_by("-date", "-time", "-id")
        count = replies.count()
        latest_reply = replies.first()
        if latest_reply:
            latest_doctor = latest_reply.doctor.name or latest_reply.doctor.user_name
            latest_text = latest_reply.content[:60] + ("..." if len(latest_reply.content) > 60 else "")
        else:
            latest_doctor = "暂无"
            latest_text = "当前问题还没有医生回复，建议优先巡检。"
        return format_html(
            '<div class="mc-review-note">'
            '<span class="mc-badge {}">回复概览</span>'
            '<p>当前回复数：{}。最近回复医生：{}。</p>'
            '<p>{}</p>'
            '</div>',
            "mc-badge-success" if count else "mc-badge-danger",
            count,
            latest_doctor,
            latest_text,
        )

    reply_summary_panel.short_description = "回复概览"

    def reply_links_panel(self, obj):
        replies = obj.reply_set.order_by("-date", "-time", "-id")[:5]
        if not replies:
            return format_html('<div class="mc-review-panel"><div class="mc-feed-empty">暂无可跳转的回复记录。</div></div>')
        rows = []
        for reply in replies:
            url = reverse("admin:wenda_reply_change", args=[reply.id])
            doctor_name = reply.doctor.name or reply.doctor.user_name
            rows.append(
                f'<div class="mc-review-row">'
                f'<strong>{doctor_name}</strong>'
                f'<a class="mc-inline-link" href="{url}">查看回复</a>'
                f'</div>'
            )
        return format_html('<div class="mc-review-panel">{}</div>', "".join(rows))

    reply_links_panel.short_description = "快速跳转"


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    fieldsets = (
        ("回复信息", {"fields": ("doctor", "question", "date", "time"), "description": "可先查看原问题上下文，再核对回复内容是否匹配。"}),
        ("原问题上下文", {"fields": ("question_context_panel",), "classes": ("wide",)}),
        ("回复内容", {"fields": ("content",)}),
        ("联动入口", {"fields": ("question_jump_link",), "classes": ("wide",)}),
    )
    list_display = ("id", "doctor", "question", "question_link", "reply_preview", "date", "time")
    list_display_links = ("id", "doctor")
    search_fields = ("content", "doctor__user_name", "question__title")
    list_filter = ("date", "doctor")
    ordering = ("-date", "-time")
    list_per_page = 15
    readonly_fields = ("date", "time", "question_context_panel", "question_jump_link")

    def reply_preview(self, obj):
        text = obj.content[:36] + ("..." if len(obj.content) > 36 else "")
        return text

    reply_preview.short_description = "回复摘要"

    def question_link(self, obj):
        url = reverse("admin:wenda_question_change", args=[obj.question.id])
        return format_html('<a class="mc-inline-link" href="{}">查看问题</a>', url)

    question_link.short_description = "问题入口"

    def question_context_panel(self, obj):
        title = obj.question.title
        content = obj.question.content[:120] + ("..." if len(obj.question.content) > 120 else "")
        asker = obj.question.user.user_name
        return format_html(
            '<div class="mc-review-note">'
            '<span class="mc-badge mc-badge-info">原问题</span>'
            '<p><strong>{}</strong></p>'
            '<p>提问用户：{}</p>'
            '<p>{}</p>'
            '</div>',
            title,
            asker,
            content,
        )

    question_context_panel.short_description = "问题上下文"

    def question_jump_link(self, obj):
        url = reverse("admin:wenda_question_change", args=[obj.question.id])
        return format_html('<a class="mc-inline-link" href="{}">跳转到对应问题详情</a>', url)

    question_jump_link.short_description = "快捷跳转"


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    fieldsets = (
        ("反馈概览", {"fields": ("feedback_type", "user_role", "user_id", "contact")}),
        ("处理辅助", {"fields": ("priority_preview",), "classes": ("wide",)}),
        ("反馈内容", {"fields": ("content",), "description": "优先处理包含报错、异常、无法使用等关键词的反馈。"}),
    )
    list_display = (
        "id",
        "feedback_type_badge",
        "priority_badge",
        "user_role",
        "user_id",
        "contact",
        "content_preview",
        "date",
    )
    list_display_links = ("id",)
    search_fields = ("feedback_type", "content", "contact")
    list_filter = (FeedbackPriorityFilter, "feedback_type", "user_role", "date")
    ordering = ("-date", "-time")
    list_per_page = 15
    readonly_fields = ("priority_preview",)

    def feedback_type_badge(self, obj):
        palette = {
            "disease": ("mc-badge-info", "疾病"),
            "symptom": ("mc-badge-primary", "症状"),
            "drug": ("mc-badge-success", "药物"),
            "wenda": ("mc-badge-warning", "问答"),
        }
        css_class, label = palette.get(obj.feedback_type, ("mc-badge-muted", obj.feedback_type))
        return format_html('<span class="mc-badge {}">{}</span>', css_class, label)

    feedback_type_badge.short_description = "反馈类型"

    def content_preview(self, obj):
        text = obj.content[:48] + ("..." if len(obj.content) > 48 else "")
        return format_html('<span class="mc-text-soft">{}</span>', text)

    content_preview.short_description = "反馈摘要"

    def priority_badge(self, obj):
        priority = infer_feedback_priority(obj)
        if priority == "high":
            css_class = "mc-badge-danger"
            label = "高优先级"
        elif priority == "medium":
            css_class = "mc-badge-warning"
            label = "中优先级"
        else:
            css_class = "mc-badge-info"
            label = "常规"
        return format_html('<span class="mc-badge {}">{}</span>', css_class, label)

    priority_badge.short_description = "处理优先级"

    def priority_preview(self, obj):
        priority = infer_feedback_priority(obj)
        if priority == "high":
            badge = "mc-badge-danger"
            text = "建议优先处理，可能涉及系统报错、功能不可用或严重异常。"
        elif priority == "medium":
            badge = "mc-badge-warning"
            text = "建议近期处理，通常与体验、建议或优化需求有关。"
        else:
            badge = "mc-badge-info"
            text = "常规反馈，可按日常节奏统一巡检。"
        return format_html(
            '<div class="mc-review-note"><span class="mc-badge {}">处理建议</span><p>{}</p></div>',
            badge,
            text,
        )

    priority_preview.short_description = "优先级说明"
