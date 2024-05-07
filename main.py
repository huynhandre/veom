  # import javascript modules
from js import THREE, window, document, Object, console, URL, Blob
# import pyscript / pyodide modules
from pyodide.ffi import create_proxy, to_js
# import python module
import math, random, time, asyncio, sys, datetime
from datetime import timedelta

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MAIN PROGRAMM
def main():
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------
    # VISUAL SETUP
    # declare the variables
    global renderer, scene, camera, controls, composer
    
    # set up the renderer
    renderer = THREE.WebGLRenderer.new()
    renderer.setPixelRatio( window.devicePixelRatio )
    renderer.setSize(window.innerWidth, window.innerHeight)
    document.body.appendChild(renderer.domElement)

    # set up the scene
    scene = THREE.Scene.new()
    back_color = THREE.Color.new(1,1,1)
    primary_color = THREE.Color.new(0.15,0.45,0.5)
    scene.background = back_color
    width = window.innerWidth
    height = window.innerHeight
    camera = THREE.PerspectiveCamera.new(30, width/height, 0.1, 1000)
    camera.position.x = -45
    camera.position.y = 15
    camera.position.z = 30
    camera.lookAt(0,0,0)
    scene.add(camera)

    # lighting
    directional_light = THREE.DirectionalLight.new(back_color, 1.0)
    ambient_light = THREE.AmbientLight.new(back_color)
    scene.add(directional_light, ambient_light)
  
    global  raycaster, mouse
    mouse = THREE.Vector2.new()
    raycaster = THREE.Raycaster.new()
    
    # graphic post processing
    global composer
    post_process()

    # set up responsive window
    resize_proxy = create_proxy(on_window_resize)
    window.addEventListener('resize', resize_proxy) 

    # set up mouse orbit control
    controls = THREE.OrbitControls.new(camera, renderer.domElement)
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BASICS
    global mousemove, dragging,  lessstrength,  strengthaktivation,  morestrength, strengthclick

    # timer
    global start_time, last_time
    start_time = datetime.datetime.now()
    last_time = start_time

    # gumball 
    global gumball_size
    gumball_size = 0.6
    controls.enabled = True
    
    lessstrength = create_proxy(LessStrength)
    window.addEventListener('keypress', lessstrength )

    morestrength = create_proxy(MoreStrength)
    window.addEventListener('keydown', morestrength )
     
    strengthaktivation = create_proxy(Sphereactivation)
    window.addEventListener('pointermove', strengthaktivation)
    
    strengthclick = create_proxy(SphereClick)
    window.addEventListener('dblclick', strengthclick)

    mousemove = create_proxy(Mousemove)
    window.addEventListener('keyup', mousemove )

    dragging = create_proxy(Dragging)
    window.addEventListener('keypress', dragging)

    proxy_timer = create_proxy(reload_timer)
    window.addEventListener('mousemove', proxy_timer)
    window.addEventListener('click', proxy_timer)

    # spawn new attractor
    global add_attractor
    add_attractor = create_proxy(Add_attractor)

    # mouse events for transformcontrols
    global mouse_down, mouse_up
    mouse_down = create_proxy(deactivate_o_controls)
    mouse_up = create_proxy(activate_o_controls)
    
    # meshes, material
    global material, material_center, line_material

    # create main material
    material = THREE.MeshBasicMaterial.new()
    material.color = primary_color
    material.transparent = True
    material.opacity = 0.15

    # create  center material
    material_center = THREE.MeshBasicMaterial.new()
    material_center.color = primary_color

    # create line material 
    line_material = THREE.LineBasicMaterial.new()
    line_material.color = primary_color

    # lists to store geometries
    global voxel_values, voxel_list, wireframe_list, voxel_positions, boundary, attractors, attractors_and_controls, attractor_positions, loaded_objects, history, future
    global selected_spheres, Helper, spheres, attractor_strengths, ValueStr, strengths_update, selection

    strengths_update = 0
    ValueStr = []

    history = []
    future = []    
    
    loaded_objects = []

    attractors = []
    attractors_and_controls = []
    attractor_positions = []

    voxel_list = []
    wireframe_list = []

    voxel_positions = []
    voxel_values = []

    boundary = []
    
    selected_spheres = []
    Helper = []

    spheres = []
    attractor_strengths = []
    selection = []

    # set up GUI
    # define the grid params
    global grid_params, grid_scale_x, grid_scale_y, grid_scale_z, wireframe_base, hide_voxels
    grid_scale_x = 15
    grid_scale_y = 15
    grid_scale_z = 15
    wireframe_base = False
    hide_voxels = False

    grid_params = {
            "grid_scale_x":grid_scale_x,
            "grid_scale_y":grid_scale_y,
            "grid_scale_z":grid_scale_z,
            "wireframe": wireframe_base,
            "hide_voxels": hide_voxels
    }
    grid_params = Object.fromEntries(to_js(grid_params))

    # define attractor params
    global attractor_params, attractor_limit, exporter, filling
    attractor_limit = 0.65
    
    set_strength = True
    
    exporter = False
    filling = "Type 1"

    attractor_params = {
            "limit": attractor_limit,
            "set_strength": set_strength,
            "Geometry": filling
            
    }
    attractor_params = Object.fromEntries(to_js(attractor_params))

    filling_options = ["No Infill", "Type 1", "Type 2", "Type 3"]
  
    global gui, param_folder, param1, param2, param3, param4, param5, param6
    gui = window.dat.GUI.new()
    param_folder = gui.addFolder('Bounding Parameters')
    param1 = param_folder.add(grid_params, 'grid_scale_x', 1,25,1).name("Scale X")
    param2= param_folder.add(grid_params, 'grid_scale_y', 1,25,1).name("Scale Y")
    param3 = param_folder.add(grid_params, 'grid_scale_z', 1,25,1).name("Scale Z")
    #param4 = param_folder.add(grid_params, 'wireframe')
    param5 = param_folder.add(grid_params, 'hide_voxels').name("Clean view")

    param_folder = gui.addFolder('Attractor')
    param6 = param_folder.add(attractor_params, 'limit', 0, 1)
    param_folder.open()
    param_folder = gui.add(attractor_params, 'Geometry', to_js(filling_options))

    # html buttonsklk
    button_proxy1 = create_proxy(export)
    button_proxy2 = create_proxy(reset)
    button_proxy3 = create_proxy(undo)
    button_proxy4 = create_proxy(redo)
    document.getElementById("download-gltf").addEventListener("click", button_proxy1, False)
    document.getElementById("reset_scene").addEventListener("click", button_proxy2, False)
    document.getElementById("undo").addEventListener("click", button_proxy3, False)
    document.getElementById("redo").addEventListener("click", button_proxy4, False)
    
    #IMPLEMENT
    # initial attractors
    generate_attractor(3, -3.5, 3)
    generate_attractor(-3, 3.5, -3)

    # delay 
    global firstupdate
    firstupdate = 0
    global updater
    updater = 2
    global delay
    delay = 2

    render()
 
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
# VOXEL GRID
# create a voxel at each node of the grid
def generate_grid():
    global voxel_positions, grid_scale_x, grid_scale_y, grid_scale_z
    voxel_positions = []
   
    generate_boundary()

    for i in range(grid_scale_x):
        for j in range(grid_scale_y):
            for k in range(grid_scale_z):
   
                # position Voxels
                # position - 1/2 of grid size + 1/2 of voxel size a
                pos_x = i - 0.5*grid_scale_x + 0.5
                pos_y = j - 0.5*grid_scale_y + 0.5
                pos_z = k - 0.5*grid_scale_z + 0.5
                
                position = THREE.Vector3.new(pos_x, pos_y, pos_z)
                voxel_positions.append(position)

def generate_voxels():
    global voxel_list, wireframe_list
    global grid_params, wireframe_base, hide_voxels
    # remove all voxels
    for wireframe in wireframe_list:
        scene.remove(wireframe)
    for voxel in voxel_list:
        scene.remove(voxel)

    wireframe_list = []
    voxel_list = []
    
    hide_voxels = grid_params.hide_voxels

    # create voxels
    geometry = THREE.BoxGeometry.new( 1, 1 , 1 ) #calculate voxel sizes
    voxel_opacity = 0.3
    for pos, val in zip(infill_positions, infill_type):

         # different colors
        if val == 1:
            voxel_material1 = THREE.MeshBasicMaterial.new()
            voxel_material1.transparent = True
            voxel_material1.opacity = voxel_opacity
            voxel_material1.color = THREE.Color.new("rgb(56, 154, 216)")

            voxel = THREE.Mesh.new(geometry, voxel_material1)
        
            geometry_wireframe = THREE.EdgesGeometry.new(voxel.geometry)
            wireframe = THREE.LineSegments.new(geometry_wireframe, line_material)

            voxel.position.set(pos.x, pos.y, pos.z)
            voxel_list.append(voxel)
            wireframe.position.set(pos.x, pos.y, pos.z)
            wireframe_list.append(wireframe)
    
            if hide_voxels == False:
                if wireframe_base == True:
                    scene.add(wireframe)
                else:
                    scene.add(voxel) 

        elif val == 2:
            voxel_material2 = THREE.MeshBasicMaterial.new()
            voxel_material2.transparent = True
            voxel_material2.opacity = voxel_opacity
            voxel_material2.color = THREE.Color.new("rgb(62, 209, 206)")

            voxel = THREE.Mesh.new(geometry, voxel_material2)
        
            geometry_wireframe = THREE.EdgesGeometry.new(voxel.geometry)
            wireframe = THREE.LineSegments.new(geometry_wireframe, line_material)

            voxel.position.set(pos.x, pos.y, pos.z)
            voxel_list.append(voxel)
            wireframe.position.set(pos.x, pos.y, pos.z)
            wireframe_list.append(wireframe)
    
            if hide_voxels == False:
                if wireframe_base == True:
                    scene.add(wireframe)
                else:
                    scene.add(voxel) 

        elif val == 3:
            voxel_material3 = THREE.MeshBasicMaterial.new()
            voxel_material3.transparent = True
            voxel_material3.opacity = voxel_opacity
            voxel_material3.color = THREE.Color.new("rgb(89, 230, 145)")

            voxel = THREE.Mesh.new(geometry, voxel_material3)
        
            geometry_wireframe = THREE.EdgesGeometry.new(voxel.geometry)
            wireframe = THREE.LineSegments.new(geometry_wireframe, line_material)

            voxel.position.set(pos.x, pos.y, pos.z)
            voxel_list.append(voxel)
            wireframe.position.set(pos.x, pos.y, pos.z)
            wireframe_list.append(wireframe)
    
            if hide_voxels == False:
                if wireframe_base == True:
                    scene.add(wireframe)
                else:
                    scene.add(voxel) 



# create boundary
def generate_boundary():
    global boundary
    for boundary_edge in boundary:
        scene.remove(boundary_edge)

    if grid_params.hide_voxels == False:

        geometry_boundary = THREE.BoxGeometry.new(grid_scale_x, grid_scale_y, grid_scale_z)
        boundary = THREE.Mesh.new(geometry_boundary, material)
        geometry_edge = THREE.EdgesGeometry.new(boundary.geometry)
        boundary_edge = THREE.LineSegments.new(geometry_edge, line_material)
        scene.add(boundary_edge)

        boundary = []
        boundary.append(boundary_edge)
    else:
        pass
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------  
# VALUES
# attractor coordinates
def getcenter(sphere):
    geometry = sphere.geometry
    geometry.computeBoundingBox()
    center = THREE.Vector3.new()
    geometry.boundingBox.getCenter(center)
    sphere.localToWorld(center)
    return center

# calculate values in relation to distance
def individual_value(attractor, attractor_strength):
    global voxel_positions
    distances = []
    values = []
    
    # get distance between attractor and voxel
    for position in voxel_positions:
        #distance = position.distanceTo(attractor)
        distance =  math.sqrt( (position.x-attractor.x)**2 + (position.y-attractor.y)**2 + (position.z-attractor.z)**2 )   
        distances.append(distance)
    
    # calculate the voxels value   
    for d in distances:
            value = (max(distances) - d)**attractor_strength
            values.append(value)

    return values

# calculate final value for every voxel
def final_values():
    global voxel_values, voxel_positions, attractors, attractor_positions, attractor_strengths
    all_values = []
    voxel_values = [] 
    attractor_positions = []

    # get current attractor positons
    for sphere, attractor_strength in zip (attractors, attractor_strengths):
        attractor = getcenter(sphere)
        attractor_positions.append(attractor)
        # calculate individual values
        individual_values = individual_value(attractor, attractor_strength)
        all_values.append(individual_values)
    
    # calculate final values
    voxel_values = [sum(n) for n in zip(*all_values)]
     
    # copy final values list and sort it
    voxel_values_2 = voxel_values[:]
    voxel_values_2.sort()

    # define limit
    limit = len(voxel_values) - len(voxel_values)**(attractor_params.limit)

    # cull out voxel values and positions below limit and remove the voxels from the scene
    global infill_type, infill_positions, remaining_voxel_values
    remaining_voxel_values = []
    infill_positions = []

    index = -1
    for value in voxel_values:
        index += 1
        if value > voxel_values_2[round(limit)]:
            remaining_voxel_values.append(value)
            infill_positions.append(voxel_positions[index])
            
    # infill types and positions: 1 = low density; 2 = medium density; 3 = high density
    infill_type = remap_values(remaining_voxel_values)
    infill_positions
    generate_voxels()

# remaps all values above the limit
def remap_values(values):
    global remapped_values
    remapped_values = []
    remap_min = 1
    remap_max = 3
    for value in values:
        unrounded = remap_min + (remap_max - remap_min)* (value - min(values)) / ((max(values) - min(values)))
        remapped_values.append(round(unrounded))
        #console.log(round(unrounded))
    return remapped_values

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------  
# LOADER
# generate geometry
def generate_geometry():
    for objects in loaded_objects:
        tiles = scene.getObjectByName("tile")
        scene.remove(tiles)

    global infill_positions_1, infill_positions_2, infill_positions_3, hide_voxels
    infill_positions_1 = []
    infill_positions_2 = []
    infill_positions_3 = []

    global  counter_1, counter_2, counter_3
    counter_1 = 0
    counter_2 = 0
    counter_3 = 0
    
    # location of filling types and their variations
    type_1 = ["./assets/models/Type1/Variation1.glb","./assets/models/Type1/Variation2.glb","./assets/models/Type1/Variation3.glb"]
    type_1_clean = ["./assets/models/Type1_clean/Variation1.glb","./assets/models/Type1_clean/Variation2.glb","./assets/models/Type1_clean/Variation3.glb"] 
    type_2 = ["./assets/models/Type2/Variation1.glb","./assets/models/Type2/Variation2.glb","./assets/models/Type2/Variation3.glb"]
    type_2_clean = ["./assets/models/Type2_clean/Variation1.glb","./assets/models/Type2_clean/Variation2.glb","./assets/models/Type2_clean/Variation3.glb"] 
    type_3 = ["./assets/models/Type3/Variation1.glb","./assets/models/Type3/Variation2.glb","./assets/models/Type3/Variation3.glb"]
    type_3_clean = ["./assets/models/Type3_clean/Variation1.glb","./assets/models/Type3_clean/Variation2.glb","./assets/models/Type3_clean/Variation3.glb"] 

    if filling == "Type 1":
        if hide_voxels == False:
            choose_type = type_1
        else:
            choose_type = type_1_clean
    elif filling == "Type 2":
        if hide_voxels == False:
            choose_type = type_2
        else:
            choose_type = type_2_clean
    elif filling == "Type 3":
        if hide_voxels == False:
            choose_type = type_3
        else:
            choose_type = type_3_clean

    for pos, val in zip(infill_positions, infill_type):
        if val == 1:
            infill_positions_1.append(pos)
        
        if val == 2:
            infill_positions_2.append(pos)

        if val == 3:
            infill_positions_3.append(pos)
    
    for i in infill_positions_1:
        loader = THREE.GLTFLoader.new()
        loader.load(choose_type[0], create_proxy(obj_loader_1))
    for j in infill_positions_2:
        loader = THREE.GLTFLoader.new()
        loader.load(choose_type[1], create_proxy(obj_loader_2))
    for k in infill_positions_3:
        loader = THREE.GLTFLoader.new()
        loader.load(choose_type[2], create_proxy(obj_loader_3))


def count_geometry():
    amount = len(voxel_list)
    document.getElementById("demo").innerHTML = (f"{amount} Voxels displayed")

# loading geometry   
def obj_loader_1(gltf):
    global counter_1, infill_positions_1
    
    gltf.scene.position.set(infill_positions_1[counter_1].x, infill_positions_1[counter_1].y, infill_positions_1[counter_1].z)
    gltf.scene.name = "tile"
    loaded_objects.append(gltf)
    scene.add(gltf.scene)

    counter_1 += 1

def obj_loader_2(gltf):
    global counter_2, infill_positions_2
    
    gltf.scene.position.set(infill_positions_2[counter_2].x, infill_positions_2[counter_2].y, infill_positions_2[counter_2].z)
    gltf.scene.name = "tile"
    loaded_objects.append(gltf)
    scene.add(gltf.scene)

    counter_2 += 1

def obj_loader_3(gltf):
    global counter_3, infill_positions_3
    
    gltf.scene.position.set(infill_positions_3[counter_3].x, infill_positions_3[counter_3].y, infill_positions_3[counter_3].z)
    gltf.scene.name = "tile"
    loaded_objects.append(gltf)
    scene.add(gltf.scene)

    counter_3 += 1

#------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
# EXPORT
link = document.createElement("a")
document.body.appendChild(link)

def export(event):
    global geom_exporter, exporter, scene
    geom_exporter = THREE.GLTFExporter.new()
    jsscene = to_js(scene)
    geom_exporter.parse(jsscene, create_proxy(download))
    pass 

def download(result):
    #console.log(result)
    jsresult = to_js(result)
    saveArrayBuffer(jsresult, "VeomScene.gltf")

def saveArrayBuffer(buffer, fileName):
    jsbuffer = to_js(buffer)
    save(Blob.new([jsbuffer]), fileName)

def save(blob, fileName):
    link.href = URL.createObjectURL(blob)
    link.download = fileName
    link.click()

def error():
    #console.log("gltf error !")
    pass
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
# UPDATE
def update():
    global grid_scale_x, grid_scale_y, grid_scale_z, attractor_limit, attractor_strengths, firstupdate, updater, delay, exporter, filling, strengths_update, param5
    # if grid changes
    if wireframe_base != grid_params.wireframe or hide_voxels != grid_params.hide_voxels:
        if filling == "No Infill":
            grid_params.hide_voxels = False
            param5.updateDisplay()
        generate_grid()
        final_values()  
        changelog()  
        generate_geometry() 
    # if attractor limit changes
    elif attractor_limit != attractor_params.limit:
        strengths_update = 0
        attractor_limit = attractor_params.limit 
        final_values()
        changelog()
        if filling != "No Infill":
            generate_geometry()
    # if attractor strengths change
    elif strengths_update == 1:
        strengths_update = 0
        final_values()
        if filling != "No Infill":
            generate_geometry() 
    # if gridscale changes
    elif grid_scale_x != grid_params.grid_scale_x or grid_scale_y != grid_params.grid_scale_y or grid_scale_z != grid_params.grid_scale_z:
        grid_scale_x = grid_params.grid_scale_x
        grid_scale_y = grid_params.grid_scale_y
        grid_scale_z = grid_params.grid_scale_z
        generate_grid()
        final_values()
        changelog()
        if filling != "No Infill":
            generate_geometry()
    # if voxel fill changes
    elif filling != attractor_params.Geometry:
        filling = attractor_params.Geometry
        if filling != "No Infill":
            generate_geometry()
        elif filling == "No Infill":
            grid_params.hide_voxels = False
            param5.updateDisplay()
            for objects in loaded_objects:
                tiles = scene.getObjectByName("tile")
                scene.remove(tiles)          
    # bugfix: delay calculation of voxels
    # first update delay
    elif firstupdate <= 1:
        firstupdate += 1
        if firstupdate == 2:
            firstupdate += 1
            generate_grid()
            final_values() 
            changelog()
            generate_geometry()
    # undo, redo, reset delay
    elif updater <= 1:
        updater += 1
        if updater == 2:
            updater += 1
            generate_grid()
            final_values() 
            if filling != "No Infill":
                generate_geometry()
    # new attractor delay
    elif delay <= 1:
        delay += 1
        if delay == 2:
            delay += 1 
            final_values() 
            changelog()
            if filling != "No Infill":
                generate_geometry()
    count_geometry()
                
# reset scene
def reset(event):
    camera.position.x = -45
    camera.position.y = 15
    camera.position.z = 30
    # remove attractors and controlls
    global attractors, strengths_update, attractors_and_controls, firstupdate, history, future, selection, attractor_strengths
    for both in  attractors_and_controls:
        both[1].detach(both[0])
        scene.remove(both[0])
        scene.remove(both[1])
    
    attractors = []
    attractors_and_controls = []
    strengths_update = 0

    # initial_attractos
    generate_attractor(3, -3.5, 3)
    generate_attractor(-3, 3.5, -3)

    # reset GUI values and update GUI
    grid_params.grid_scale_x = 15
    grid_params.grid_scale_y = 15
    grid_params.grid_scale_z = 15
    grid_params.wireframe = False
    grid_params.hide_voxels = False
    attractor_params.limit = 0.65
    attractor_params.set_strength = True
    
    param1.updateDisplay()
    param2.updateDisplay()
    param3.updateDisplay()
    #param4.updateDisplay()
    param5.updateDisplay()
    param6.updateDisplay()

    history = []
    future = []
    for both in attractors_and_controls:
        del attractor_strengths[0]
    firstupdate = 0

# undo change
def undo(event):
    console.log("reset works!-")
    global attractors, attractors_and_controls, updater, history, future
    if len(history) >= 2:
        i = len(history) - 2

        for both in attractors_and_controls:
            both[1].detach(both[0])
            scene.remove(both[0])
            scene.remove(both[1])

            attractors = []
            attractors_and_controls = []

        for attractor in history[i][0]:
            generate_attractor(attractor.x, attractor.y, attractor.z)

        global grid_scale_x, grid_scale_y, grid_scale_z, wireframe_base, hide_voxels, attractor_limit

        grid_scale_x = history[i][1]
        grid_params.grid_scale_x = history[i][1]

        grid_scale_y = history[i][2]
        grid_params.grid_scale_y = history[i][2]

        grid_scale_z = history[i][3]
        grid_params.grid_scale_z = history[i][3]

        #wireframe_base = history[i][4]
        #grid_params.wireframe = history[i][4]

        hide_voxels = history[i][5]
        grid_params.hide_voxels = history[i][5]

        attractor_limit = history[i][6]
        attractor_params.limit = history[i][6]

        param1.updateDisplay()
        param2.updateDisplay()
        param3.updateDisplay()
        #param4.updateDisplay()
        param5.updateDisplay()
        param6.updateDisplay()
        
        future.append(history.pop(i+1))

        for both in attractors_and_controls:
            del attractor_strengths[-1]
        # update 
        updater = 0
    else: 
        pass

# redo change
def redo(event):
    global attractors, attractors_and_controls, updater, history, future
    if len(future) > 0:
        i = len(future) - 1

        for both in attractors_and_controls:
            both[1].detach(both[0])
            scene.remove(both[0])
            scene.remove(both[1])

            attractors = []
            attractors_and_controls = []

        for attractor in future[i][0]:
            generate_attractor(attractor.x, attractor.y, attractor.z)

        global grid_scale_x, grid_scale_y, grid_scale_z, wireframe_base, hide_voxels, attractor_limit

        grid_scale_x = future[i][1]
        grid_params.grid_scale_x = future[i][1]

        grid_scale_y = future[i][2]
        grid_params.grid_scale_y = future[i][2]

        grid_scale_z = future[i][3]
        grid_params.grid_scale_z = future[i][3]

        #wireframe_base = future[i][4]
        #grid_params.wireframe = future[i][4]

        hide_voxels = future[i][5]
        grid_params.hide_voxels = future[i][5]

        attractor_limit = future[i][6]
        attractor_params.limit = future[i][6]

        param1.updateDisplay()
        param2.updateDisplay()
        param3.updateDisplay()
        #param4.updateDisplay()
        param5.updateDisplay()
        param6.updateDisplay()
        
        history.append(future.pop(i)) 
        for both in attractors_and_controls:
            del attractor_strengths[-1]
        # update 
        updater = 0
    else: 
        pass

# store last changes in list
def changelog():
    global history, attractor_positions, grid_scale_x, grid_scale_y, grid_scale_z, wireframe_base, hide_voxels, attractor_limit, attractor_strengths, future
    future = []
    changes = []
    changes.append(attractor_positions)
    changes.append(grid_scale_x)
    changes.append(grid_scale_y)
    changes.append(grid_scale_z)
    changes.append(wireframe_base)
    changes.append(hide_voxels)
    changes.append(attractor_limit)

    if len(history) > 5:
        history.pop(0)

    history.append(changes)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------  
# ATTRACTORS
# add_attractor
def Add_attractor(event):
    global delay, attractor_strengths
    xr = random.randint(round(-0.45*grid_scale_x,0), round(0.45*grid_scale_x,0))
    yr = random.randint(round(-0.45*grid_scale_y,0), round(0.45*grid_scale_y,0))
    zr = random.randint(round(-0.45*grid_scale_z,0), round(0.45*grid_scale_z,0))
    generate_attractor(xr, yr, zr)
    delay = 0

# create attractor point
def generate_attractor(x, y, z):
    global attractors, attractors_and_controls, tf_control, strengths_update
    both = []
    #  random color material
    r = random.random()
    g = random.random()
    b = random.random()
    material_attractor = THREE.MeshBasicMaterial.new()
    material_attractor.color = THREE.Color.new(r, g, b)

    sphere_geom = THREE.SphereGeometry.new(0.5,20,10)
    sphere = THREE.Mesh.new(sphere_geom, material_attractor)
    scene.add(sphere)
    spheres.append(sphere)
    attractors.append(sphere)

    # controls
    tf_control = THREE.TransformControls.new(camera, renderer.domElement)
    tf_control.size = gumball_size
    tf_control.addEventListener('mouseDown', mouse_down )
    tf_control.addEventListener('mouseUp', mouse_up )
        
    sphere.translateX(x)
    sphere.translateY(y)
    sphere.translateZ(z)

    attractor_strength = 2.6
    attractor_strengths.append(attractor_strength)

    both.append(sphere)
    both.append(tf_control)
    attractors_and_controls.append(both)
    
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------  
# EVENTS
# STRENGTH    
def LessStrength(event):
    global str, attractor_strengths, strengths_update
    keyName = event.key
    if attractor_params.set_strength == True:
        #if the list is not empty, you do the same but only for specific str 
        if keyName == '-':
                id = selected_spheres[-1]
                str = attractor_strengths[id]
                  
                attractor_strength2 =   str - 0.06
                if attractor_strength2 <= 0:
                    attractor_strength2 = 0.06
                
                console.log(attractor_strength2, "str new5", id)
            
                ValueStr.append(attractor_strength2)

                attractor_strengths[id] = ValueStr[-1]   
                #print(attractor_strengths)     
                strengths_update = 1  
                              
def MoreStrength(event):  
    global str, attractor_strengths, strengths_update 
    keyName = event.key
    if attractor_params.set_strength == True:
        if keyName == '+': 
            id = selected_spheres[-1]
            str = attractor_strengths[id]
            #console.log(str, "str+", id)
            attractor_strength2 =   str + 0.06
            console.log(attractor_strength2, "str new5", id)
            if attractor_strength2 >= 6.0:
                attractor_strength2 = 5.94
        
            ValueStr.append(attractor_strength2)

            attractor_strengths[id] = ValueStr[-1]     
            #print(attractor_strengths)           
            strengths_update = 1  
                   
def Sphereactivation(event):
    if attractor_params.set_strength == True:
        event.preventDefault()
        global spheres, tf_control, object, mouse, object, selected_spheres
        mouse.set((event.clientX/window.innerWidth)*2-1, -(event.clientY/window.innerHeight)*2+1)
        raycaster.setFromCamera(mouse, camera)
        for s in spheres:
            js_objects = to_js(s)
            intersects = raycaster.intersectObject(js_objects, True)
            id = spheres.index(s)
            
            if len(intersects) != 0:
                object = intersects[0].object
                console.log("found")   
                selection.append(object)
                        
                if id in selected_spheres:
                    selected_spheres.pop(id )
               
                if id not in selected_spheres:
                    selected_spheres.append(id)
    
    else:
        for both in attractors_and_controls:
            both[1].detach(both[0])
            
def SphereClick(event):
    if attractor_params.set_strength == True:
        for object in selection:   
            tf_control.attach(object)
            scene.add(tf_control)
    if attractor_params.set_strength == False:
        for both in attractors_and_controls:
            both[1].detach(both[0])

# hide the gumball, when mouse moves around and no key is pressed
def Mousemove(event):
    for both in attractors_and_controls:
        both[1].detach(both[0])
    window.removeEventListener('dblclick', add_attractor) 

# show the gumball while dragging
def Dragging(event):
    keyName = event.key
    if keyName == 'a':

        for both in attractors_and_controls:
            both[1].attach(both[0])
            scene.add(both[1])     

        window.addEventListener('dblclick', add_attractor)  
     
# orbitcontrols toggle while transformcontrols(on/off)
def deactivate_o_controls(event):
    global controls
    controls.enabled = False

def activate_o_controls(event):
    global controls, infi
    controls.enabled = True
    
    final_values()
    changelog()
    if filling != "No Infill":
        generate_geometry()

# create timer that resets when mouse is moving (otherwiese refresh scene)   
def reload_timer(event):
    global last_time
    last_time = datetime.datetime.now()

def timer_checker():
    global last_time
    now = datetime.datetime.now()
    difference = now - last_time
    delta = timedelta(seconds=180)
    if difference > delta:
        window.location.reload()
        last_time = datetime.datetime.now()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------  
# RENDER
# simple render and animate
def render(*args):
    window.requestAnimationFrame(create_proxy(render))
    controls.update()
    update()
    composer.render()
    timer_checker()

# graphical post-processing
def post_process():
    render_pass = THREE.RenderPass.new(scene, camera)
    render_pass.clearColor = THREE.Color.new(0,0,0)
    render_pass.ClearAlpha = 0
    fxaa_pass = THREE.ShaderPass.new(THREE.FXAAShader)

    pixelRatio = window.devicePixelRatio

    fxaa_pass.material.uniforms.resolution.value.x = 1 / ( window.innerWidth * pixelRatio )
    fxaa_pass.material.uniforms.resolution.value.y = 1 / ( window.innerHeight * pixelRatio )
   
    global composer
    composer = THREE.EffectComposer.new(renderer)
    composer.addPass(render_pass)
    composer.addPass(fxaa_pass)

# adjust display when window size changes
def on_window_resize(event):

    event.preventDefault()

    global renderer
    global camera
    
    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()

    renderer.setSize( window.innerWidth, window.innerHeight )

    #post processing after resize
    post_process()
#-----------------------------------------------------------------------
#RUN THE MAIN PROGRAM
if __name__=='__main__':
    main()
