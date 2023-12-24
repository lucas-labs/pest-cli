from pest import controller, get

from .greeter_service import Greet, GreeterService


@controller("/")
class HelloController:
    """say hello routes"""

    service: GreeterService  # 💉 injected

    @get("/")
    def say_hello(self) -> Greet:
        """Say hello"""

        return self.service.say_hello()
