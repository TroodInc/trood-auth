from django.conf import settings

from trood.contrib.django.auth.engine import TroodABACEngine, TroodABACResolver


class AuthABACEngine(TroodABACEngine):
    def check_permited(self, request, view):
        try:
            rules = self.rules[settings.SERVICE_DOMAIN][view.basename][view.action]
            resolver = AuthABACResolver(subject=request.user, context=request.data)
            for rule in rules:
                result, filters = resolver.evaluate_rule(rule)
                if result:
                    self.filters = filters
                    return True

        except KeyError:
            return True

        return False


class AuthABACResolver(TroodABACResolver):

    def evaluate_rule(self, rule: dict):
        result, filters = super().evaluate_rule(rule)
        if rule['result'] == 'deny':
            result = not result

        return result, filters
