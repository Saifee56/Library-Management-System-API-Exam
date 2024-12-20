from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils.timezone import now

class BookModel(models.Model):
    title=models.CharField(max_length=120)
    author=models.CharField(max_length=50)
    is_borrowed=models.BooleanField(default=False)
    borrowed_by=models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="borrowed_books"
    )
    availability_status=models.BooleanField(default=True)
    borrowed_at=models.DateTimeField(null=True,blank=True)
    return_deadline=models.DateTimeField(null=True,blank=True)

    def save(self,*args,**kwargs):
        if self.is_borrowed and not self.borrowed_at:
            self.borrowed_at=now()
            self.return_deadline=self.borrowed_at+timedelta(days=14)
        super().save(*args,**kwargs)

    def __str__(self):
        return self.title