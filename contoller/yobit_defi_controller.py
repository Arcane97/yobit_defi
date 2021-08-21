from view.yobit_defi_view import YobitDefiView


class YobitDefiController:
    def __init__(self, model):
        self._model = model

        self._view = YobitDefiView(self, model)

        self._view.show()
