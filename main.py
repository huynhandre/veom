 # Import javascript modules
from js import THREE, window, document, Object, console
# Import pyscript / pyodide modules
from pyodide.ffi import create_proxy, to_js
# Import python module
import math
#-----------------------------------------------------------------------
# USE THIS FUNCTION TO WRITE THE MAIN PROGRAM
def main():
    #-----------------------------------------------------------------------
    # VISUAL SETUP
    # Declare the variables
    global renderer, scene, camera, controls,composer
    
    #Set up the renderer
    renderer = THREE.WebGLRenderer.new()
    renderer.setPixelRatio( window.devicePixelRatio )
    renderer.setSize(window.innerWidth, window.innerHeight)
    document.body.appendChild(renderer.domElement)

    # Set up the scene

    scene = THREE.Scene.new()
    back_color = THREE.Color.new(0.9,0.9,0.9)
    primary_color = THREE.Color.new(0.15,0.45,0.5)
    scene.background = back_color
    width = window.innerWidth
    height = window.innerHeight
    camera = THREE.PerspectiveCamera.new(30, width/height, 0.1, 1000)
    camera.position.z = 13
    camera.position.y = 10
    camera.position.x = 13
    scene.add(camera)

    # Graphic Post Processing
    global composer
    post_process()

    # Set up responsive window
    resize_proxy = create_proxy(on_window_resize)
    window.addEventListener('resize', resize_proxy) 

    # Set up Mouse orbit control
    controls = THREE.OrbitControls.new(camera, renderer.domElement)

    #---------------------------------------------------------------------------------------------------------------------------------------------------------------
    # YOUR DESIGN / GEOMETRY GENERATION

    # CREATE ATTRACTORS
    # meshes, material
    global sphere1, sphere2
    material_attractor_red = THREE.MeshBasicMaterial.new()
    material_attractor_red.color = THREE.Color.new(255, 0, 0)

    material_attractor_yellow = THREE.MeshBasicMaterial.new()
    material_attractor_yellow.color = THREE.Color.new(255, 255, 0)


    sphere_geom1 = THREE.SphereGeometry.new(0.15,20,10)
    sphere_geom2 = THREE.SphereGeometry.new(0.15,20,10)
    
    sphere1 = THREE.Mesh.new(sphere_geom1, material_attractor_red)
    scene.add(sphere1)

    

    sphere2 = THREE.Mesh.new(sphere_geom2, material_attractor_yellow)
    scene.add(sphere2)

    # Mouse Events for TransformControls
    mouse_down = create_proxy(deactivate_o_controls)
    mouse_up = create_proxy(activate_o_controls)

    # add TransformControls
    gumball_size = 0.6
    controls.enabled = True
    tf_controls = THREE.TransformControls.new(camera, renderer.domElement)
    tf_controls.size = gumball_size
    tf_controls.addEventListener('mouseDown', mouse_down )
    tf_controls.addEventListener('mouseUp', mouse_up )
    tf_controls.attach(sphere1)

    sphere1.translateX(-2.5)
    sphere1.translateY(1)
    scene.add(tf_controls)

    tf_controls_2 = THREE.TransformControls.new(camera, renderer.domElement)
    tf_controls_2.size = gumball_size
    tf_controls_2.addEventListener('mouseDown', mouse_down )
    tf_controls_2.addEventListener('mouseUp', mouse_up )
    tf_controls_2.attach(sphere2)

    sphere2.translateX(2)
    sphere2.translateY(-0.5)
    scene.add(tf_controls_2)
    
    # origin for orientation
    point = THREE.BufferGeometry.new()
    vertices = []
    x = 0
    y = 0
    z = 0
    vertices.append(x)
    vertices.append(y)
    vertices.append(z)
    point.setAttribute('position',THREE.Float32BufferAttribute.new( vertices, 3 ))
    pointmaterial = THREE.PointsMaterial.new()
    pointmaterial.color = THREE.Color.new(355,0,0)
    pointmaterial.size = 0.2
    origin = THREE.Points.new(point, pointmaterial)
    scene.add(origin)
    
    # define the grid params
    global grid_params, grid_count, grid_scale_x, grid_scale_y, grid_scale_z, wireframe_base, voxel_centers, hide_voxels
    grid_count = 10
    grid_scale_x = 5
    grid_scale_y = 5
    grid_scale_z = 5
    wireframe_base = False
    voxel_centers = False
    hide_voxels = False

    grid_params = {
            "density":grid_count,
            "grid_scale_x":grid_scale_x,
            "grid_scale_y":grid_scale_y,
            "grid_scale_z":grid_scale_z,
            "wireframe": wireframe_base,
            "voxel_centers": voxel_centers,
            "hide_voxels": hide_voxels
    }
        
    grid_params = Object.fromEntries(to_js(grid_params))

    #define attractor params
    global attractor_params, attractor_1_strength, attractor_2_strength, attractor_limit
    attractor_limit = 0.5
    attractor_1_strength = 2.6
    attractor_2_strength= 2.6
    
    lock_points = False

    attractor_params = {
            "limit": attractor_limit,
            "red_strength": attractor_1_strength,
            "yellow_strength": attractor_2_strength,
            "lock_points": lock_points
    }

    attractor_params = Object.fromEntries(to_js(attractor_params))

    # create a THREE.js voxel  material
    global material, material_center, line_material
    material = THREE.MeshBasicMaterial.new()
    material.color = primary_color
    material.transparent = True
    material.opacity = 0.15

    # create a THREE.js center material
    material_center = THREE.MeshBasicMaterial.new()
    material_center.color = primary_color

    # create a THREE.js line material 
    line_material = THREE.LineBasicMaterial.new()
    line_material.color = primary_color

    # create a voxel at each node of the grid, store position in vector3
    global voxel_values, voxel_list, sphere_list, wireframe_list, voxel_position, boundary

    voxel_list = []
    sphere_list = []
    wireframe_list = []

    voxel_position = []
    voxel_values = []

    boundary = []

    # set up GUI
    gui = window.dat.GUI.new()
    param_folder = gui.addFolder('Grid Parameters')
    param_folder.add(grid_params, 'density', 2,20,1)
    param_folder.add(grid_params, 'grid_scale_x', 1,10,1)
    param_folder.add(grid_params, 'grid_scale_y', 1,10,1)
    param_folder.add(grid_params, 'grid_scale_z', 1,10,1)
    param_folder.add(grid_params, 'wireframe')
    param_folder.add(grid_params, 'voxel_centers')
    param_folder.add(grid_params, 'hide_voxels')
    param_folder.open()

    param_folder = gui.addFolder('Attractor')
    param_folder.add(attractor_params, 'limit', 0, 1)
    param_folder.add(attractor_params, 'red_strength', 1, 5, 0.1)
    param_folder.add(attractor_params, 'yellow_strength', 1, 5, 0.1)
    param_folder.add(attractor_params, 'lock_points')
    param_folder.open()

    #IMPLEMENT
    global firstupdate
    firstupdate = 0
    render()
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------

# create a voxel at each node of the grid
def generate_voxel():

    # remove all voxels
    for wireframe in wireframe_list:
        scene.remove(wireframe)
    for sphere in sphere_list:
        scene.remove(sphere)
    for voxel in voxel_list:
        scene.remove(voxel)
    
    store_parameters()
    generate_boundary()

    #create voxels
    geometry = THREE.BoxGeometry.new(grid_scale_x / grid_count, grid_scale_y / grid_count, grid_scale_z / grid_count) #calculate voxel sizes

    geometry_center_scaler = (((grid_scale_x + grid_scale_y + grid_scale_z) / 3) / grid_count) * 0.1 # calculate the average grid scale and adjust point size accordingly
    geometry_center = THREE.SphereGeometry.new(geometry_center_scaler, 10, 10) 
    
    for i in range(grid_count):
        for j in range(grid_count):
            for k in range(grid_count):

                voxel = THREE.Mesh.new(geometry, material)
                sphere = THREE.Mesh.new(geometry_center, material_center)
        
                geometry_wireframe = THREE.EdgesGeometry.new(voxel.geometry)
                wireframe = THREE.LineSegments.new(geometry_wireframe, line_material)
                    
                # position Voxels and center spheres
                # position - 1/2 of grid size + 1/2 of voxel size 
                pos_x = ((i / grid_count) * grid_scale_x) - (grid_scale_x / 2) + (grid_scale_x/grid_count/2)
                pos_y = ((j / grid_count) * grid_scale_y) - (grid_scale_y / 2) + (grid_scale_y/grid_count/2)
                pos_z = ((k / grid_count) * grid_scale_z) - (grid_scale_z / 2) + (grid_scale_z/grid_count/2)
                
                voxel.position.set(pos_x, pos_y, pos_z)
                sphere.position.set(pos_x, pos_y, pos_z)
                wireframe.position.set(pos_x, pos_y, pos_z)

                voxel_list.append(voxel)
                sphere_list.append(sphere)
                wireframe_list.append(wireframe)
                
                position = THREE.Vector3.new(pos_x, pos_y, pos_z)
                voxel_position.append(position)

                if hide_voxels == False:
                    if wireframe_base == True:
                        scene.add(wireframe)
                    else:
                        scene.add(voxel) 
                if voxel_centers == True:
                    scene.add(sphere)

# store parameters, reset lists              
def store_parameters():
    global voxel_list, sphere_list, wireframe_list, voxel_position
    global grid_params, grid_count, grid_scale_x, grid_scale_y, grid_scale_z, wireframe_base, voxel_centers, hide_voxels

    wireframe_list = []
    sphere_list = []
    voxel_list = []
    
    voxel_position = []

    grid_count = grid_params.density
    grid_scale_x = grid_params.grid_scale_x
    grid_scale_y = grid_params.grid_scale_y
    grid_scale_z = grid_params.grid_scale_z
    wireframe_base = grid_params.wireframe
    voxel_centers = grid_params.voxel_centers
    hide_voxels = grid_params.hide_voxels

#create boundary
def generate_boundary():
    global boundary
    for boundary_edge in boundary:
        scene.remove(boundary_edge)

    geometry_boundary = THREE.BoxGeometry.new(grid_scale_x, grid_scale_y, grid_scale_z)
    boundary = THREE.Mesh.new(geometry_boundary, material)
    geometry_edge = THREE.EdgesGeometry.new(boundary.geometry)
    boundary_edge = THREE.LineSegments.new(geometry_edge, line_material)
    scene.add(boundary_edge)

    boundary = []
    boundary.append(boundary_edge)
    
# attractor coordinates
def getcenter(sphere):
    geometry = sphere.geometry
    geometry.computeBoundingBox()
    center = THREE.Vector3.new()
    geometry.boundingBox.getCenter(center)
    sphere.localToWorld(center)

    return center

# calculate values in relation to distance
def individual_values(attractor, attractor_strength):
    global voxel_position
    distances = []
    values = []
    
    # get distance between attractor and voxel
    for position in voxel_position:
        distance = position.distanceTo(attractor)    
        distances.append(distance)
       
    # calculate the voxels value   
    for d in distances:
        value = (max(distances) - d)**attractor_strength
        values.append(value)

    return values

def final_values():
    global voxel_values, voxel_list, sphere_list, wireframe_list
    #get current attractor positon
    attractor1 = getcenter(sphere1)
    attractor2 = getcenter(sphere2)

    #calculate values for every attractor and store in list
    attractor1_values = []
    attractor2_values = []
    voxel_values = []

    attractor1_values = individual_values(attractor1, attractor_params.red_strength)
    attractor2_values = individual_values(attractor2, attractor_params.yellow_strength)
    
    #calculate the final value
    voxel_values = [x + y for x, y in zip(attractor1_values, attractor2_values)]

    console.log(max(voxel_values))
    limit = max(voxel_values) - max(voxel_values)*attractor_params.limit
    index = -1

    for value in voxel_values:
        index += 1
        if value <= limit:
            if hide_voxels == False:
                if wireframe_base == True:
                    scene.remove(wireframe_list[index])
                else:
                    scene.remove(voxel_list[index])
            if voxel_centers == True:
                scene.remove(sphere_list[index])
        else: 
            pass  

def rebuild_voxel():
    if voxel_centers == True:
        for sphere in sphere_list:
            scene.remove(sphere)
        for sphere in sphere_list:
            scene.add(sphere)   

    if hide_voxels == False:
        if wireframe_base == True:
            for wireframe in wireframe_list:
                scene.remove(wireframe)
            for wireframe  in wireframe_list:
                scene.add(wireframe) 
        else:
            for voxel in voxel_list:
                scene.remove(voxel)
            for voxel in voxel_list:
                scene.add(voxel)   

# position acctractors relative to grid
def position_attractors():
    if attractor_params.lock_points == False:
        global sphere1, sphere2, grid_scale_x, grid_params

        attractor_1_pos = THREE.Vector3.new()
        sphere1.getWorldPosition(attractor_1_pos)

        attractor_2_pos = THREE.Vector3.new()
        sphere2.getWorldPosition(attractor_2_pos)

        # get value for relative position on every axis for every point
        # Attractor 1
        relative_pos_x_1 = attractor_1_pos.x / (grid_scale_x)
        relative_pos_y_1 = attractor_1_pos.y / (grid_scale_y)
        relative_pos_z_1 = attractor_1_pos.z / (grid_scale_z)
        # Attractor 2
        relative_pos_x_2 = attractor_2_pos.x / (grid_scale_x)
        relative_pos_y_2 = attractor_2_pos.y / (grid_scale_y)
        relative_pos_z_2 = attractor_2_pos.z / (grid_scale_z)

        # move the attractors when scaling
        if grid_scale_x != grid_params.grid_scale_x:

            sphere1.translateX((relative_pos_x_1 * grid_params.grid_scale_x) - attractor_1_pos.x)
            sphere2.translateX((relative_pos_x_2 * grid_params.grid_scale_x) - attractor_2_pos.x)
    
        if grid_scale_y != grid_params.grid_scale_y:
    
            sphere1.translateY((relative_pos_y_1 * grid_params.grid_scale_y) - attractor_1_pos.y)
            sphere2.translateY((relative_pos_y_2 * grid_params.grid_scale_y) - attractor_2_pos.y)

        if grid_scale_z != grid_params.grid_scale_z:

            sphere1.translateZ((relative_pos_z_1 * grid_params.grid_scale_z) - attractor_1_pos.z)
            sphere2.translateZ((relative_pos_z_2 * grid_params.grid_scale_z) - attractor_2_pos.z)


# Update
def update():
    global attractor_limit, attractor_1_strength, attractor_2_strength, firstupdate
    #if grid changes
    if grid_count != grid_params.density or wireframe_base != grid_params.wireframe or grid_params.voxel_centers != voxel_centers or hide_voxels != grid_params.hide_voxels:
        generate_voxel()
        final_values()    
    elif attractor_limit != attractor_params.limit or attractor_1_strength != attractor_params.red_strength or attractor_2_strength != attractor_params.yellow_strength: 
        attractor_limit = attractor_params.limit 
        attractor_1_strength = attractor_params.red_strength
        attractor_2_strength = attractor_params.yellow_strength
        rebuild_voxel()
        final_values()
    elif grid_scale_x != grid_params.grid_scale_x or grid_scale_y != grid_params.grid_scale_y or grid_scale_z != grid_params.grid_scale_z:
        position_attractors()
        generate_voxel()
        final_values()
    #first update
    elif firstupdate <= 1:
        firstupdate += 1
        if firstupdate == 2:
            firstupdate +=1
            generate_voxel()
            final_values() 
    else:
        pass

# OrbitControls Toggle while TransformControls(On/Off)
def deactivate_o_controls(event):
    global controls
    controls.enabled = False

def activate_o_controls(event):
    global controls
    controls.enabled = True
    rebuild_voxel()
    final_values()

# Simple render and animate
def render(*args):
    window.requestAnimationFrame(create_proxy(render))
    controls.update()
    update()
    #renderer.render(scene, camera)
    composer.render()

# Graphical post-processing
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

# Adjust display when window size changes
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