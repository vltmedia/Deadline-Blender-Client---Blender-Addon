#
#Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 2 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import print_function

from bpy.props import IntProperty, PointerProperty, BoolProperty, CollectionProperty,FloatProperty
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty
from bpy.types import Panel, PropertyGroup, WindowManager

bl_info = {
    "name": "Submit Blender To Deadline",
    "description": "Submit a Blender job to Deadline",
    "author": "Thinkbox Software Inc & Ammendments by Justin Jaro",
    "version": (1,0),
    "blender" : (3, 0, 0),
    "category": "Render",
    "location": "Render > Submit To Deadline",
    }

import bpy
import os
import sys
from sys import platform
import subprocess

print("------------------------------------------------------")
print("------------------------------------------------------")
print(__name__)
print("------------------------------------------------------")
print("------------------------------------------------------")

class SubmitBlenderToDeadlineAddonPreferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__
    deadlineBin = ""
    try:
        deadlineBin = os.environ['DEADLINE_PATH']
        
    except KeyError:
        #if the error is a key error it means that DEADLINE_PATH is not set. however Deadline command may be in the PATH or on OSX it could be in the file /Users/Shared/Thinkbox/DEADLINE_PATH
        pass
    DeadlineBinPath: StringProperty(
        name="Deadline Bin Path",
        subtype='DIR_PATH',
        default=deadlineBin
        
    )

    

    def draw(self, context):
        layout = self.layout
        layout.label(text="Set these preferences")
        layout.prop(self, "DeadlineBinPath")

def GetDeadlineCommand(*args, **kwargs):
    deadlineBin = ""
    # try:
    #     deadlineBin = os.environ['DEADLINE_PATH']
    #     if not os.path.exists(deadlineBin):
    #         deadlineBin = os.environ['DEADLINE_PATH'] = "F:/DeadlineClient/BigBoy/bin"
    # except KeyError:
    #     #if the error is a key error it means that DEADLINE_PATH is not set. however Deadline command may be in the PATH or on OSX it could be in the file /Users/Shared/Thinkbox/DEADLINE_PATH
    #     pass
    
    
    # # On OSX, we look for the DEADLINE_PATH file if the environment variable does not exist.
    # if deadlineBin == "" and  os.path.exists( "/Users/Shared/Thinkbox/DEADLINE_PATH" ):
    #     with open( "/Users/Shared/Thinkbox/DEADLINE_PATH" ) as f:
    #         deadlineBin = f.read().strip()

    preferences = kwargs['preferences']
    deadlineBin = preferences.DeadlineBinPath
    
    deadlineCommand = os.path.join(deadlineBin, "deadlinecommand")
    if platform == "linux" or platform == "linux2":
        deadlineCommand = os.path.join(deadlineBin, "deadlinecommand")
        
    # linux
    elif platform == "darwin":
        deadlineCommand = os.path.join(deadlineBin, "deadlinecommand")
        
        # OS X
    elif platform == "win32":
        deadlineCommand = os.path.join(deadlineBin, "deadlinecommand.exe")
        
    return deadlineCommand

def GetRepositoryPath(*args, **kwargs):
    deadlineCommand = GetDeadlineCommand(preferences=kwargs['preferences'])
    subdir = args[0]
    startupinfo = None
    #if os.name == 'nt':
    #   startupinfo = subprocess.STARTUPINFO()
    #   startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    args = [deadlineCommand, "-GetRepositoryPath "]   
    if subdir != None and subdir != "":
        args.append(subdir)
    print(args)
    # Specifying PIPE for all handles to workaround a Python bug on Windows. The unused handles are then closed immediatley afterwards.
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)

    proc.stdin.close()
    proc.stderr.close()

    output = proc.stdout.read()

    path = output.decode("utf_8")
    path = path.replace("\r","").replace("\n","").replace("\\","/")

    return path
def GetRepositoryFilePath(*args, **kwargs):
    deadlineCommand = GetDeadlineCommand(preferences=kwargs['preferences'])
    subdir = args[0]
    startupinfo = None
    #if os.name == 'nt':
    #   startupinfo = subprocess.STARTUPINFO()
    #   startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    args = [deadlineCommand, "-GetRepositoryFilePath "]   
    if subdir != None and subdir != "":
        args.append(subdir)
    
    # Specifying PIPE for all handles to workaround a Python bug on Windows. The unused handles are then closed immediatley afterwards.
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)

    proc.stdin.close()
    proc.stderr.close()

    output = proc.stdout.read()

    path = output.decode("utf_8")
    path = path.replace("\r","").replace("\n","").replace("\\","/")

    return path


def SubmitBlenderToDeadline(*args, **kwargs ):
    script_file = GetRepositoryFilePath("scripts/Submission/BlenderSubmission.py",preferences=kwargs['preferences'])

    curr_scene = bpy.context.scene
    curr_render = curr_scene.render    

    scene_file = str(bpy.data.filepath)
    
    if scene_file != "":
        bpy.ops.wm.save_mainfile()
    
    frame_range = str(curr_scene.frame_start)
    if curr_scene.frame_start != curr_scene.frame_end:
        frame_range = frame_range + "-" + str(curr_scene.frame_end)
    
    output_path = str(curr_render.frame_path( frame=curr_scene.frame_start ))
    threads_mode = str(curr_render.threads_mode)
    threads = curr_render.threads
    if threads_mode == "AUTO":
        threads = 0
    
    platform = str(bpy.app.build_platform)
    
    deadlineCommand = GetDeadlineCommand(*args, **kwargs)
    
    args = []
    args.append(deadlineCommand)
    args.append("-ExecuteScript")
    args.append(script_file)
    args.append(scene_file)
    args.append(frame_range)
    args.append(output_path)
    args.append(str(threads))
    args.append(platform)
    
    startupinfo = None
    #~ if os.name == 'nt':
        #~ startupinfo = subprocess.STARTUPINFO()
        #~ startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    subprocess.Popen(args, startupinfo=startupinfo)


class SubmitToDeadline_Operator (bpy.types.Operator):
    bl_idname = "ops.submit_blender_to_deadline"
    bl_label = "Submit Blender To Deadline"
    
    def execute( self, context ):
        # Get the repository path
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences
        
        path = GetRepositoryPath("K:/", preferences =addon_prefs)
        if path != "":            
            # Add the path to the system path
            if path not in sys.path :
                print( "Appending \"%s\" to system path to import SubmitBlenderToDeadline module" % path )
                sys.path.append( path )
            else:
                print( "\"%s\" is already in the system path" % path )

            
            # Import the script and call the main() function
            # import SubmitBlenderToDeadline
            # SubmitBlenderToDeadline.main( )
            SubmitBlenderToDeadline(preferences =addon_prefs)
        else:
            print( "The SubmitBlenderToDeadline.py script could not be found in the Deadline Repository. Please make sure that the Deadline Client has been installed on this machine, that the Deadline Client bin folder is set in the DEADLINE_PATH environment variable, and that the Deadline Client has been configured to point to a valid Repository." )
        
        return {'FINISHED'}


    
def deadline_submit_button( self, context ):
    
    self.layout.separator()
    self.layout.operator( SubmitToDeadline_Operator.bl_idname, text="Submit To Deadline" )
    
classes = (
    SubmitToDeadline_Operator, 
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
        
    bpy.utils.register_class(SubmitBlenderToDeadlineAddonPreferences)

    bpy.types.TOPBAR_MT_render.append( deadline_submit_button )

def unregister():
    from bpy.utils import unregister_class
    bpy.utils.unregister_class(SubmitBlenderToDeadlineAddonPreferences)
    for cls in reversed(classes):
        unregister_class(cls)
    
    bpy.types.TOPBAR_MT_render.remove( deadline_submit_button )

if __name__ == "__main__":
    register()
    
