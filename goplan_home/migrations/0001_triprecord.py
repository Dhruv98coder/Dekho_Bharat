from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="TripRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_key", models.CharField(blank=True, db_index=True, max_length=40)),
                ("title", models.CharField(max_length=180)),
                ("origin", models.CharField(blank=True, max_length=180)),
                ("destination", models.CharField(max_length=180)),
                ("mode", models.CharField(default="car", max_length=30)),
                ("distance_km", models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ("duration_minutes", models.PositiveIntegerField(blank=True, null=True)),
                ("details", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="auth.user")),
            ],
            options={"ordering": ("-created_at",)},
        ),
    ]