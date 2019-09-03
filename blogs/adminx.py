from django.urls import reverse
from django.utils.html import format_html

import xadmin
from xadmin.layout import Row, Fieldset, Container

from .models import Category, Tag, Post, Comment, SideBar, Link
from .forms import PostAdminForm
from .excel2model import excel_into_model,excel_into_obj_list
from xlrd import open_workbook
from django.shortcuts import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt


class BaseOwnerAdmin:
    """
    1. 用来处理文章、分类、标签、侧边栏、友链这些model的owner字段自动补充
    2. 用来针对queryset过滤当前用户的数据
    """
    exclude = ('owner',)

    def get_list_queryset(self):
        request = self.request
        qs = super().get_list_queryset()
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def save_models(self):
        self.new_obj.owner = self.request.user
        return super().save_models()

# from  xadmin.plugins.chart import ChartsPlugin
# from xadmin.plugins.actions import BaseActionView
@xadmin.sites.register(Category)
class CategoryAdmin(BaseOwnerAdmin):
    # inlines = [PostInline, ]
    list_display = ('name', 'status', 'is_nav', 'created_time', 'post_count')
    fields = ('name', 'status', 'is_nav')
    # data_charts ={
    #     'user_count': {'title': u"User Report", "x-field": "created_time", "y-field": ("post_count"), "order": ('created_time',)},
    # }
    import_excel = True

    def post_count(self, obj):
        return obj.post_set.count()

    post_count.short_description = '文章数量'

    # 定义重载post方法来获取excel表格中的数据
    def post(self, request, *args, **kwargs):
        if 'excel' in request.FILES:
            execl_file = request.FILES.get('excel')
            files = open_workbook(filename=None, file_contents=request.FILES['excel'].read())
            obj_list = excel_into_obj_list('blog', 'Category', excel_file=files)
            for obj in obj_list:
                obj.owner = request.user
            Category.objects.bulk_create(obj_list)
            return HttpResponseRedirect('/admin/blog/category')
        return super(BaseOwnerAdmin,self).post(request, *args, **kwargs)


@xadmin.sites.register(Tag)
class TagAdmin(BaseOwnerAdmin):
    list_display = ('name', 'status', 'created_time')
    fields = ('name', 'status')


@xadmin.sites.register(Post)
class PostAdmin(BaseOwnerAdmin):
    form = PostAdminForm
    list_display = [
        'title', 'category', 'status',
        'created_time', 'owner', 'operator'
    ]
    list_display_links = []

    list_filter = ['category', ]
    search_fields = ['title', 'category__name']
    save_on_top = True

    actions_on_top = True
    actions_on_bottom = True

    # 编辑页面
    # save_on_top = True

    exclude = ['owner']
    form_layout = (
        Fieldset(
            '基础信息',
            Row("title", "status"),
            'category',
            'tag',
        ),
        Fieldset(
            '内容信息',
            'desc',
            'is_md',
            'content_ck',
            'content_md',
            'content',
        )
    )

    def operator(self, obj):
        return format_html(
            '<a href="{}">编辑</a>',
            reverse('xadmin:blog_post_change', args=(obj.id,))
        )

    operator.short_description = '操作'


@xadmin.sites.register(Comment)
class CommentAdmin:
    list_display = ('target', 'nickname', 'content', 'created_time')


@xadmin.sites.register(Link)
class LinkAdmin(BaseOwnerAdmin):
    list_display = ('title', 'href', 'status', 'weight', 'created_time')
    fields = ('title', 'href', 'status', 'weight')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(LinkAdmin, self).save_model(request, obj, form, change)


@xadmin.sites.register(SideBar)
class SideBarAdmin(BaseOwnerAdmin):
    list_display = ('title', 'display_type', 'content', 'created_time')
    fields = ('title', 'display_type', 'content')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(SideBarAdmin, self).save_model(request, obj, form, change)



from xadmin.views import BaseAdminPlugin, ListAdminView
from django.template import loader
from xadmin.plugins.utils import get_context_dict

# excel 导入
class ListImportExcelPlugin(BaseAdminPlugin):
    import_excel = False

    def init_request(self, *args, **kwargs):
        return bool(self.import_excel)

    def block_top_toolbar(self, context, nodes):
        context = get_context_dict(context or {})
        nodes.append(
            loader.render_to_string('xadmin/excel/model_list.top_toolbar.import.html',context=context))


xadmin.site.register_plugin(ListImportExcelPlugin, ListAdminView)