from rest_framework.renderers import JSONRenderer


class AuthJsonRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data and isinstance(data, list) or (isinstance(data, dict) and not data.get('status') == 'FAIL'):
            data = {
                'status': 'OK',
                'data': data
            }
        return super(AuthJsonRenderer, self).render(data, accepted_media_type, renderer_context)
