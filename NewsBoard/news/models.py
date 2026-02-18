from django.db import models
from django.contrib.auth.models import User
import uuid

class Category(models.TextChoices):
    TANKS = 'tanks', 'Танки'
    HEALS = 'heals', 'Хилы'
    DD = 'dd', 'ДД'
    TRADERS = 'traders', 'Торговцы'
    GUILDMASTERS = 'guildmasters', 'Гилдмастеры'
    QUESTGIVERS = 'questgivers', 'Квестгиверы'
    BLACKSMITHS = 'blacksmiths', 'Кузнецы'
    LEATHERWORKERS = 'leatherworkers', 'Кожевники'
    ALCHEMISTS = 'alchemists', 'Зельевары'
    SPELLMASTERS = 'spellmasters', 'Мастера заклинаний'


class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.TANKS
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comments(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['post', 'content'], name='unique_comment_text_per_post')
        ]

    def __str__(self):
        return f'Отклик от {self.author}'


class EmailConfirmation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Newsletter(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class PostMedia(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='post_media/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_image(self):
        return self.file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif'))

    @property
    def is_video(self):
        return self.file.name.lower().endswith(('.mp4', '.webm'))

    def __str__(self):
        return f"{self.post.title} - {self.file.name}"
