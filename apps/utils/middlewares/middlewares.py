from utils.middlewares.language import LanguageMiddleware


def init_middlewares(app):
    app.add_middleware(LanguageMiddleware)
