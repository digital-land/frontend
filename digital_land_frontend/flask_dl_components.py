from jinja2 import PackageLoader, PrefixLoader, ChoiceLoader


class DLComponents:
    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        multi_loader = ChoiceLoader(
            [
                app.jinja_loader,
                PrefixLoader(
                    {"digital-land-frontend": PackageLoader("digital_land_frontend")}
                ),
            ]
        )
        app.jinja_loader = multi_loader