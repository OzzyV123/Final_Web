from django.contrib import admin
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import *

admin.site.register(Post)
admin.site.register(PostMedia)
admin.site.register(Comments)

User = get_user_model()

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'sent')
    actions = ['send_newsletter']

    def send_newsletter(self, request, queryset):
        for newsletter in queryset:
            if newsletter.sent:
                continue

            users = User.objects.filter(is_active=True, is_staff=False)
            recipient_list = [u.email for u in users if u.email]

            # Генерируем HTML из шаблона
            html_content = render_to_string(
                'emails/newsletter.html',
                {
                    'title': newsletter.title,
                    'content': newsletter.content,
                    'site_url': request.build_absolute_uri('/')[:-1]  # URL сайта
                }
            )

            # Отправка письма
            msg = EmailMultiAlternatives(
                subject=newsletter.title,
                body=newsletter.content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipient_list
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)

            newsletter.sent = True
            newsletter.save()

        self.message_user(request, "Рассылка отправлена.")
    send_newsletter.short_description = "Отправить выбранные рассылки"
