from django import template

register = template.Library()


@register.simple_tag
def pagelink(request, value):
    d = request.GET.copy()
    d['p'] = value
    return "?%s" % d.urlencode()