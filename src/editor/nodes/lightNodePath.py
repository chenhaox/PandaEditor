import editor.utils as ed_utils
from editor.nodes.baseNodePath import BaseNodePath
from panda3d.core import LColor, LVecBase3f


class LightNp(BaseNodePath):
    def __init__(self, np, uid=None, *args, **kwargs):
        BaseNodePath.__init__(self, np, uid, create_properties=False, *args, **kwargs)

        self.__ed_light_colour = LColor(1, 1, 1, 1)  # actual color(Hue), as seen, unscaled by intensity
        self.__intensity = 1.0
        self.__is_active = True

        self.setScale(4)

        copy = kwargs.pop("copy", False)
        if copy and np.hasPythonTag("PICKABLE"):
            np = np.getPythonTag("PICKABLE")
            self.__intensity = np.get_intensity()
            self.__ed_light_colour = np.get_color(normalized=False)
            self.toggle_active(np.get_active_status())

    def create_properties(self):
        super().create_properties()

        space = ed_utils.EdProperty.EmptySpace(0, 10)
        label = ed_utils.EdProperty.Label(name="Light Properties", is_bold=True)

        colour = ed_utils.EdProperty.FuncProperty(name="Light Color",
                                                  value=self.get_color(),
                                                  setter=self.set_color,
                                                  getter=self.get_color)

        intensity = ed_utils.EdProperty.FuncProperty(name="Color intensity",
                                                     value=self.get_intensity(),
                                                     setter=self.set_intensity,
                                                     getter=self.get_intensity)

        is_active = ed_utils.EdProperty.FuncProperty(name="Is Active",
                                                     value=self.get_active_status(),
                                                     setter=self.toggle_active,
                                                     getter=self.get_active_status)

        self.properties.append(space)
        self.properties.append(label)
        self.properties.append(colour)
        self.properties.append(intensity)
        self.properties.append(is_active)

    def set_intensity(self, val):
        if not self.__is_active:
            self.__intensity = 0.0
        else:
            self.__intensity = val

        r = self.__ed_light_colour.x * self.__intensity
        g = self.__ed_light_colour.y * self.__intensity
        b = self.__ed_light_colour.z * self.__intensity

        color = LColor(r, g, b, 1)
        self.node().setColor(color)

    def set_color(self, val, normalize=True):
        # convert to panda3d colour range
        if normalize:
            r = ed_utils.common_maths.map_to_range(0, 255, 0, 1, val.x)
            g = ed_utils.common_maths.map_to_range(0, 255, 0, 1, val.y)
            b = ed_utils.common_maths.map_to_range(0, 255, 0, 1, val.z)
        else:
            r = val.x
            g = val.y
            b = val.z

        self.setColor(LColor(r, g, b, 1))
        self.__ed_light_colour = LColor(r, g, b, 1)

        r = r * self.__intensity
        g = g * self.__intensity
        b = b * self.__intensity
        self.node().setColor(LColor(r, g, b, 1))

    def toggle_active(self, val):
        self.__is_active = val
        if not self.__is_active:
            self.set_intensity(0.0)

    def get_intensity(self):
        return self.__intensity

    def get_color(self, normalized=True):
        if normalized:
            r = ed_utils.common_maths.map_to_range(0, 1, 0, 255, self.__ed_light_colour.x)
            g = ed_utils.common_maths.map_to_range(0, 1, 0, 255, self.__ed_light_colour.y)
            b = ed_utils.common_maths.map_to_range(0, 1, 0, 255, self.__ed_light_colour.z)
            return LColor(r, g, b, 255)
        else:
            return LColor(self.__ed_light_colour.x, self.__ed_light_colour.y, self.__ed_light_colour.z, 255)

    def get_active_status(self):
        return self.__is_active


class EdDirectionalLight(LightNp):
    def __init__(self, np, uid=None, *args, **kwargs):
        LightNp.__init__(self, np, uid, *args, **kwargs)
        self._id = "__DirectionalLight__"
        self.set_scale(8)
        self.create_properties()

    def create_properties(self):
        super(EdDirectionalLight, self).create_properties()


class EdPointLight(LightNp):
    def __init__(self, np, uid=None, *args, **kwargs):
        LightNp.__init__(self, np, uid, *args, **kwargs)
        self._id = "__PointLight__"

        self.attenuation_map = {
            0: LVecBase3f(1, 0, 0),
            1: LVecBase3f(0, 1, 0),
            2: LVecBase3f(0, 0, 1),
            3: LVecBase3f(0, 1, 1)
        }

        # set default value for attenuation
        self.attenuation = -1
        if self.node().getAttenuation() in self.attenuation_map.values():
            value = [i for i in self.attenuation_map if self.attenuation_map[i] == self.node().getAttenuation()]
            self.attenuation = value[0]

        copy = kwargs.pop("copy", False)
        if copy and np.hasPythonTag("PICKABLE"):
            np = np.getPythonTag("PICKABLE")
            self.set_attenuation(np.get_attenuation())

        self.set_scale(15)
        self.create_properties()

    def create_properties(self):
        super(EdPointLight, self).create_properties()

        attenuation = ed_utils.EdProperty.ChoiceProperty(name="Attenuation",
                                                         setter=self.set_attenuation,
                                                         getter=self.get_attenuation,
                                                         choices=['constant', 'linear', 'quadratic',
                                                                  'linear-quadratic'])

        self.properties.append(attenuation)

    def get_attenuation(self):
        return self.attenuation

    def set_attenuation(self, val):
        self.node().setAttenuation(self.attenuation_map[val])
        self.attenuation = val


class EdSpotLight(LightNp):
    def __init__(self, np, uid=None, *args, **kwargs):
        LightNp.__init__(self, np, uid, *args, **kwargs)
        self._id = "__SpotLight__"

        self.attenuation_map = {
            0: (1, 0, 0),
            1: (0, 1, 0),
            2: (0, 0, 1),
            3: (0, 1, 1)
        }
        # set default value for attenuation
        self.attenuation = -1
        if self.node().getAttenuation() in self.attenuation_map.values():
            value = [i for i in self.attenuation_map if self.attenuation_map[i] == self.node().getAttenuation()]
            self.attenuation = value[0]

        copy = kwargs.pop("copy", False)
        if copy and np.hasPythonTag("PICKABLE"):
            np = np.getPythonTag("PICKABLE")
            self.set_attenuation(np.get_attenuation())

        self.create_properties()

    def create_properties(self):
        super(EdSpotLight, self).create_properties()

        attenuation = ed_utils.EdProperty.ChoiceProperty(name="Attenuation",
                                                         setter=self.set_attenuation,
                                                         getter=self.get_attenuation,
                                                         choices=['constant', 'linear', 'quadratic',
                                                                  'linear-quadratic'])

        space = ed_utils.EdProperty.EmptySpace(0, 10)
        label = ed_utils.EdProperty.Label(name="Lens", is_bold=True)

        lens = self.node().getLens()
        lens.setNearFar(0.5, 5)
        lens_props = ed_utils.EdProperty.Utils.get_properties_for_lens(lens)

        self.properties.append(attenuation)
        self.properties.append(space)
        self.properties.append(label)
        self.properties.extend(lens_props)

    def get_attenuation(self):
        return self.attenuation

    def set_attenuation(self, val):
        self.node().attenuation = self.attenuation_map[val]
        self.attenuation = val


class EdAmbientLight(LightNp):
    def __init__(self, np, uid=None, *args, **kwargs):
        LightNp.__init__(self, np, uid, *args, **kwargs)
        self._id = "__AmbientLight__"

    def create_properties(self):
        super(EdAmbientLight, self).create_properties()