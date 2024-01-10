from .logger import logger
from .maps import property_map, field_map
from .records import Record

from cached_property import cached_property


class UserSettings(Record):
    _table = "user_settings"

    type = field_map("settings.type")
    persona = field_map("settings.persona")
    team_role = field_map("settings.team_role")

    time_zone = field_map("settings.time_zone")
    signup_time = field_map("settings.signup_time")

    preferred_locale = field_map("settings.preferred_locale")
    preferred_locale_origin = field_map("settings.preferred_locale_origin")

    cookie_consent = field_map("settings.cookie_consent")


class User(Record):
    _table = "notion_user"

    given_name = field_map("given_name")
    family_name = field_map("family_name")

    name = field_map("name")
    email = field_map("email")
    profile_photo = field_map("profile_photo")

    @property
    def full_name(self):
        return " ".join([self.given_name or "", self.family_name or ""]).strip()

    @cached_property
    def settings(self):
        return UserSettings(self._client, self.id)

    def _str_fields(self):
        return super()._str_fields() + ["email", "name"]

    def refresh(self):
        self.settings.refresh()
        super().refresh()
