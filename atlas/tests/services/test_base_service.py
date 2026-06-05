import pytest

from atlas.services.base import BaseService, ServiceException, ServiceError


class SuccessService(BaseService):
    def perform(self):
        self.result["value"] = self.context["input"] * 2


class FailingService(BaseService):
    def perform(self):
        self.fail(message="Something went wrong.", payload={"field": ["error"]})


class FailingServiceNoPayload(BaseService):
    def perform(self):
        self.fail(message="bare error")


def test_successful_call_returns_result():
    result, error = SuccessService.call(input=5)

    assert error is None
    assert result["value"] == 10


def test_successful_call_error_is_none():
    _, error = SuccessService.call(input=1)

    assert error is None


def test_failing_call_returns_none_result():
    result, error = FailingService.call()

    assert result is None


def test_failing_call_returns_service_error():
    _, error = FailingService.call()

    assert isinstance(error, ServiceError)
    assert error.message == "Something went wrong."
    assert error.payload == {"field": ["error"]}


def test_failing_call_without_payload():
    _, error = FailingServiceNoPayload.call()

    assert error.message == "bare error"
    assert error.payload is None


def test_context_accessible_via_attribute():
    service = SuccessService(input=42)

    assert service.input == 42


def test_missing_context_attribute_raises_attribute_error():
    service = SuccessService(input=1)

    with pytest.raises(AttributeError):
        _ = service.nonexistent


def test_perform_not_implemented_on_base():
    service = BaseService()

    with pytest.raises(NotImplementedError):
        service.perform()


def test_service_exception_carries_error():
    exc = ServiceException(message="oops", payload={"x": [1]})

    assert exc.error.message == "oops"
    assert exc.error.payload == {"x": [1]}
