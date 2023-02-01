#¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨#
#            SIMULATION STOP            #
#.......................................#
time.stop_time               =   22000.0     # Max (simulated) time to evolve
time.max_step                =   1000        # Max number of time steps

#¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨#
#         TIME STEP COMPUTATION         #
#.......................................#
time.fixed_dt         =   1.0          # Use this constant dt if > 0
time.cfl              =   0.95         # CFL factor

#¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨#
#            INPUT AND OUTPUT           #
#.......................................#
io.outputs = actuator_src_term
time.plot_interval            =  25       # Steps between plot files
time.checkpoint_interval      =  -5       # Steps between checkpoint files

#¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨#
#               PHYSICS                 #
#.......................................#
incflo.gravity          =   0.  0. -9.81  # Gravitational force (3D)
incflo.density             = 1.0          # Reference density 
incflo.use_godunov = 1
incflo.godunov_type = "weno"
transport.viscosity = 1.0e-5
transport.laminar_prandtl = 0.7
transport.turbulent_prandtl = 0.3333
turbulence.model = Smagorinsky
Smagorinsky_coeffs.Cs = 0.135


incflo.physics = ABL Actuator
ICNS.source_terms = BoussinesqBuoyancy CoriolisForcing ABLForcing ActuatorForcing
BoussinesqBuoyancy.reference_temperature = 300.0
ABL.reference_temperature = 300.0
CoriolisForcing.latitude = 41.3
ABLForcing.abl_forcing_height = 90

incflo.velocity = 6.128355544951824  5.142300877492314 0.0

ABL.temperature_heights = 650.0 750.0 1000.0
ABL.temperature_values = 300.0 308.0 308.75

ABL.kappa = .41
ABL.surface_roughness_z0 = 0.15

Actuator.labels = WTG01 WTG02
Actuator.type = UniformCtDisk
Actuator.UniformCtDisk.rotor_diameter = 126.0
Actuator.WTG01.base_position = 250.0 475.0 0.0
Actuator.UniformCtDisk.hub_height = 90.0
Actuator.UniformCtDisk.yaw = 270.0 # degrees (yaw is relative to north which defaults to {0,1,0})
Actuator.UniformCtDisk.sample_yaw = 270.0 # set velocity sampling to be in the normal flow direction
Actuator.UniformCtDisk.num_force_points = 5
Actuator.UniformCtDisk.thrust_coeff = 0.0 0.7 1.2
Actuator.UniformCtDisk.wind_speed = 0.0 10.0 12.0
Actuator.UniformCtDisk.epsilon = 50.0
Actuator.UniformCtDisk.density = 1.225
Actuator.UniformCtDisk.diameters_to_sample = 1.0
Actuator.UniformCtDisk.num_vel_points_r = 3
Actuator.UniformCtDisk.num_vel_points_t = 3

Actuator.UniformCtDisk.rotor_diameter = 126.0
Actuator.WTG02.base_position = 750.0 525.0 0.0
Actuator.UniformCtDisk.hub_height = 90.0
Actuator.UniformCtDisk.yaw = 270.0 # degrees (yaw is relative to north which defaults to {0,1,0})
Actuator.UniformCtDisk.sample_yaw = 270.0 # set velocity sampling to be in the normal flow direction
Actuator.UniformCtDisk.num_force_points = 5
Actuator.UniformCtDisk.thrust_coeff = 0.0 0.7 1.2
Actuator.UniformCtDisk.wind_speed = 0.0 10.0 12.0
Actuator.UniformCtDisk.epsilon = 50.0
Actuator.UniformCtDisk.density = 1.225
Actuator.UniformCtDisk.diameters_to_sample = 1.0
Actuator.UniformCtDisk.num_vel_points_r = 3
Actuator.UniformCtDisk.num_vel_points_t = 3

#¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨#
#        ADAPTIVE MESH REFINEMENT       #
#.......................................#
amr.n_cell              = 96 96 96    # Grid cells at coarsest AMRlevel
amr.max_level           = 0           # Max AMR level in hierarchy 

#¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨#
#              GEOMETRY                 #
#.......................................#
geometry.prob_lo        =   0.       0.     0.  # Lo corner coordinates
geometry.prob_hi        =   1000.  1000.  1000.  # Hi corner coordinates
geometry.is_periodic    =   1   1   0   # Periodicity x y z (0/1)

# Boundary conditions
zlo.type =   "wall_model"

zhi.type =   "slip_wall"
zhi.temperature_type = "fixed_gradient"
zhi.temperature = 0.003 # tracer is used to specify potential temperature gradient

#¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨#
#              VERBOSITY                #
#.......................................#
incflo.verbose          =   0          # incflo_level


#¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨#
#              SAMPLING                 #
#.......................................#
incflo.post_processing = sampling

# Frequency of output for the data
sampling.output_frequency = 1

sampling.labels = z_plane
# Fields to output
sampling.fields = velocity
# Definitions for each probe
sampling.z_plane.type = PlaneSampler
sampling.z_plane.axis1 = 1000.0 0.0 0.0
sampling.z_plane.axis2 = 0.0 1000.0 0.0
sampling.z_plane.origin = 0.0 0.0 0.0
sampling.z_plane.num_points = 96 96
sampling.z_plane.normal = 0.0 0.0 1.0
sampling.z_plane.offsets = 90.0
