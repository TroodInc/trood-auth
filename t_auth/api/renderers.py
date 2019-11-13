from rest_framework.renderers import JSONRenderer


class AuthJsonRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        status = data.pop('response_status', 'OK') if isinstance(data, dict) else 'OK'

        if isinstance(data, dict) and 'data' in data:
            data["status"] = status
        else:
            data = {
                "data": data,
                "status": status
            }

        return super(AuthJsonRenderer, self).render(data, accepted_media_type, renderer_context)
