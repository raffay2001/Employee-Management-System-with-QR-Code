from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.http import HttpResponse
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os
import cv2
from pyzbar import pyzbar
from PIL import Image

# main page function


# function for signup

def signup(request):
    if request.method == "POST":
        name = request.POST['name']
        l_name = request.POST['l_name']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        context = {
            "name": name,
            "l_name": l_name,
            "email": email,
            "pass1": pass1,
            "pass2": pass2,
        }
        if pass1 == pass2:
            if User.objects.filter(username=email).exists():
                print("Email already taken")
                messages.info(request, "Entered email already in use!")
                context['border'] = "email"
                return render(request, "signup.html", context)

            user = User.objects.create_user(
                username=email, first_name=name, password=pass1, last_name=l_name)
            user.save()

            return redirect("login")
        else:
            messages.info(request, "Your pasword doesn't match!")
            context['border'] = "password"
            return render(request, "signup.html", context)

    return render(request, "signup.html")


def get_company_by_admin(user_object):
    company_admin = CompanyAdmin.objects.get(user=user_object)
    company = Company.objects.get(company_admin=company_admin)
    return company
# function for login

# function for logout


def logout(request):
    auth.logout(request)
    return redirect("index")

# function for rendering the dashboard


@login_required
def dashboard(request):
    context = {
        "name": "dashboard"
    }

    return render(request, "index.html", context)


def read_qr(image):
    try:
        qr_code = pyzbar.decode(image)[0]
        # convert into string
        data = qr_code.data.decode("utf-8")
        return data
    except:
        return False



@login_required
def upload_qr_code(request):
    if request.method == "POST":
        qr_code = request.FILES['upload_qr_input']

        # saving into a model to save file in the folder
        new_scan = Scan(my_file=qr_code)
        new_scan.save()

        # getting base path
        BASE_DIR = settings.BASE_DIR
        # Making full path of the file
        file_path = os.path.join(BASE_DIR, "media", str(new_scan.my_file))
        # Calling a function which is using cv2
        # to detect and scan qr code
        image = Image.open(file_path)
        qr_content = read_qr(image)

        # printing the value of QR code
        print(qr_content)

        return redirect("index")

    return redirect("login")


@login_required
def all_employees(request):
    context = {
        "name": "all-employees"
    }

    company = get_company_by_admin(request.user)
    all_employees = Employee.objects.filter(company=company)
    context['all_employees'] = all_employees
    context['company'] = company
    return render(request, "all-employees.html", context)


@login_required
def save_employee(request):
    if request.method == "POST":
        profile_picture = request.FILES['profile_picture']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        designation = request.POST['designation']
        birthday = request.POST['birthday']

        # Get current admin
        current_admin = CompanyAdmin.objects.get(user=request.user)
        # Get current company
        company = Company.objects.get(company_admin=current_admin)

        # Check if this user has already been created
        query = Employee.objects.filter(
            email=email,  company=company) | Employee.objects.filter(phone=phone, company=company)

        if query.count() == 0:
            # Creating new employee
            new_employee = Employee(
                first_name=first_name,
                last_name=last_name,
                email=email,
                designation=designation,
                phone=phone,
                birthday=birthday,
                profile_picture=profile_picture,
                company=company,
            )
            new_employee.save()
            messages.info(request, "New employee has been registered!")
        else:
            messages.error(request, "This employee already exists!")

        return redirect("/all-employees/")

    return redirect("login")


@login_required
def update_employee(request):

    return redirect("login")


@login_required
def single_employee(request, id, index):
    if request.method == "POST":
        if id and len(id) > 0:
            employee = Employee.objects.filter(id=id)
            if employee.exists():
                employee = employee[0]

                company = get_company_by_admin(request.user)
                if employee.company == company:

                    if 'profile_picture' in request.FILES and request.FILES['profile_picture']:
                        employee.profile_picture = request.FILES['profile_picture']

                    employee.first_name = request.POST['first_name']
                    employee.last_name = request.POST['last_name']
                    employee.email = request.POST['email']
                    employee.phone = request.POST['phone']
                    employee.designation = request.POST['designation']
                    employee.birthday = request.POST['birthday']
                    employee.save()

                    messages.info(
                        request, "Employee info has been updated successfully!")
                else:
                    messages.error(
                        request, "This employee doesn't belong to your company!")
            else:
                messages.error(request, "No employee exists with this id!")
        else:
            messages.error(request, "Invalid id!")

        return redirect(f"/employee/{id}/{index}")

    context = {
        "employee": None,
        "index": index
    }
    employee = Employee.objects.filter(id=id)

    if employee.exists():
        employee = employee[0]
        context['employee'] = employee

    return render(request, "profile.html", context)


@login_required
def edit_company_details(request):
    company = get_company_by_admin(request.user)
    if request.method == "POST":
        try:
            name = request.POST['name']
            tagline = request.POST['tagline']
            description = request.POST['description']
            founded_in = request.POST['founded_in']
            error_message = "Kindly provide valid values for all fields!"
            if name:
                company.name = name
            else:
                raise ValueError(error_message)
            if tagline:
                company.tagline = tagline
            else:
                raise ValueError(error_message)
            if description:
                company.description = description
            else:
                raise ValueError(error_message)
            if founded_in:
                company.founded_in = founded_in
            else:
                raise ValueError(error_message)

            if 'template_input' in request.POST and request.POST['template_input']:
                template_id = request.POST['template_input']
                template_query = CardTemplate.objects.filter(id=template_id)
                if template_query.exists():
                    template = template_query[0]
                    company.card_template = template

            company.save()
            messages.info(
                request, "Company information has been updated successfully!")
        except Exception as e:
            messages.error(request, "Provide the valid information!")

        return redirect("edit-company-details")

    context = {
        "name": "edit-company-details"
    }
    context['card_templates'] = CardTemplate.objects.all()
    context['company'] = company
    return render(request, "edit-company-details.html", context)


def buttons(request):
    return render(request, "buttons.html")


def dropdowns(request):
    return render(request, "dropdowns.html")


def typography(request):
    return render(request, "typography.html")


def basic_elements(request):
    return render(request, "basic_elements.html")


def chartjs(request):
    return render(request, "chartjs.html")


def basictable(request):
    return render(request, "basic-table.html")


def icons(request):
    return render(request, "mdi.html")


def login(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        context = {
            'email': email,
            'password': password
        }
        user = auth.authenticate(username=email, password=password)
        if user is not None:
            auth.login(request, user)

            redirection = request.POST['redirection']
            if redirection and len(redirection) > 0:
                return redirect(redirection)
            else:
                return redirect("index")
        else:
            messages.info(request, "Incorrect login details!")
            return render(request, "login.html", context)
            # return redirect("login")
    else:
        return render(request, "login.html")


def register(request):
    return render(request, "register.html")


def error_404(request):
    return render(request, "error-404.html")


def error_500(request):
    return render(request, "error-500.html")


def documentation(request):
    return render(request, "documentation.html")


def profile(request):
    return render(request, "profile.html")
