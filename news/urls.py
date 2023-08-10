from django.urls import path
from .views import PostsList, PostDetail, PostCreate, PostUpdate, PostDelete, PostSearch, ArticleCreate
from django.urls import path
from .views import IndexView
from django.views.decorators.cache import cache_page


urlpatterns = [
    path('', cache_page(60*1)(NewsList.as_view())),
    path('<int:pk>/', cache_page(60*10)(NewsDetailView.as_view()), name='news_detail'),
    path('', PostsList.as_view(), name='news_list'),
    path('<int:pk>', PostDetail.as_view(), name='post_detail'),
    # Добавим создание(статьи и новости отдельно), редактирование и удаление объектов
    path('create/', PostCreate.as_view(), name='post_create'),
    path('articles/create/', ArticleCreate.as_view(), name='article_create'),
    path('<int:pk>/update/', PostUpdate.as_view(), name='post_update'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('search/', PostSearch.as_view(), name='post_search'),

    path('', IndexView.as_view()),
]