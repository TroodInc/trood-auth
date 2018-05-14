from rest_framework.renderers import JSONRenderer


class AuthJsonRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        status = 'OK'
        if 'response_status' in data:
            status = data.pop('response_status')

        res_data = {
            'status': status,
            'data': data
        }
        return super(AuthJsonRenderer, self).render(res_data, accepted_media_type, renderer_context)
