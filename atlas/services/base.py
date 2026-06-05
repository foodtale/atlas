from dataclasses import dataclass


@dataclass
class ServiceError:
    message: str
    payload: dict | None = None


class ServiceException(Exception):
    def __init__(
        self,
        message: str,
        payload: dict | None = None,
    ):
        self.error = ServiceError(
            message=message,
            payload=payload,
        )
        super().__init__(message)


class BaseService:
    """
    Base class for application services.

    Usage:

        class CreateOTPService(BaseService):

            def perform(self):
                user = self.context["user"]

                if not user.phone_number:
                    self.fail(
                        message="Phone number missing",
                        payload={
                            "phone_number": [
                                "Required",
                            ],
                        },
                    )

                self.attach(
                    otp_request=otp_request,
                    otp=otp,
                )

    Calling:

        result, error = CreateOTPService.call(
            user=user,
        )

    Accessing context:

        user = self.context["user"]

        # or

        user = self.context.get("user")

    Accessing results:

        if not error:
            otp_request = result["otp_request"]

    Raising errors:

        self.fail(
            message="Invalid OTP",
            payload={
                "otp": [
                    "Invalid OTP",
                ],
            },
        )

    Accessing errors:

        if error:
            error.message
            error.payload

    Notes:

        - Only keyword arguments should be passed to `.call(...)`.
        - Services should implement `perform()`.
        - Inputs are available via `self.context`.
        - Outputs should be attached via `self.attach(...)`.
        - Business errors should be raised via `self.fail(...)`.
    """

    def __init__(self, **context):
        self.context = context
        self.result = {}

    @classmethod
    def call(cls, **context):
        service = cls(**context)

        try:
            service.perform()
            return service.result, None

        except ServiceException as exc:
            return None, exc.error

    def fail(
        self,
        message: str,
        payload: dict | None = None,
    ):
        raise ServiceException(
            message=message,
            payload=payload,
        )

    def perform(self):
        raise NotImplementedError

    def __getattr__(self, name):
        try:
            return self.context[name]
        except KeyError:
            raise AttributeError(name)
