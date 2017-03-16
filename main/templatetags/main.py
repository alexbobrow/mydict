from django import template

register = template.Library()


@register.simple_tag
def pagelink(request, value):
    d = request.GET.copy()
    d['p'] = value
    return "?%s" % d.urlencode()


@register.filter
def sensible(user):
	fn = user.get_full_name()
	if not fn:
		return "Пользователь №%s" % user.pk
	else:
		return fn

