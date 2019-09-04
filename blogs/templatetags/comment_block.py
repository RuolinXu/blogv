from django import template

from blog.forms import CommentForm
from blog.models import Comment

register = template.Library()


@register.inclusion_tag('blog/comment_block.html')
def comment_block(target):
    return {
        'target': target,
        'comment_form': CommentForm(),
        'comment_list': Comment.get_by_target(target),
    }
