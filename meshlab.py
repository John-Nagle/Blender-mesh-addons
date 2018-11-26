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
    
#
#   FilterScriptOperator - runs indicated filter on the selection
#
class FilterScriptOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"
    ####bl_options = {'REGISTER', 'UNDO'}  
    
    script_filename = bpy.props.StringProperty(name="filter_script_filename")
    

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        """
        Submenu item clicked.
        """
        self.report({'INFO'}, "%s clicked!" % self.script_filename)
        self.run(context)
        return {'FINISHED'}
        
    def run(self, context) :
        """
        Run Meshlab using selected filter
        """
        server = findmeshlab()                                                          # find meshlabserver executable
        if server is None :
            self.report({'ERROR'}, "Can't find Meshlab Server program. 'meshlabserver' must be in your PATH for command line programs.")
            return      
        #   Preliminary checks complete, OK to attempt operation   
        try :
            scriptfile = self.script_filename
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



        
    
class FilterSubmenu (bpy.types.Menu):
    """
    Submenu for selecting filter to use
    """
    bl_idname = "OBJECT_MT_select_submenu"
    bl_label = "Select Meshlab Script"

    def draw(self, context) :
        """
        Draw submenu offering various standard MeshLab scripts
        """
        addonpath = os.path.dirname(__file__)               # the mlx files are in the script directory
        for f in findscriptfiles(addonpath,"mlx") :
            self.layout.operator("object.simple_operator", text=f).script_filename = f
       
    
class Meshlab(bpy.types.Operator):
    """
    Run a Meshlab script on selected objects - menu part
    """
    bl_idname = "meshlab.send_to_meshlab"
    bl_label = "Send To Meshlab"
    bl_options = {'REGISTER','UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None                                  

    def execute(self, context):
        """
        All this does is pop up the script submenu
        """
        print("Pop up menu")    # ***TEMP****        
        bpy.ops.wm.call_menu(name="OBJECT_MT_select_submenu") # submenu for selecting script 
        return {'FINISHED'}


