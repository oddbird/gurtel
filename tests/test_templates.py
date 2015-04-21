import os

from pretend import stub
import pytest

from gurtel import templates


@pytest.fixture
def tpl(request, testapp_base_dir):
    kwargs = {}
    if 'tpl_kwargs' in request.keywords:
        kwargs = request.keywords['tpl_kwargs'].args[0]
    return templates.TemplateRenderer(
        template_dir=os.path.join(testapp_base_dir, 'templates'),
        **kwargs)


class TestTemplateRenderer(object):
    def test_render_custom_mime_type(self, tpl):
        """Render can take a custom mime type."""
        resp = tpl.render(None, 'text.txt', mimetype='text/plain')

        assert resp.mimetype == 'text/plain'

    def test_render_template_custom_mime_type(self, tpl):
        """Render template can take a custom mime type."""
        resp = tpl.render_template('text.txt', mimetype='text/plain')

        assert resp.mimetype == 'text/plain'

    @pytest.mark.tpl_kwargs(
        {'context_processors': [lambda req: {'flash': req.flash_messages}]})
    def test_context_processor(self, tpl):
        """Updates template context with dicts returned from context procs."""
        req = stub(flash_messages=[{'message': 'yay for you.'}])
        resp = tpl.render(req, 'flash.html')

        assert resp.data == '\n  yay for you.\n'
