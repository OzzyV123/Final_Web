from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import *
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q

from .forms import *
from .models import *


class PostList(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created_at')  # сортировка по дате
        search_query = self.request.GET.get('q', '')

        if search_query:
            queryset = queryset.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
        return queryset

class PostDetail(DetailView):
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'
    model = Post

class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        files = self.request.FILES.getlist('media_files')
        for f in files:
            PostMedia.objects.create(post=self.object, file=f)

        return response

    def get_success_url(self):
        return reverse('news:post_detail', kwargs={'pk': self.object.pk})


class PostUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'category']
    template_name = 'posts/post_form.html'

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse('news:post_detail', kwargs={'pk': self.object.pk})

class MyCommentsList(ListView):
    model = Comments
    template_name = 'posts/my_comments.html'
    context_object_name = 'comments'

    def get_queryset(self):
        queryset = Comments.objects.filter(post__author=self.request.user)

        post_id = self.request.GET.get('post')
        status = self.request.GET.get('status')

        if post_id:
            queryset = queryset.filter(post_id=post_id)

        if status == 'accepted':
            queryset = queryset.filter(is_accepted=True)
        elif status == 'pending':
            queryset = queryset.filter(is_accepted=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Список всех постов пользователя для фильтрации в шаблоне
        context['my_posts'] = self.request.user.posts.all()
        return context

@login_required
def accept_comment(request, pk):
    comment = get_object_or_404(Comments, pk=pk)
    if comment.post.author != request.user:
        return HttpResponseForbidden()
    comment.is_accepted = True
    comment.save()
    send_mail(
        subject=f"Ваш отклик принят на '{comment.post.title}'",
        message=f"Привет, {comment.author.username}!\n\n"
                f"Ваш отклик на объявление '{comment.post.title}' был принят.\n\n"
                f"Текст отклика:\n{comment.content}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[comment.author.email],
        fail_silently=False,
    )
    return redirect('news:my_comments')

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comments, pk=pk)
    if comment.post.author != request.user:
        return HttpResponseForbidden()
    comment.delete()
    return redirect('news:my_comments')


class CommentCreate(LoginRequiredMixin, CreateView):
    model = Comments
    form_class = CommentForm
    template_name = 'posts/comment_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = Post.objects.get(pk=self.kwargs['pk'])

        try:
            response = super().form_valid(form)
        except IntegrityError:
            messages.error(self.request, "Такой отклик уже существует для этого объявления.")
            return redirect('news:post_detail', pk=self.kwargs['pk'])

        # Отправка e-mail автору поста
        post_author_email = form.instance.post.author.email
        if post_author_email:  # проверяем, что email есть
            send_mail(
                subject=f"Новый отклик на ваше объявление '{form.instance.post.title}'",
                message=f"Привет, {form.instance.post.author.username}!\n\n"
                        f"Пользователь {form.instance.author.username} оставил новый отклик на ваше объявление:\n\n"
                        f"{form.instance.content}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[post_author_email],
                fail_silently=False,
            )

        return response

    def get_success_url(self):
        return reverse('news:post_detail', kwargs={'pk': self.kwargs['pk']})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                is_active=False
            )

            confirmation = EmailConfirmation.objects.create(user=user)

            send_mail(
                subject='Подтверждение регистрации',
                message=f'Код подтверждения: {confirmation.code}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

            return redirect('news:confirm_email')
    else:
        form = RegisterForm()

    return render(request, 'posts/register.html', {'form': form})


def confirm_email_view(request):
    if request.method == 'POST':
        code = request.POST.get('code')

        try:
            confirmation = EmailConfirmation.objects.get(code=code)
        except EmailConfirmation.DoesNotExist:
            return render(
                request,
                'posts/confirm_email.html',
                {'error': 'Неверный код'}
            )

        user = confirmation.user
        user.is_active = True
        user.save()

        confirmation.delete()

        return redirect('news:login')

    return render(request, 'posts/confirm_email.html')

