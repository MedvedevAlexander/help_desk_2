import os
import re
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.models import User, Group
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import views as auth_views
from django.views.generic import ListView
from django_sendfile import sendfile
from django.conf import settings
from guardian.shortcuts import assign_perm
from guardian.core import ObjectPermissionChecker
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import View
import magic

from .models import News, Ticket, File, Comment, TicketCategory, TicketPriority
from .forms import TicketForm, UploadFileForm, CommentForm, SignupForm, UserProfileForm, UserProfileAdditionalForm,\
    ProfileAvatarUploadFileForm


def test(request, *args, **kwargs):

    context = {
        'env': os.getenv('DJANGO_SETTINGS_MODULE'),
        'test_env': os.getenv('TEST_ENV')
    }

    return render(request, 'main/test.html', context)


def test_2(request, *args, **kwargs):
    am = User.objects.get(username='am')
    category = TicketCategory.objects.get(id=1)
    priority = TicketPriority.objects.get(id=1)
    for ticket in range(100):
        Ticket.objects.create(title='Тестовый тикет', text='Описание проблемы', author=am, category=category, priority=priority)
    return HttpResponse('OK')


def main_page(request, *args, **kwargs):
    all_news = News.objects.select_related('author').all()
    current_page_number = request.GET.get('page') or 1
    current_page_number = int(current_page_number)
    paginator = Paginator(all_news, 10)
    current_page = paginator.get_page(current_page_number)

    """
    page_range - генератор, содержащий набор номеров страниц, который передается в шаблон для формирования пагинатора.
    Стандартное поле Django paginator.page_range не используется целенаправленно, 
    чтобы избежать излишнего перебора по всему диапазону страниц и 
    необходимости реализации проверки условий в шаблоне (с целью не добавления логики проверки внутрь шаблона).
    В данном случае речь идет о количестве страниц, отображаемых в пагинаторе и проверке того, нужно ли
    отображать страницу из итератора paginator.page_range или нет.
    """
    page_range = (i for i in range(current_page_number - 3, current_page_number + 4)
                 if i >= 1 and i <= paginator.num_pages)

    context = {
        'current_page': current_page,
        'paginator': paginator,
        'current_page_number': current_page_number,
        'page_range': page_range
    }
    return render(request, 'main/index.html', context)


@login_required
def create_ticket(request, *args, **kwargs):
    if request.method == 'POST':
        ticket_form_data = {
            'text': request.POST['text'],
            'title': request.POST['title'],
            'category': request.POST['category'],
            'priority': request.POST['priority'],
            'author': User.objects.get(username=request.user)
        }
        form = TicketForm(ticket_form_data)
        if form.is_valid():
            ticket = form.save()
            assign_perm(perm='view_ticket', user_or_group=request.user, obj=ticket)
            try:
                assign_perm(perm='view_ticket', user_or_group=Group.objects.
                            get(name=f'{ticket.category.codename}_admins'), obj=ticket)
            except Group.DoesNotExist as e:
                url = reverse('main:http_500')
                return HttpResponseRedirect(url)
            for file in request.FILES.getlist('file'):
                file_obj = File.objects.create(file=file, file_name=file.name, file_size=file.size,
                                               content_object=ticket)
                assign_perm(perm='view_file', user_or_group=request.user, obj=file_obj)
                try:
                    assign_perm(perm='view_file',
                                user_or_group=Group.objects.get(name=f'{ticket.category.codename}_admins'),
                                obj=file_obj)
                except Group.DoesNotExist as e:
                    url = reverse('main:http_500')
                    return HttpResponseRedirect(url)
            url = reverse('main:show_ticket', args=[ticket.id])
            return HttpResponseRedirect(url)

    else:
        form = TicketForm()
        file_form = UploadFileForm()

    context = {
        'form': form,
        'file_form': file_form
    }
    return render(request, 'main/add_ticket.html', context)


class HelpDeskLoginView(auth_views.LoginView):
    template_name = 'main/signin.html'


class HelpDeskLogoutView(auth_views.LogoutView):
    pass


@login_required
def show_ticket(request, *args, **kwargs):
    ticket_id = kwargs['ticket_id']
    ticket_obj = get_object_or_404(Ticket.objects.select_related('author', 'category', 'priority', 'status').
                                   prefetch_related('files'), pk=ticket_id)
    perm_checker = ObjectPermissionChecker(request.user)
    if not perm_checker.has_perm('view_ticket', ticket_obj):
        raise PermissionDenied
    comments = Comment.objects.select_related('user').prefetch_related('files').filter(ticket=ticket_obj)

    if request.method == 'POST':
        comment_form_data = {
            'text': request.POST['text'],
            'ticket': ticket_id,
            'user': request.user
        }
        comment_form = CommentForm(comment_form_data)
        if comment_form.is_valid():
            comment = comment_form.save()
            for file in request.FILES.getlist('file'):
                file_obj = File.objects.create(file=file, file_name=file.name, file_size=file.size,
                                               content_object=comment)
                if request.user.id != ticket_obj.author.id:
                    assign_perm(perm='view_file', user_or_group=User.objects.get(id=ticket_obj.author.id), obj=file_obj)
                try:
                    assign_perm(perm='view_file',
                                user_or_group=Group.objects.get(name=f'{ticket_obj.category.codename}_admins'),
                                obj=file_obj)
                except Group.DoesNotExist as e:
                    url = reverse('main:http_500')
                    return HttpResponseRedirect(url)
        url = reverse('main:show_ticket', args=[kwargs['ticket_id']])
        return HttpResponseRedirect(url)
    else:
        comment_form = CommentForm()
        file_form = UploadFileForm()

        context = {
            'ticket': ticket_obj,
            'comment_form': comment_form,
            'file_form': file_form,
            'comments': comments
        }
    return render(request, 'main/show_ticket.html', context)


def signup_page(request, *args, **kwargs):
    if request.method == 'POST':
        signup_form = SignupForm(request.POST)
        if signup_form.is_valid():
            user = signup_form.save()
            url = '/'
            return HttpResponseRedirect(url)
    else:
        signup_form = SignupForm()

    context = {
        'signup_form': signup_form
    }
    return render(request, 'main/signup_page.html', context=context)


class UserAccountView(LoginRequiredMixin, ListView):
    template_name = 'main/user_account_page.html'
    context_object_name = 'last_tickets'

    def dispatch(self, request, *args, **kwargs):
        if kwargs['pk'] != request.user.id and request.user.is_authenticated:
            raise PermissionDenied
        return super(UserAccountView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        pr1 = Prefetch('comment_ticket', queryset=Comment.objects.order_by('-added_at'))
        queryset = Ticket.objects.select_related('category', 'priority', 'status', 'author').prefetch_related(pr1).filter(author=self.request.user.id)[:5]
        return queryset


class UserAccountTicketsListView(LoginRequiredMixin, ListView):
    template_name = 'main/user_account_page_tickets_list.html'
    context_object_name = 'all_tickets'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        # check access rights to the page
        if kwargs['pk'] != request.user.id and request.user.is_authenticated:
            raise PermissionDenied
        return super(UserAccountTicketsListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        pr1 = Prefetch('comment_ticket', queryset=Comment.objects.order_by('-added_at'))
        queryset = Ticket.objects.select_related('category', 'priority', 'status', 'author').prefetch_related(pr1).filter(author=self.request.user.id)
        return queryset


class UserAccountProfileInfoEditView(LoginRequiredMixin, View):
    template_name = 'main/user_account_page_profile_info.html'

    def dispatch(self, request, *args, **kwargs):
        self.user_obj = User.objects.select_related('user_profile').get(id=kwargs['pk'])
        # check access rigths to the page
        if kwargs['pk'] != request.user.id and request.user.is_authenticated:
            raise PermissionDenied
        return super(UserAccountProfileInfoEditView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {
            'user_form': UserProfileForm(instance=self.user_obj),
            'user_profile_form': UserProfileAdditionalForm(instance=self.user_obj.user_profile),
            'user_avatar_form': ProfileAvatarUploadFileForm(),
            'user_obj': self.user_obj
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # check that email, username fields have not been changed by user
        user_form_data = {
            'username': self.user_obj.username,
            'first_name': request.POST['first_name'],
            'last_name': request.POST['last_name'],
            'email': self.user_obj.email
        }
        user_form = UserProfileForm(user_form_data, instance=self.user_obj)
        user_profile_form = UserProfileAdditionalForm(request.POST, instance=self.user_obj.user_profile)
        if user_form.has_changed() or user_profile_form.has_changed():
            if user_form.is_valid() and user_profile_form.is_valid():
                user_form.save(user_form_data)
                user_profile_form.save()
        if request.FILES:
            user_avatar_form = ProfileAvatarUploadFileForm(files=request.FILES)
            if user_avatar_form.is_valid():
                user_avatar_form.save(avatar=request.FILES['file'], user=self.user_obj)
        else:
            user_avatar_form = ProfileAvatarUploadFileForm()

        if user_form.errors or user_profile_form.errors or user_avatar_form.errors:
            context = {
                'user_form': user_form,
                'user_profile_form': user_profile_form,
                'user_avatar_form': user_avatar_form,
                'user_obj': self.user_obj
            }
            return render(request, self.template_name, context)

        url = reverse('main:user_account_profile_info', kwargs={'pk': kwargs['pk']})
        return HttpResponseRedirect(url)


@login_required
def check_file_permissions(request, *args, **kwargs):
    """
    Check what type of file is requested:
    - if a user avatar is requested (e.g. /media/user_profile/), we do not check access rights
    - otherwise we check the file permissions
    """
    if not re.search(pattern=r'^media\/user_profile\/', string=request.path):
        perm_checker = ObjectPermissionChecker(request.user)
        file_obj = get_object_or_404(File, file=request.path[7:])
        if not perm_checker.has_perm('view_file', file_obj):
            raise PermissionDenied
    send = sendfile(request, filename=f'{os.getenv("SENDFILE_ROOT")}{request.path[7:]}', attachment=True)
    return send


def http_response_server_error(request, *args, **kwargs):

    return render(request, '500.html', status=500)
