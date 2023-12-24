from pest import Pest

from .app_module import AppModule

app = Pest.create(
    AppModule,
    title='wewe'
)
