from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *
from django.contrib import messages
from .forms import *
#import requests
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from io import BytesIO
from django.core.paginator import Paginator

def home(request):
    #return render(request, 'base.html')
    #instance = auth_user.objects.get(id=8)
    #instance.delete()
    #user_to_delete = User.objects.get(username='user')
    #user_to_delete.delete()
    return redirect('dashboard')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            '''data = {
                "username": form.cleaned_data['username'],
                "password": form.cleaned_data['password'],
                "re_password": form.cleaned_data['re_password'],
                "email": form.cleaned_data['email'],
            }
            response = requests.post('http://localhost:8000/auth/users/', json=data)

            if response.status_code == 201:'''
            try:
                User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password']
                )
                messages.success(request, "Registration successful! Please log in.")
                return redirect('loginTemp')
            except Exception as exc:
                messages.error(request, f"Registration failed: {exc}")
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard') 
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('loginTemp')  # Change to your desired redirect URL name

@login_required
def dashboard_view(request):
    projects = Project.objects.filter(user=request.user).filter(is_active=True).prefetch_related('invoice_set')
    invoices = Invoice.objects.filter(project__user=request.user)

    paginator = Paginator(projects, 5)

    page_number = request.GET.get('page')
    projects_pag = paginator.get_page(page_number)
    
    context = {
        'projects': projects_pag,
        'invoices': invoices,
    }
    return render(request, 'dashboard.html', context)

@login_required
def completed_view(request):
    projects = Project.objects.filter(user=request.user).filter(is_active=False).prefetch_related('invoice_set')
    invoices = Invoice.objects.filter(project__user=request.user)

    paginator = Paginator(projects, 5)

    page_number = request.GET.get('page')
    projects_pag = paginator.get_page(page_number)
    
    context = {
        'projects': projects_pag,
        'invoices': invoices,
    }
    return render(request, 'completed.html', context)

@login_required
def account_view(request):
    user = request.user
    if request.method == 'POST':
        form = AccountUpdateForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)

            # Handle password change
            new_password = form.cleaned_data.get('new_password')
            if new_password:
                updated_user.set_password(new_password)
            updated_user.save()

            messages.success(request, "Account updated successfully.")
            return redirect('login') if new_password else redirect('account')
    else:
        form = AccountUpdateForm(instance=user)

    return render(request, 'account.html', {'form': form})

    
@login_required
def create_project_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect('dashboard')  # Or wherever you want to send them
    else:
        form = ProjectForm()
    return render(request, 'create_project.html', {'form': form})

@login_required
def set_project_inactive_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        project.is_active=False
        project.save()
    return redirect('dashboard')

@login_required
def set_project_active_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        project.is_active=True
        project.save()
    return redirect('completed')

@login_required
def add_time_entry_for_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    if request.method == 'POST':
        form = TimeEntryForm(request.POST)
        if form.is_valid():
            time_entry = form.save(commit=False)
            time_entry.project = project
            time_entry.save()
            return redirect('dashboard')
    else:
        form = TimeEntryForm()

    return render(request, 'add_time_entry.html', {'form': form, 'project': project})

@login_required
def start_timer_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    # Stop any running timers for this user
    TimeEntry.objects.filter(project__user=request.user, is_running=True).update(is_running=False, end_time=now())

    # Start a new time entry
    TimeEntry.objects.create(
        project=project,
        start_time=now(),
        is_running=True
    )
    return redirect('project_time_entries', project_id=project.id)

@login_required
def stop_timer_view(request, project_id):
    running_entry = TimeEntry.objects.filter(project__id=project_id, is_running=True, project__user=request.user).first()
    if running_entry:
        running_entry.end_time = now()
        running_entry.is_running = False
        running_entry.save()
    return redirect('project_time_entries', project_id=project_id)

@login_required
def delete_time_entry_view(request, entry_id):
    entry = get_object_or_404(TimeEntry, id=entry_id)
    project_id = entry.project.id

    # Ensure the user owns the project
    if entry.project.user != request.user:
        return redirect('dashboard')

    if request.method == 'POST':
        entry.delete()
    return redirect('project_time_entries', project_id=project_id)

@login_required
def project_time_entries_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    time_entries = TimeEntry.objects.filter(project=project).order_by('-created_at')
    
    total_hours = sum(entry.total_hours() for entry in time_entries)

    return render(request, 'project_time_entries.html', {
        'project': project,
        'time_entries': time_entries,
        'total_hours': total_hours,
    })
    
@login_required
def create_invoice_view(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.user = request.user

            # Calculate total from time entries
            time_entries = TimeEntry.objects.filter(project=invoice.project)
            invoice.total_hours = sum(te.total_hours() for te in time_entries)
            if invoice.project.billing_type == 'hourly':
                hourly_rate = invoice.project.hourly_rate or Decimal('0.00')
                invoice.total_amount = invoice.total_hours * hourly_rate
            else:
                hourly_rate = invoice.project.fixed_rate or Decimal('0.00')
                invoice.total_amount = hourly_rate
            invoice.save()
            return redirect('invoice_list')
    else:
        form = InvoiceForm()

    return render(request, 'create_invoice.html', {'form': form})

@login_required
def create_invoice_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    time_entries = TimeEntry.objects.filter(project=project)

    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.project = project
            invoice.total_hours = sum(te.total_hours() for te in time_entries)
            if invoice.project.billing_type == 'hourly':
                hourly_rate = invoice.project.hourly_rate or Decimal('0.00')
                invoice.total_amount = invoice.total_hours * hourly_rate
            else:
                hourly_rate = invoice.project.fixed_rate or Decimal('0.00')
                invoice.total_amount = hourly_rate
            invoice.save()
            invoice.save()
            #invoice.time_entries.set(time_entries)
            return redirect('invoice_detail', invoice.id)
    else:
        form = InvoiceForm()

    return render(request, 'create_invoice.html', {
        'form': form,
        'project': project,
        'time_entries': time_entries
    })
    
@login_required
def invoice_list_view(request):
    invoices = Invoice.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'invoice_list.html', {'invoices': invoices})

@login_required
def edit_time_entry_description(request, entry_id):
    entry = get_object_or_404(TimeEntry, id=entry_id, project__user=request.user)

    if request.method == 'POST':
        new_description = request.POST.get('description', '').strip()
        if new_description:
            entry.description = new_description
            entry.save()
            return redirect('project_time_entries', entry.project.id)

    return render(request, 'edit_time_entry.html', {'entry': entry})

'''@login_required
def project_invoices_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    invoices = project.invoice_set.all()
    return render(request, 'project_invoices.html', {
        'project': project,
        'invoices': invoices
    })'''

@login_required
def project_invoices_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    invoice_list = project.invoice_set.all().order_by('-created_at')

    paginator = Paginator(invoice_list, 2) 
    page_number = request.GET.get('page')
    invoices = paginator.get_page(page_number)

    return render(request, 'project_invoices.html', {
        'project': project,
        'invoices': invoices
    })
    
@login_required
def invoice_detail_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    time_entries = TimeEntry.objects.filter(project=invoice.project)
    return render(request, 'invoice_detail.html', {
        'invoice': invoice,
        'time_entries': time_entries
    })

@login_required
def update_invoice_status_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    if request.method == 'POST':
        form = InvoiceStatusForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            return redirect('invoice_detail', invoice_id=invoice.id)
    else:
        form = InvoiceStatusForm(instance=invoice)

    return render(request, 'update_invoice_status.html', {
        'invoice': invoice,
        'form': form
    })

@login_required
def delete_invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    if request.method == 'POST':
        invoice.delete()
        return redirect('invoice_list')
    return render(request, 'confirm_delete_invoice.html', {'invoice': invoice})

@login_required
def export_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    time_entries = TimeEntry.objects.filter(project=invoice.project)

    template = get_template("invoice_pdf.html")
    html = template.render({'invoice': invoice, 'time_entries': time_entries})
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'

    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    response.write(pdf.getvalue())
    return response