from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *
from django.contrib import messages
from .forms import *
from datetime import date
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from io import BytesIO
from django.core.paginator import Paginator
from django.db.models import Q

def home(request):
    #return render(request, 'base.html')
    '''instance = Client.objects.get(id=9)
    instance.delete()
    user_to_delete = User.objects.get(username='test')
    user_to_delete.delete()
    instance2 = Project.objects.get(id=3)
    instance2.delete()'''
    return redirect('dashboard')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
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
    query = request.GET.get('q', '')
    
    projects = Project.objects.filter(user=request.user).filter(is_active=True).prefetch_related('invoice_set')
    invoices = Invoice.objects.filter(project__user=request.user)
    
    if query:
        projects = projects.filter(
            Q(name__icontains=query) |
            Q(client__name__icontains=query) |
            Q(client__company__icontains=query) |
            Q(client__email__icontains=query) |
            Q(client__phone__icontains=query) |
            Q(client__address__icontains=query) |
            Q(start_date__icontains=query)
        )


    paginator = Paginator(projects, 5)

    page_number = request.GET.get('page')
    projects_pag = paginator.get_page(page_number)
    
    context = {
        'projects': projects_pag,
        'invoices': invoices,
        'query': query,
    }
    return render(request, 'dashboard.html', context)

@login_required
def completed_view(request):
    query = request.GET.get('q', '')
    
    projects = Project.objects.filter(user=request.user).filter(is_active=False).prefetch_related('invoice_set')
    invoices = Invoice.objects.filter(project__user=request.user)

    if query:
        projects = projects.filter(
            Q(name__icontains=query) |
            Q(client__name__icontains=query) |
            Q(client__company__icontains=query) |
            Q(client__email__icontains=query) |
            Q(client__phone__icontains=query) |
            Q(client__address__icontains=query) |
            Q(start_date__icontains=query)
        )
        
    paginator = Paginator(projects, 5)

    page_number = request.GET.get('page')
    projects_pag = paginator.get_page(page_number)
    
    context = {
        'projects': projects_pag,
        'invoices': invoices,
        'query': query,
    }
    return render(request, 'completed.html', context)

@login_required
def client_projects_view(request, client_id):
    client = get_object_or_404(Client, id=client_id, user=request.user)
    projects = Project.objects.filter(client=client, user=request.user)
    return render(request, 'client_projects.html', {
        'client': client,
        'projects': projects
    })
    
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
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)  # log the user out first
        user.delete()    # delete the user from DB
        messages.success(request, "Your account has been deleted.")
        return redirect('home')  # or wherever you want to send them

    return render(request, 'delete_account.html')

@login_required
def client_list_view(request):
    query = request.GET.get('q', '')
    
    clients = Client.objects.filter(user=request.user)
    
    if query:
        clients = clients.filter(
            Q(name__icontains=query) |
            Q(company__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(address__icontains=query) 
        )
        
    paginator = Paginator(clients, 20)

    page_number = request.GET.get('page')
    clients_pag = paginator.get_page(page_number)
    
    return render(request, 'client_list.html', {'clients': clients_pag, 'query': query,})

@login_required
def edit_client_view(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'edit_client.html', {'form': form, 'client': client})
    
@login_required
def create_project_view(request):
    clients = Client.objects.filter(user=request.user).count()
    if request.method == 'POST':
        form = ProjectForm(request.POST, user=request.user)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            
            if form.cleaned_data['use_existing_client']:
                project.client = form.cleaned_data['existing_client']
            else:
                new_client = Client.objects.create(
                    user=request.user,
                    name=form.cleaned_data['client_name'],
                    company=form.cleaned_data['client_company'],
                    email=form.cleaned_data['client_email'],
                    phone=form.cleaned_data['client_phone'],
                    address=form.cleaned_data['client_address']
                )
                project.client = new_client
            
            project.full_clean()    
            project.save()
            return redirect('dashboard') 
    else:
        form = ProjectForm(user=request.user)
    return render(request, 'create_project.html', {'form': form, 'clients': clients})

@login_required
def set_project_inactive_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        project.is_active=False
        project.save()
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def set_project_active_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        project.is_active=True
        project.save()
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def add_time_entry_for_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    if request.method == 'POST':
        form = TimeEntryForm(request.POST)
        if form.is_valid():
            time_entry = form.save(commit=False)
            time_entry.project = project
            time_entry.full_clean()
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
    
'''@login_required
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
            for entry in time_entries:
                entry.invoice = get_object_or_404(Invoice, id=invoice.id, user=request.user)
                entry.save()
            return redirect('invoice_list')
    else:
        form = InvoiceForm()

    return render(request, 'create_invoice.html', {'form': form})'''

@login_required
def create_invoice_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    time_entries = TimeEntry.objects.filter(project=project).filter(invoice=None)

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
            for entry in time_entries:
                entry.invoice = get_object_or_404(Invoice, id=invoice.id, user=request.user)
                entry.save()
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
    project = request.GET.get('project', '')
    client = request.GET.get('client', '')
    invoice_start = request.GET.get('invoice_start', '')
    invoice_due = request.GET.get('invoice_due', '')
    status = request.GET.get('status', '')
    invoices = Invoice.objects.filter(project__user=request.user).order_by('due_date')

    if project:
        invoices = invoices.filter(
            Q(project__name__icontains=project) 
        )
    if client:
        invoices = invoices.filter(
            Q(project__client__name__icontains=client) |
            Q(project__client__company__icontains=client) |
            Q(project__client__email__icontains=client) |
            Q(project__client__phone__icontains=client) |
            Q(project__client__address__icontains=client) 
        )
    if invoice_start:
        invoices = invoices.filter(
            Q(created_at__icontains=invoice_start)
        )
    if invoice_due:
        invoices = invoices.filter(
            Q(due_date__icontains=invoice_due)
        )
    if status:
        invoices = invoices.filter(status=status)

    paginator = Paginator(invoices, 20)

    page_number = request.GET.get('page')
    invoices_pag = paginator.get_page(page_number)
    
    return render(request, 'invoice_list.html', {
        'invoices': invoices_pag,
        'status': status,
        'project': project,
        'client' : client,
        'invoice_start' : invoice_start,
        'invoice_due' : invoice_due,
        'today': date.today(),
    })

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

@login_required
def project_invoices_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    invoice_list = project.invoice_set.all().order_by('due_date')
        
    paginator = Paginator(invoice_list, 20) 
    page_number = request.GET.get('page')
    invoices = paginator.get_page(page_number)

    return render(request, 'project_invoices.html', {
        'project': project,
        'invoices': invoices
    })
    
@login_required
def invoice_detail_view(request, invoice_id):
    #invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    invoice = Invoice.objects.get(id=invoice_id)
    time_entries = TimeEntry.objects.filter(project=invoice.project).filter(invoice=invoice.id)
    
    if invoice.project.billing_type == 'hourly':
        entry_details = []
        total_paid = 0
        total_unpaid = 0

        rate = invoice.project.hourly_rate or Decimal('0.00')

        invoice.total_hours = sum(te.total_hours() for te in time_entries)
        formatted_total_amount = f"{invoice.total_hours * rate:.2f}"
        invoice.total_amount = formatted_total_amount
        invoice.save()
        for entry in time_entries:
            hours = entry.total_hours() or 0
            amount = hours * rate
            if entry.paid == "Paid":
                total_paid += amount
            else:
                total_unpaid += amount
            formatted_amount = f"{amount:.2f}"
            entry_details.append({
                'entry': entry,
                'hours': hours,
                'amount': formatted_amount
            })
        
        formatted_total_unpaid = f"{total_unpaid:.2f}"
        formatted_total_paid = f"{total_paid:.2f}"
        
        return render(request, 'invoice_detail.html', {
            'invoice': invoice,
            'entry_details': entry_details,
            'total_paid': formatted_total_paid,
            'total_unpaid': formatted_total_unpaid,
        })
    else:
        return render(request, 'invoice_detail.html', {
        'invoice': invoice,
        'entry_details': time_entries
        })
        

@login_required
def update_invoice_status_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    time_entries = TimeEntry.objects.filter(project=invoice.project)
    
    if request.method == 'POST':
        form = InvoiceStatusForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            if invoice.status == 'Paid':
                for entries in time_entries:
                    entries.paid = "Paid"
                    entries.save()
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
    time_entries = TimeEntry.objects.filter(project=invoice.project)
    if request.method == 'POST':
        id = invoice.project.id
        for entry in time_entries:
            entry.invoice = None
            entry.save()
        invoice.delete()
        return redirect('project_invoices', id)
    return render(request, 'confirm_delete_invoice.html', {'invoice': invoice})

@login_required
def export_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    time_entries = TimeEntry.objects.filter(project=invoice.project).filter(invoice=invoice.id)

    if invoice.project.billing_type == 'hourly':
        entry_details = []
        total_paid = 0
        total_unpaid = 0

        rate = invoice.project.hourly_rate or Decimal('0.00')

        invoice.total_hours = sum(te.total_hours() for te in time_entries)
        formatted_total_amount = f"{invoice.total_hours * rate:.2f}"
        invoice.total_amount = formatted_total_amount
        invoice.save()
        for entry in time_entries:
            hours = entry.total_hours() or 0
            amount = hours * rate
            if entry.paid == "Paid":
                total_paid += amount
            else:
                total_unpaid += amount
            formatted_amount = f"{amount:.2f}"
            entry_details.append({
                'entry': entry,
                'hours': hours,
                'amount': formatted_amount
            })
        
        formatted_total_unpaid = f"{total_unpaid:.2f}"
        formatted_total_paid = f"{total_paid:.2f}"
        
        money = []
        money.append({
            'total_paid': formatted_total_paid,
            'total_unpaid': formatted_total_unpaid,
        })
        
        template = get_template("invoice_pdf.html")
        html = template.render({
            'invoice': invoice,
            'time_entries': entry_details,
            'total_paid': formatted_total_paid,
            'total_unpaid': formatted_total_unpaid,
        })
    else:
        template = get_template("invoice_pdf.html")
        html = template.render({
        'invoice': invoice,
        'time_entries': time_entries
        })
        
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'

    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    response.write(pdf.getvalue())
    return response