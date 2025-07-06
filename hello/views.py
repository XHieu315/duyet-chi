from django.utils.timezone import datetime
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from hello.forms import LogMessageForm
from django.views.generic import ListView
from .forms import ExpenseRequestForm, RegisterForm
from .models import ExpenseRequest
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserProfile, ExpenseRequest
from .forms import ProfileUpdateForm, AvatarUpdateForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, get_object_or_404
from .models import EditPermission, User
from django.contrib import messages

class HomeListView(ListView):
    """Renders the home page, with a list of all messages."""
    

def about(request):
    return render(request, "hello/about.html")


# Add this code elsewhere in the file:
def log_message(request):
    form = LogMessageForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            message = form.save(commit=False)
            message.log_date = datetime.now()
            message.save()
            return redirect("home")
    else:
        return render(request, "hello/log_message.html", {"form": form})

@login_required
def create_expense_request(request):
    if request.method == 'POST':
        form = ExpenseRequestForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.employee = request.user
            expense.save()
            return redirect('expense_list')
    else:
        form = ExpenseRequestForm()
    return render(request, 'hello/create_expense_request.html', {'form': form})

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "hello/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "hello/login.html", {"form": form})

@login_required
def dashboard(request):
    waiting_count = ExpenseRequest.objects.filter(status__in=['submitted', 'manager_approved', 'accountant_approved']).count()
    approved_amount = ExpenseRequest.objects.filter(status='director_approved').aggregate(
        total=Sum(ExpressionWrapper(F('quantity') * F('unit_price'), output_field=DecimalField()))
    )['total'] or 0
    recent_requests = ExpenseRequest.objects.filter(employee=request.user).order_by('created_at')
    permissions = {p.user_id: p.can_edit for p in EditPermission.objects.all()}  # Thêm dòng này
    return render(request, 'hello/dashboard.html', {
        'waiting_count': waiting_count,
        'approved_amount': approved_amount,
        'recent_requests': recent_requests,
        'permissions': permissions,
    })


@login_required
def approval_list(request):
    tab = request.GET.get('tab', 'manager')
    if tab == 'manager':
        requests = ExpenseRequest.objects.filter(status='submitted')
    elif tab == 'accountant':
        requests = ExpenseRequest.objects.filter(status='manager_approved')
    elif tab == 'director':
        requests = ExpenseRequest.objects.filter(status='accountant_approved')
    else:
        requests = ExpenseRequest.objects.none()
    permissions = {p.user_id: p.can_edit for p in EditPermission.objects.all()}
    return render(request, 'hello/approval_list.html', {'requests': requests, 'tab': tab, 'permissions': permissions})

@login_required
def approval_detail(request, pk):
    req = get_object_or_404(ExpenseRequest, pk=pk)
    has_approve_permission = (
        request.user.is_superuser or
        EditPermission.objects.filter(user=request.user, can_edit=True).exists()
    )
    if request.method == 'POST':
        if not has_approve_permission:
            return HttpResponse("Bạn không có quyền duyệt đề xuất này.", status=403)
        comment = request.POST.get('comment', '')
        if 'approve' in request.POST:
            if req.status == 'submitted':
                req.status = 'manager_approved'
                req.manager_comment = comment
            elif req.status == 'manager_approved':
                req.status = 'accountant_approved'
                req.accountant_comment = comment
            elif req.status == 'accountant_approved':
                req.status = 'director_approved'
                req.director_comment = comment
            req.save()
            messages.success(request, "Đã duyệt đề xuất!")
        elif 'reject' in request.POST:
            req.status = 'rejected'
            req.save()
            messages.error(request, "Đã từ chối đề xuất!")
        elif 'edit_required' in request.POST:
            req.status = 'edit_required'
            req.save()
            messages.warning(request, "Yêu cầu chỉnh sửa đề xuất!")
        return redirect('approval_list')
    return render(request, 'hello/approval_detail.html', {'req': req, 'has_approve_permission': has_approve_permission})

@login_required
def report(request):
    status_choices = ExpenseRequest.STATUS_CHOICES
    status = request.GET.get('status', '')
    employee = request.GET.get('employee', '')
    month = request.GET.get('month', '')
    requests = ExpenseRequest.objects.all() # Lấy tất cả các yêu cầu chi tiêu
    permissions = {p.user_id: p.can_edit for p in EditPermission.objects.all()}  # Thêm dòng này
    if status:
        requests = requests.filter(status=status)
    if employee:
        requests = requests.filter(employee__username__icontains=employee)
    if month:
        year, month_num = month.split('-')
        requests = requests.filter(created_at__year=year, created_at__month=month_num)
    # requests = requests.order_by('-updated_at')  # Sắp xếp theo ngày duyệt mới nhất đến cũ nhất
    total_approved = requests.count()
    total_amount = requests.aggregate(
        total=Sum(ExpressionWrapper(F('quantity') * F('unit_price'), output_field=DecimalField()))
    )['total'] or 0
    return render(request, 'hello/report.html', {
        'requests': requests,
        'total_approved': total_approved,
        'total_amount': total_amount,
        'status_choices': status_choices,
        'status': status,
        'employee': employee,
        'month': month,
        'permissions': permissions,
    })


@login_required
def profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    expense_history = ExpenseRequest.objects.filter(employee=request.user).order_by('created_at')
    return render(request, 'hello/profile.html', {
        'profile': profile,
        'expense_history': expense_history,
    })

@login_required
def profile_update(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, instance=request.user)
        a_form = AvatarUpdateForm(request.POST, request.FILES, instance=profile)
        if p_form.is_valid() and a_form.is_valid():
            p_form.save()
            a_form.save()
            return redirect('profile')
    else:
        p_form = ProfileUpdateForm(instance=request.user)
        a_form = AvatarUpdateForm(instance=profile)
    return render(request, 'hello/profile_update.html', {
        'p_form': p_form,
        'a_form': a_form,
        'profile': profile,
    })



@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseRequestForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.employee = request.user
            expense.save()
            return redirect('dashboard')
    else:
        form = ExpenseRequestForm()
    return render(request, 'hello/expense_create.html', {'form': form})

@login_required
def expense_update(request, pk):
    expense = get_object_or_404(ExpenseRequest, pk=pk)
    if request.method == 'POST':
        form = ExpenseRequestForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ExpenseRequestForm(instance=expense)
    return render(request, 'hello/expense_update.html', {'form': form})


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(ExpenseRequest, pk=pk)
    # Kiểm tra quyền: admin hoặc user có quyền chỉnh sửa hoặc chủ đơn
    has_edit_permission = (
        request.user.is_superuser or
        EditPermission.objects.filter(user=request.user, can_edit=True).exists()
    )
    is_owner = expense.employee == request.user

    if not (has_edit_permission or is_owner):
        return HttpResponse("Bạn không có quyền xóa đề xuất này.", status=403)

    if request.method == 'POST':
        expense.delete()
        return redirect('dashboard')
    return render(request, 'hello/expense_confirm_delete.html', {'expense': expense})

@login_required
def home(request):
    users = User.objects.all().order_by('-date_joined')
    permissions = {p.user_id: p.can_edit for p in EditPermission.objects.all()}

    # Tổng hợp số lượng đề xuất theo trạng thái
    from django.db.models import Count, F, Sum, ExpressionWrapper, DecimalField
    status_labels = [label for key, label in ExpenseRequest.STATUS_CHOICES]
    status_keys = [key for key, label in ExpenseRequest.STATUS_CHOICES]
    status_counts = []
    for key in status_keys:
        count = ExpenseRequest.objects.filter(status=key).count()
        status_counts.append(count)
    # Tổng hợp tổng tiền từng trạng thái (nếu muốn)
    status_amounts = []
    for key in status_keys:
        amount = ExpenseRequest.objects.filter(status=key).aggregate(
            total=Sum(ExpressionWrapper(F('quantity') * F('unit_price'), output_field=DecimalField()))
        )['total'] or 0
        status_amounts.append(float(amount))

    return render(request, 'hello/home.html', {
        'users': users,
        'permissions': permissions,
        'status_labels': status_labels,
        'status_counts': status_counts,
        'status_amounts': status_amounts,
    })

@login_required
def expense_permission_list(request):
    users = User.objects.all().order_by('-date_joined')
    permissions = {p.user_id: p.can_edit for p in EditPermission.objects.all()}
    return render(request, 'hello/expense_permission_list.html', {
        'users': users,
        'permissions': permissions,
    })


@user_passes_test(lambda u: u.is_superuser)
def toggle_edit_permission(request, user_id):
    user = get_object_or_404(User, id=user_id)
    perm, created = EditPermission.objects.get_or_create(user=user)
    if perm.can_edit:
        perm.can_edit = False
    else:
        perm.can_edit = True
    perm.save()
    return redirect('expense_permission_list')

@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('expense_permission_list')
    return HttpResponse("Phương thức không hợp lệ.", status=405)

@login_required
def expense_detail(request, pk):
    req = get_object_or_404(ExpenseRequest, pk=pk)
    return render(request, 'hello/expense_detail.html', {'req': req})
