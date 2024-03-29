from editor.commandManager import Command
from editor.globals import editor


class RenameNPs(Command):
    def __init__(self, np, old_name, new_name, *args, **kwargs):

        self.np = np
        self.old_name = old_name
        self.new_name = new_name

    def do(self, *args, **kwargs):
        self.np.set_name(self.new_name)
        editor.inspector.set_object(self.np, self.np.get_name(), self.np.get_properties())

    def undo(self):
        self.np.set_name(self.old_name)
        editor.scene_graph.rename_item(self.np, self.np.get_name())
        editor.inspector.layout_object_properties(self.np, self.np.get_name(), self.np.get_properties())

    def clean(self, **kwargs):
        pass
