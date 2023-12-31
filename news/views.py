from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from datetime import datetime
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Author, Subscription, Category
from .filters import PostFilter
from .forms import PostForm
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.views import View






class PostsList(ListView):
    model = Post
    ordering = '-posting_time'  # от более свежей к самой старой
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 3

    def get_context_date(self, **kwargs):  # Позволяет нам получить доп. данные, которые будут переданы в шаблон.
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['next_post'] = "Обновление в пятницу"  # будет выведено содержимое.
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        con = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        con['filterset'] = self.filterset

        return con


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = self.kwargs.get('pk')
        qwe = Category.objects.filter(pk=Post.objects.get(pk=id).category.id).values("subscribers__username")
        context['is_not_subscribe'] = not qwe.filter(subscribers__username=self.request.user).exists()
        context['is_subscribe'] = qwe.filter(subscribers__username=self.request.user).exists()
        return context


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('simpleapp.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('simpleapp.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('simpleapp.delete_post',)
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news_list')

    @login_required
    def new_subscribe(request, **kwargs):
        pk = request.GET.get('pk', )
        print('Пользователь', request.user, 'добавлен в подписчики категории:', Category.objects.get(pk=pk))
        Category.objects.get(pk=pk).subscribers.add(request.user)
        return redirect('/news_list/')

    @login_required
    def non_subscribe(request, **kwargs):
        pk = request.GET.get('pk', )
        print('Пользователь', request.user, 'удален из подписчиков категории:', Category.objects.get(pk=pk))
        Category.objects.get(pk=pk).subscribers.remove(request.user)
        return redirect('/news_list/')


class PostSearch(ListView):
    model = Post
    ordering = '-posting_time'
    template_name = 'post_search.html'
    context_object_name = 'news'
    paginate_by = 2  # количество записей на странице

    # Переопределяем функцию получения списка товаров
    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs  # Возвращаем из функции отфильтрованный список товаров

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset  # Добавляем в контекст объект фильтрации.
        return context


class ArticleCreate(CreateView, PermissionRequiredMixin):
    form_class = PostForm
    model = Post
    permission_required = 'add_news'
    template_name = 'post_edit.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.choice_field = 'article'
        post.author = Author.objects.get(user=self.request.user)
        return super().form_valid(form)

@login_required
@csrf_protect
def subscriptions(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            Subscription.objects.create(user=request.user, category=category)
        elif action == 'unsubscribe':
            Subscription.objects.filter(
                user=request.user,
                category=category,
            ).delete()

    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(
            Subscription.objects.filter(
                user=request.user,
                category=OuterRef('pk'),
            )
        )
    ).order_by('name')
    return render(
        request,
        'subscriptions.html',
        {'categories': categories_with_subscriptions},
    )


from django.http import HttpResponse
from django.views import View
from .tasks import hello, printer
from datetime import datetime, timedelta


class IndexView(View):
    def get(self, request):
        printer.apply_async([10],
                            eta=datetime.now() + timedelta(seconds=5))
        hello.delay()
        return HttpResponse('Hello!')
