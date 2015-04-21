from jinja2 import Environment, FileSystemLoader
from werkzeug.wrappers import Response


class TemplateRenderer(object):
    def __init__(self, template_dir,
                 asset_handler=None, context_processors=None):
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True,
            )
        self.context_processors = context_processors or []

    def render(self, request, template_name, context=None,
               mimetype='text/html'):
        """Request-aware template render."""
        context = context or {}
        for cp in self.context_processors:
            context.update(cp(request))
        return self.render_template(template_name, context, mimetype)

    def render_template(self, template_name, context=None,
                        mimetype='text/html'):
        """
        Render ``template_name`` with ``context`` and ``mimetype``.

        Return as ``Response``.

        """
        tpl = self.jinja_env.get_template(template_name)
        return Response(tpl.render(context or {}), mimetype=mimetype)
