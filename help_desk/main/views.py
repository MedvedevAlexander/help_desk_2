import os
import re
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import views as auth_views
from django.views.generic import View
from django_sendfile import sendfile

from .models import News, Ticket, File, Comment
from .forms import TicketForm, UploadFileForm, CommentForm, SignupForm, UserAccountForm, UserAccountAdditionalForm
from .services import check_file_download_permissions, check_ticket_view_permissions


def test(request, *args, **kwargs):

    context = {
        'env': os.getenv('DJANGO_SETTINGS_MODULE'),
        'test_env': os.getenv('TEST_ENV')
    }

    return render(request, 'main/test.html', context)


def test_2(request, *args, **kwargs):
    user_1 = User.objects.get(username='user_1')
    user_2 = User.objects.get(username='user_2')
    for i in range(6, 110):
        if i % 2 == 0:
            news = News.objects.create(title=f'Test news {i}',
                                       text=f'This is random text to fill the text field. Create by user {user_1}',
                                       author=user_1)
        else:
            news = News.objects.create(title=f'Test news {i}',
                                       text=f'This is random text to fill the text field. Create by user {user_2}',
                                       author=user_2)

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
            for file in request.FILES.getlist('file'):
                file_obj = File.objects.create(file=file, file_name=file.name, file_size=file.size,
                                               content_object=ticket)
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
    check_ticket_view_permissions(ticket_id, request.user.id)
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


class UserAccountView(View):
    def get(self, request, *args, **kwargs):
        user_form = UserAccountForm
        user_additional_data_form = UserAccountAdditionalForm

        context = {
            'user_form': user_form,
            'user_additional_data_form': user_additional_data_form
        }
        return render(request, 'main/user_account_page.html', context)

    def post(self, request, *args, **kwargs):
        return


@login_required
def check_file_permissions(request, *args, **kwargs):
    check_file_download_permissions(file_link=request.path, user=request.user)
    send = sendfile(request, filename=f'{os.getenv("SENDFILE_ROOT")}{request.path[7:]}', attachment=True)
    return send
