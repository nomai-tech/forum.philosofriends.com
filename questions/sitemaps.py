from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Question


class HomepageSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return ["question_list"]

    def lastmod(self, obj):
        latest_question = Question.objects.order_by("-created_at").only("created_at").first()
        return latest_question.created_at if latest_question else None

    def location(self, obj):
        return reverse(obj)
