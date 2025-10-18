from uuid import UUID

from .user_preference_service import UserPreferenceService
from ...schemas.user import UserPreferencesRequest


def build_request(**overrides):
    base = dict(
        email="user@example.com",
        diet_id="balanced",
        culture_id="indian",
        additional_cultures=["ethiopian"],
        country="germany",
        city="Berlin",
        dietary_goals=["healthy_eating", "time_saving"],
        allergies=["nuts"],
        disliked_ingredients=["eggplant"],
        meals_per_day=3,
        household_size=2,
        cooking_time_limit=30,
    )
    base.update(overrides)
    return UserPreferencesRequest(**base)


def test_save_preferences_returns_workflow_identifier() -> None:
    service = UserPreferenceService()
    request = build_request()

    response = service.save_preferences(request)

    assert response.status == "accepted"
    assert response.message.startswith("Preferences saved")
    assert isinstance(response.workflow_id, UUID)

    stored = service.get_preferences(request.email)
    assert stored is not None
    assert stored.culture_id == "indian"
    assert stored.additional_cultures == ["ethiopian"]


def test_save_preferences_deduplicates_lists() -> None:
    service = UserPreferenceService()
    request = build_request(
        dietary_goals=["healthy_eating", "healthy_eating"],
        allergies=["nuts", "nuts"],
        disliked_ingredients=["eggplant", "eggplant"],
        additional_cultures=["ethiopian", "ethiopian"],
    )

    service.save_preferences(request)
    stored = service.get_preferences(request.email)

    assert stored is not None
    assert stored.dietary_goals == ["healthy_eating"]
    assert stored.allergies == ["nuts"]
    assert stored.disliked_ingredients == ["eggplant"]
    assert stored.additional_cultures == ["ethiopian"]


def test_get_preferences_returns_none_when_unknown() -> None:
    service = UserPreferenceService()

    assert service.get_preferences("missing@example.com") is None
