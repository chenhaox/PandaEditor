import random
import panda3d.core as p3dCore
import direct.gui.DirectGui as gui
from editor.core import RuntimeModule
from editor.utils import EdProperty


class Component(RuntimeModule, p3dCore.NodePath):
    def __init__(self, *args, **kwargs):
        RuntimeModule.__init__(self, *args, **kwargs)

    def __attach__(self, np):
        p3dCore.NodePath.__init__(self, np)

    def __detach__(self):
        pass


class Basics(RuntimeModule):
    def __init__(self, *args, **kwargs):
        """__init__ should not be used for anything except for variable declaration"""

        RuntimeModule.__init__(self, *args, **kwargs)

        # create some properties that will be displayed in inspector
        # properties of these types are laid out automatically by the editor
        self.int_property = 5
        self.float_property = 7.5
        self.str_property = "Panda3d"
        self.bool_property = False
        self.vector3 = p3dCore.LVecBase3f(10, 17, 28)
        self.vector2 = p3dCore.LVecBase2f(25, 46)
        self.__color = p3dCore.LColor(1, 1, 1, 1)  # private attributes are not visible in inspector

        # Custom properties --------------------------------------------------------------------
        # empty space property
        self.add_property(EdProperty.EmptySpace(0, 5))

        # label property
        self.add_property(EdProperty.Label(name="Custom Properties", is_bold=True))

        # button property
        self.add_property(EdProperty.ButtonProperty(name="ButtonProperty", func=self.on_button))

        # slider property
        self.__temperature = 5

        self.add_property(EdProperty.Slider(name="Slider",
                                            value=self.__temperature,  # initial value
                                            min_value=0,
                                            max_value=10,
                                            setter=self.set_temperature,
                                            getter=lambda: self.__temperature,
                                            ))

        # choice property
        self.__curr_choice = 0

        choices = ["Apple", "PineApple", "BigApple", "Blueberry"]
        self.add_property(EdProperty.ChoiceProperty(name="Choice",
                                                    choices=choices,
                                                    value=self.__curr_choice,  # initial value
                                                    setter=self.set_choice,
                                                    getter=lambda: self.__curr_choice))

        # color property
        self.add_property(EdProperty.FuncProperty(name="Color_picker",
                                                  value=self.__color,
                                                  setter=self.set_color,
                                                  getter=self.get_color))

        # --------------------------------------------------------------------
        # horizontal layout group property
        self.toggle = True

        properties = [EdProperty.Label(name="HorizontalGroup: ", is_bold=True),
                      EdProperty.ObjProperty(name="vector2", value=self.vector2, obj=self),
                      EdProperty.ObjProperty(name="toggle", value=self.toggle, obj=self)]

        horizontal_layout_group = EdProperty.HorizontalLayoutGroup(name="HLayoutGroup", properties=properties)
        self.add_property(horizontal_layout_group)

        # --------------------------------------------------------------------
        # vertical layout group or foldout group property

        self.__integer = 45
        self.__boolean = False
        self.__vector = p3dCore.LVecBase3f(5, 10, 15)

        properties = [EdProperty.ObjProperty(name="_Basics__integer", value=self.__integer, obj=self),
                      EdProperty.ObjProperty(name="_Basics__boolean", value=self.__boolean, obj=self),
                      EdProperty.ObjProperty(name="_Basics__vector", value=self.__vector, obj=self)]
        foldout_group = EdProperty.FoldoutGroup(properties=properties)
        self.add_property(foldout_group)

        # you can also hide attributes in the inspector
        # hide these attributes
        self.hidden_attrs = "bool_a"
        self.hidden_attrs = "bool_b"

    def on_start(self):
        """on_start method is called only once"""

        # -------------------------------------------------------------------- #
        # attributes defined in Runtime module, they act as bridge between PandaEditor and Panda3d engine
        # self._win                : the window we are rendering into currently
        # self.mouse_watcher_node  : mouse watcher node
        # self.render              : this is the current scene's parent node-path
        # self.game                : instance of current running game
        # -------------------------------------------------------------------- #

        # basic scene graph operations
        np = self.render.find("**/cube.fbx")
        camera_np = self.render.find("**/Camera")

        # get reference to other runtime modules
        test_module = self.game.get_module("TestModule")
        if test_module is not None:
            test_module.foo()  # foo is a method defined TestModule

        # creating direct gui elements
        self.create_ui()

        # basic event handling
        self.accept("a", self.on_key_down, ["a"])
        self.accept("a-up", self.on_key_up, ["a"])

    def create_ui(self):
        b = gui.DirectButton(text=("OK", "click!", "rolling over", "disabled"), scale=.2,
                             command=self.on_direct_gui_btn_press)
        b.setPos((0, 0, 0))
        b.reparent_to(self.aspect2d)

    def on_update(self):
        """update method is called every frame"""
        pass

    def on_late_update(self):
        """on late update is called after update"""
        pass

    def on_key_down(self, key: str):
        print("[Basics.py] event key down {0}".format(key))

    def on_key_up(self, key: str):
        print("[Basics.py] event key up {0}".format(key))

    def on_direct_gui_btn_press(self):
        print("[Basics.py] Direct gui button pressed.")

    def on_button(self):
        print("[Basics.py] EdProperty button pressed.")

    def set_temperature(self, val):
        self.__temperature = val

    def set_choice(self, val):
        self.__curr_choice = val

    def set_color(self, val):
        self.__color = val

    def get_color(self):
        return self.__color
