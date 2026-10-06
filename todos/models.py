from django.db import models
from django.contrib.auth.models import User


class Todo(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    completed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    due_date = models.DateField(
        null=True,
        blank=True
    )

    priority = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High')
        ],
        default='medium'
    )

    category = models.CharField(
        max_length=20,
        choices=[
            ('work', '💼 Work'),
            ('study', '📚 Study'),
            ('personal', '🏠 Personal'),
            ('shopping', '🛒 Shopping'),
            ('health', '💪 Health'),
            ('other', '📌 Other')
        ],
        default='other'
    )

    def __str__(self):
        return self.title