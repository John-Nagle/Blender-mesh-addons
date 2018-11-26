#
#   Meshlab interface for Second Life
#
#   Runs various canned Meshlab scripts on meshes in Blender.
#
#   John Nagle
#   October, 2018
#   License: GPL 3
#
#   Init file
#
import bpy
import importlib
from . import meshlab
importlib.reload(meshlab)                                 # force a reload. Blender will not do this by default.

bl_info = {
    "name": "Meshlab",
    "author": "John Nagle",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "Object > Meshlab",
    "description": "Meshlab utilities for Second Life",
    "category": "Object",
    "support" : "Testing",
}

#   Connect to Blender menu system        
def menu_func(self, context) :
    self.layout.operator(meshlab.Meshlab.bl_idname) 
        
#
#   register -- addon is being loaded
#
def register():
    bpy.utils.register_class(meshlab.Meshlab)
    bpy.utils.register_class(meshlab.FilterSubmenu)
    ####bpy.utils.register_class(meshlab.MeshlabPanel)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    return
        
#
#   unregister -- addon is being unloaded
def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_class(meshlab.FilterSubmenu)

    ####bpy.utils.unregister_class(meshlab.MeshlabPanel)
    bpy.utils.unregister_class(meshlab.Meshlab)

    
if __name__ == "__main__":              # for debug
    register()

