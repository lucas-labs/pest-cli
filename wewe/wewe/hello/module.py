from pest import module

from .greeter_service import GreeterService
from .hello_controller import HelloController


@module(
    controllers=[HelloController],
    providers=[GreeterService],
)
class HelloModule:
    pass
