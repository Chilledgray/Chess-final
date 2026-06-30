from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window


class Menu(RelativeLayout):

    def on_touch_down(self, touch):
        if self.opacity == 0:
            return False
        return super(RelativeLayout, self).on_touch_down(touch)

    pass
