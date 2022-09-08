import editor.constants as constants
from panda3d.core import PerspectiveLens, OrthographicLens, Camera, NodePath
from editor.nodes.baseNodePath import BaseNodePath
from editor.utils import EdProperty


class CameraNodePath(BaseNodePath):
    def __init__(self, np, uid=None, *args, **kwargs):

        if np is None:
            np = NodePath(Camera("CameraNodePath"))
        BaseNodePath.__init__(self, np, uid, *args, **kwargs)

        self._id = "__CameraNodePath__"
        # self.lens_type = 0  # [Lens type] 0: Perspective, 1: Ortho
        self.current_lens_type = -1
        self.lens_properties = []  # properties for particular lens type

        copy_data = kwargs.pop("copy", False)
        if copy_data and np.hasPythonTag("PICKABLE"):
            obj = np.getPythonTag("PICKABLE")
            if obj.get_lens_type() == 0:
                self.set_perspective_lens(obj.node().getLens())
            elif obj.get_lens_type() == 1:
                self.set_ortho_lens(obj.node().getLens())
        else:
            self.set_perspective_lens()

    def create_properties(self):
        super(CameraNodePath, self).create_properties()

        space_prop = EdProperty.EmptySpace(0, 10)
        lens_prop_label = EdProperty.Label(name="Lens", is_bold=True)
        lens_prop = EdProperty.ChoiceProperty("Lens Type",
                                              choices=["Perspective", "Orthographic"],
                                              value=0,
                                              setter=self.set_lens,
                                              getter=self.get_lens_type)

        # remove color property for camera
        for prop in self.properties:
            if prop.name == "Color":
                self.properties.remove(prop)

        self.properties.append(space_prop)
        self.properties.append(lens_prop_label)
        self.properties.append(lens_prop)

    def set_lens(self, lens_type: int):
        if lens_type == 0:
            self.set_perspective_lens()
        if lens_type == 1:
            self.set_ortho_lens()

    def get_lens_type(self):
        return self.current_lens_type

    def set_perspective_lens(self, lens=None):
        # make sure to not redo same thing
        if self.current_lens_type == 0:
            return

        if lens:
            pass
        else:
            lens = PerspectiveLens()

        self.node().setLens(lens)
        self.create_perspective_lens_properties(lens)
        self.current_lens_type = 0
        constants.obs.trigger("ResizeEvent")

    def set_ortho_lens(self, lens=None):
        # make sure to not redo same thing
        if self.current_lens_type == 1:
            return

        if lens:
            pass
        else:
            lens = OrthographicLens()

        self.node().setLens(lens)
        self.create_ortho_lens_properties(lens)
        self.current_lens_type = 1

    def create_perspective_lens_properties(self, lens):
        # clear existing lens properties
        for prop in self.lens_properties:
            self.properties.remove(prop)
            continue
        self.lens_properties.clear()

        self.lens_properties.extend(EdProperty.Utils.get_properties_for_lens(lens))
        self.properties.extend(self.lens_properties)

    def create_ortho_lens_properties(self, lens):
        # clear existing lens properties
        for prop in self.lens_properties:
            self.properties.remove(prop)
            continue
        self.lens_properties.clear()

        self.lens_properties.extend(EdProperty.Utils.get_properties_for_lens(lens))
        self.properties.extend(self.lens_properties)
