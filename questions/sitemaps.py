from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Question


class QuestionSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Question.objects.order_by("-created_at")

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse("question_detail_slug", args=[obj.slug])
