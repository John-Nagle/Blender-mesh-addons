#
#   Meshlab interface for Second Life
#
#   Runs various canned Meshlab scripts on meshes in Blender.
#
#   John Nagle
#   October, 2018
#   License: GPL V3
#
#   Imports
#
import bpy
import os
import os.path
import sys
import subprocess
import math
import shutil
import tempfile

#   Debug constants
DEBUGPRINT = True                                           # print if on
KEEPTEMPDIR = True                                          # do not delete temp dir if on

#
#   Non-class functions
#
def findmeshlab() :
    """
    Find the meshlabserver program. Look in search path.
    """
    if sys.platform in ['win32', 'cygwin'] :                                            # if Windows-type platform
        meshlabloc = shutil.which("meshlabserver.exe")                                  # look for server
    else :                                                                              # Linux/Unix
        meshlabloc = shutil.which("meshlabserver")                                      # look on PATH for server
    if meshlabloc and os.path.isfile(meshlabloc) and os.access(meshlabloc, os.X_OK) :
        return meshlabloc                                                               # found an executable meshlabserver
    return None
    
def findscriptfiles(path, suffix) :
    """
    Find all readable files with given suffix in given directory.
    """
    return [f for f in os.listdir(path) if f.endswith("." + suffix) and os.path.isfile(os.path.join(path, f))] 
    
class SimpleOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        self.report({'INFO'}, "Button clicked!")
        return {'FINISHED'}


        
    
class FilterSubmenu (bpy.types.Menu):
    """
    Submenu for selecting filter to use
    """
    bl_idname = "OBJECT_MT_select_submenu"
    bl_label = "Select Meshlab Script"

    def draw(self, context):
        layout = self.layout
        addonpath = os.path.dirname(__file__)   # the mlx files are where the script is
        for f in findscriptfiles(addonpath,"mlx") :
            print("MLX file: " + f) # ***TEMP***
            layout.operator("object.simple_operator", text=f)
        ####    items = bpy.props.EnumProperty(items=[("A","A",'',1), ("B","B",'',2)])  
        
        self.items = bpy.props.EnumProperty(items= (('0', 'A', 'The zeroth item'),    
                                                 ('1', 'B', 'The first item'),    
                                                 ('2', 'C', 'The second item'),    
                                                 ('3', 'D', 'The third item')),
                                                 name = "fixed list")       
        ####self.layout.prop(self, 'items', expand=True)
        ####layout.operator("object.simple_operator")
        layout.separator()


        layout.operator("object.select_all", text="Select/Deselect All").action = 'TOGGLE'
        layout.operator("object.select_all", text="Inverse").action = 'INVERT'
        layout.operator("object.select_random", text="Random")

        # access this operator as a submenu
        layout.operator_menu_enum("object.select_by_type", "type", text="Select All by Type...")

        layout.separator()

        # expand each operator option into this menu
        layout.operator_enum("object.lamp_add", "type")

        layout.separator()

        # use existing memu
        layout.menu("VIEW3D_MT_transform")


####bpy.utils.register_class(FilterSubmenu)

# test call to display immediately.
####bpy.ops.wm.call_menu(name="OBJECT_MT_select_submenu")                                                                     

       
    
class Meshlab(bpy.types.Operator):
    """
    Run a Meshlab script on selected objects
    """
    bl_idname = "meshlab.send_to_meshlab"
    bl_label = "Send To Meshlab"
    bl_options = {'REGISTER','UNDO'}
    
    cleanup = bpy.props.BoolProperty(name = "cleanup", description = "True to delete temp files", default = False)
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
        
    def run(self, context) :
        """
        Export file, send to meshlab server, re-import file
        """
        sce = bpy.context.scene
        ob = bpy.context.object
        scale = ob.scale
        name = ob.name
    
        server = findmeshlab()                                                          # find meshlabserver executable
        if server is None :
            self.report({'ERROR'}, "Can't find Meshlab Server program. 'meshlabserver' must be in your PATH for command line programs.")
            return
        #   Pop up submenu for script to select    
        
        bpy.ops.wm.call_menu(name="OBJECT_MT_select_submenu")                           # submenu for selecting script
        
        return # ***TEMP***
                                    

        #   Preliminary checks complete, OK to attempt operation   
        try :
            working_dir = tempfile.mkdtemp(prefix='Blender-Meshlab')                    # scratch file directory  
            #   Name export file from blender, and meshlab output file for re-import
            temp_ply_path = os.path.join(working_dir,"temp_mesh.ply")
            temp_o_ply_path = os.path.join(working_dir,"temp_mesh_o.ply")
    
            bpy.ops.export_mesh.ply(filepath=temp_ply_path, check_existing = False)     # exports entire scene, revise
     
    
            ####result = subprocess.call([server,"-i",temp_ply_path,"-o",temp_o_ply_path,"-s",scriptfile, "-om","vc vn fn fc vt"])
            result = subprocess.call([server,"-i",temp_ply_path,"-o",temp_o_ply_path,"-s",scriptfile, "-m","vc vn fn fc vt"])

            if result != 0 :
                self.report({'ERROR'},"\"%s\" running script \"%s\" failed, status %d" % (server, scriptfile, result)) # trouble
                return
    
            bpy.ops.import_mesh.ply(filepath=temp_o_ply_path)
            new_obj = bpy.data.objects["temp_mesh_o"]
            new_obj.name = name + "_meshlab"
    
            bpy.ops.object.select_all(action = 'DESELECT')
            new_obj.select = True
            bpy.context.scene.objects.active = new_obj
            bpy.ops.transform.rotate(value = (math.pi/2,),axis = (1,0,0))
            new_obj.scale = scale
            
        finally:                                                                            # clean up, even if things went wrong
            assert(working_dir)
            if not KEEPTEMPDIR :                                                            # clean up, unless debugging
                if os.path.exists(temp_ply_path) :
                    os.remove(temp_ply_path)
                if os.path_exists(temp_o_ply_path) :
                    os.remove(temp_o_ply_path)
                os.rmdir(working_dir)                                                       # temp directory should always exist


    def execute(self, context):
        self.run(context)       
        return {'FINISHED'}


