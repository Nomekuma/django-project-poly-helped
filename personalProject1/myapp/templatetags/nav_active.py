from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, name_or_path):
    """Return 'active' when the current request matches the given url name or path prefix.

    Usage examples in templates:
      {% load nav_active %}
      <a href="{% url 'home' %}" class="nav-link {% active 'home' %}">Home</a>
      <a href="/pages/about/" class="nav-link {% active '/pages/about/' %}">About</a>
    """
    request = context.get("request")
    if not request:
        return ""
    try:
        s = str(name_or_path)
        if s.startswith("/"):
            return "active" if request.path.startswith(s) else ""
        resolver = getattr(request, "resolver_match", None)
        if resolver and resolver.url_name == s:
            return "active"
    except Exception:
        pass
    return ""
