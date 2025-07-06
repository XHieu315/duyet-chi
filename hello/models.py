from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django import template
from django import forms

register = template.Library()

@register.filter
def get(dict_data, key):
    return dict_data.get(key)

class LogMessage(models.Model):
    message = models.CharField(max_length=300)
    log_date = models.DateTimeField("date logged")

    def __str__(self):
        """Returns a string representation of a message."""
        date = timezone.localtime(self.log_date)
        return f"'{self.message}' logged on {date.strftime('%A, %d %B, %Y at %X')}"

class ExpenseRequest(models.Model):
    EXPENSE_TYPE_CHOICES = [
        ('packaging', 'Mua bao bì'),
        ('maintenance', 'Bảo dưỡng máy'),
        ('fertilizer', 'Mua phân bón'),
        # Thêm các loại chi khác nếu cần
    ]
    STATUS_CHOICES = [
        ('submitted', 'Đã gửi'),
        ('manager_approved', 'Trưởng bộ phận duyệt'),
        ('accountant_approved', 'Kế toán duyệt'),
        ('director_approved', 'Giám đốc duyệt'),
        ('rejected', 'Từ chối'),
        ('edit_required', 'Yêu cầu chỉnh sửa'),
    ]
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    expense_type = models.CharField(max_length=50, choices=EXPENSE_TYPE_CHOICES)
    reason = models.TextField()
    invoice_image = models.ImageField(upload_to='invoices/', blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='submitted')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    manager_comment = models.TextField(blank=True, null=True)
    accountant_comment = models.TextField(blank=True, null=True)
    director_comment = models.TextField(blank=True, null=True)
    detail = models.CharField(max_length=255, verbose_name="Chi tiết")
    content = models.TextField(verbose_name="Nội dung")
    quantity = models.PositiveIntegerField(verbose_name="Số lượng")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Đơn giá")

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.get_expense_type_display()} - {self.total_price} ({self.get_status_display()})"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class EditPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='edit_permissions')
    can_edit = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {'Được phép' if self.can_edit else 'Không'}"

# forms.py
class AvatarUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar']

