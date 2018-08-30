import pytest


@pytest.fixture(autouse=True)
def disabled_user_profile_data_url_setting(settings):
    settings.USER_PROFILE_DATA_URL = None


@pytest.fixture(autouse=True)
def disabled_default_account_role_id_setting(settings):
    settings.DEFAULT_ACCOUNT_ROLE_ID = None
