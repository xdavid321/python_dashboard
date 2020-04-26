from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.forms import forms, ValidationError
from django.forms.utils import ErrorList
import django.shortcuts as shortcuts

from django.views.generic.edit import FormView
from .forms import DataSheetUpload, LoginForm
from .functions import handle_uploaded_file, handle_user_auth, fetch_data, fetch_users, update_user_markets, update_user_password, handle_delete_user, handle_add_user, handle_my_password_update

ACCESS_ROLES = {
    'super': ["upload", "manage", "view"],
}

# Create your views here.
def index(request):
    if not request.session.has_key("user_name"):
        return HttpResponseRedirect('/login')
    template = loader.get_template('index.html')
    return HttpResponse(template.render({}, request))


def super_user(request):
    if not request.session.has_key("user_name"):
        return HttpResponseRedirect('/login')
    template = loader.get_template('superuser.html')
    return HttpResponse(template.render({}, request))

def manage_users(request):
    if not request.session.has_key("user_name") or  request.session["user_type"] != 'super':
        return HttpResponseRedirect('/login')

    context = {
        'users': fetch_users(request.session["user_name"])
    }
    print(context)
    
    template = loader.get_template('manageUser.html')
    return HttpResponse(template.render(context, request))

def view_data(request):
    if not request.session.has_key('user_name'):
        return HttpResponseRedirect('/login')
    if ( request.session["user_market"] != "" and request.session["user_market"] != None ) and request.session["user_type"] == "external":
        market = request.session["user_market"]
    else:
        market = None
    week = request.GET.get('week')
    headers, data = fetch_data(market, week)
    template = loader.get_template('viewData.html')

    return HttpResponse(template.render({
        'table_data': {
            'headers': headers,
            'data': data
        }
    }, request))

def assign_market(request):
    data = request.POST.copy()
    user_id = data.get('user_id')
    markets = data.get('markets')
    print(user_id, markets)
    update_user_markets(user_id=user_id, markets= markets)
    return HttpResponseRedirect('/admin/users')

def change_user_password(request):
    data = request.POST.copy()
    user_id = data.get('user_id')
    password = data.get('password')
    update_user_password(user_id=user_id, password=password)
    return HttpResponseRedirect('/admin/users')

def change_my_password(request):
    if request.method == 'GET':
        template = loader.get_template('changeMyPassword.html')
        return HttpResponse(template.render({}, request))
    if request.method == 'POST':
        data = request.POST.copy()
        user_id = request.session["user_name"]
        password = data.get('password_new')
        password_old = data.get('password_old')
        changed = handle_my_password_update(user_id=user_id, password_new=password, password_old=password_old)
        template = loader.get_template('changeMyPassword.html')
        context = { }
        if changed == True:
            context['password_changed'] = 'Y'
        if changed == False:
            context['password_changed'] = 'N'
        return HttpResponse(template.render(context, request))

def delete_user(request):
    data = request.POST.copy()
    user_id = data.get('user_id')
    handle_delete_user(user_id=user_id)
    return HttpResponseRedirect('/admin/users')

def add_user(request):
    data = request.POST.copy()
    user_id = data.get('user_id')
    user_type = data.get('user_type')
    market = data.get('market')
    if data.get('market') == None:
        market = ''
    password = data.get('password')
    handle_add_user(user_id=user_id, user_type=user_type, market=market, password=password)
    # handle_delete_user(user_id=user_id)
    return HttpResponseRedirect('/admin/users')

def user_logout(request):
    request.session.flush()
    return HttpResponseRedirect('/')

class AuthView(FormView):
    form_class = LoginForm
    template_name = 'login.html'
    success_url = "/"

    def get(self, request, *args, **kwargs):
        if(request.session.has_key('user_name')):
            return HttpResponseRedirect('/')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        user_name = form.cleaned_data["user_name"]
        password = form.cleaned_data["password"]
        response = handle_user_auth(user_name, password)
        if response["status"] == False:
            if response["message"] == "NOT_FOUND":
                response["message"] = "User not found"
            elif response["message"] == "WRONG_PASSWORD":
                response["message"] = "Invalid password"
            form._errors[forms.NON_FIELD_ERRORS] = ErrorList([
                response["message"]
            ])
            return self.form_invalid(form)
        else:
            self.request.session["user_name"] = user_name
            self.request.session["user_type"] = response["user_type"]
            self.request.session["user_market"] = response["market"]

            return HttpResponseRedirect('/')

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class DataSheetView(FormView):
    form_class = DataSheetUpload
    template_name = 'upload.html'


    def get(self, request, *args, **kwargs):
        required_access = "upload"
        if not request.session.has_key("user_name"):
            return HttpResponseRedirect('/')
        if request.session["user_type"] != "super":
            return HttpResponseRedirect('/')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        print("in form valid")
        context = {
            'file_data': self.extra_context
        }
        return render(self.request, 'uploadResult.html', context)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('datasheet')
        
        if form.is_valid():
            headerCols = form.cleaned_data["headerColumns"]
            view_context = []
            for f in files:
                context = handle_uploaded_file(f, headerCols = headerCols)
                context["file-name"] = f.name
                view_context.append(context)
            self.extra_context = view_context
            return self.form_valid(form)
        else:
            return self.form_invalid(form)