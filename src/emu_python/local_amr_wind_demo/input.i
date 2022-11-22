# --- Simulation time control parameters ---
time.stop_time                           = 1000000000.0             # Max (simulated) time to evolve [s]
time.max_step                            = 1000000000              
time.fixed_dt                            = 1.0                 # Fixed timestep size (in seconds). If negative, then time.cfl is used
time.checkpoint_interval                 = -2000                
incflo.physics                           = ABL Actuator        # List of physics models to include in simulation.
incflo.verbose                           = 3                  
io.check_file                            = chk                 
#io.restart_file                         = chk80000/           
incflo.use_godunov                       = true                
incflo.godunov_type                      = weno_z              
incflo.diffusion_type                    = 1                   # Type of diffusion scheme used.  0 = explicit diffusion, 1 = Crank-Nicolson, 2 = fully implicit
turbulence.model                         = Smagorinsky        
nodal_proj.mg_rtol                       = 1e-03               
nodal_proj.mg_atol                       = 1e-12               
mac_proj.mg_rtol                         = 1e-04               
mac_proj.mg_atol                         = 1e-12               
diffusion.mg_rtol                        = 1e-06               
diffusion.mg_atol                        = 1e-12               
temperature_diffusion.mg_rtol            = 1e-8               
temperature_diffusion.mg_atol            = 1e-12               
incflo.gravity                           = 0.0 0.0 -9.81       # Gravitational acceleration vector (x,y,z) [m/s^2]
incflo.density                           = 1.0                 # Fluid density [kg/m^3]
transport.viscosity                      = 1.5e-05             # Fluid dynamic viscosity [kg/m-s]
transport.laminar_prandtl                = 0.7                 # Laminar prandtl number
transport.turbulent_prandtl              = 0.3333              # Turbulent prandtl number
incflo.initial_iterations                = 0
incflo.do_initial_proj                   = 0

# --- Geometry and Mesh ---
geometry.prob_lo                         = -3200.0 -3200.0 0.0 
geometry.prob_hi                         = 3200.0 3200.0 1920.0
amr.n_cell                               = 320 320 96 # 160 160 48 #640 640 192         # Number of cells in x, y, and z directions
#amr.n_cell                               = 80 80 24 #640 640 192         # Number of cells in x, y, and z directions
amr.max_level                            = 0                   
geometry.is_periodic                     = 0 0 0               
xlo.type                                 = mass_inflow         
xlo.density                              = 1.0                 
xlo.temperature                          = 0.0                 
xhi.type                                 = pressure_outflow    
ylo.type                                 = mass_inflow         
ylo.density                              = 1.0                 
ylo.temperature                          = 0.0                 
yhi.type                                 = pressure_outflow    
zlo.type                                 = wall_model          
zlo.temperature_type                     = wall_model          
zlo.tke_type                             = zero_gradient       
zhi.type                                 = slip_wall           
zhi.temperature_type                     = fixed_gradient      
zhi.temperature                          = 0.003               

# --- ABL parameters ---
ICNS.source_terms                        = ActuatorForcing  BoussinesqBuoyancy ABLMeanBoussinesq # ABLForcing # BoussinesqBuoyancy ABLMeanBoussinesq
incflo.velocity                          = 8.0 0.0 0.0 # 6.36396103068 6.36396103068 0.0
ABLForcing.abl_forcing_height            = 150.0               
ABL.kappa                                = 0.4                 
ABL.normal_direction                     = 2                   
ABL.surface_roughness_z0                 = 0.0001              
ABL.reference_temperature                = 300.0               
ABL.surface_temp_rate                    = 0.0                 
ABL.surface_temp_flux                    = 0.0                 # Surface temperature flux [K-m/s]
ABL.mo_beta_m                            = 16.0                # Monin-Obukhov Beta m parameter
ABL.mo_gamma_m                           = 5.0                 # Monin-Obukhov Gamma m parameter
ABL.mo_gamma_h                           = 5.0                 # Monin-Obukhov Gamma h parameter
ABL.random_gauss_mean                    = 0.0                 
ABL.random_gauss_var                     = 1.0                 
BoussinesqBuoyancy.reference_temperature = 300.0               
ABL.temperature_heights                  = 0     750.0  850.0 1920.0
ABL.temperature_values                   = 300.0 300.0  301.0 304.21
time.plot_interval                       = 2000                
io.plot_file                             = plt                 
io.KE_int                                = -1                  
incflo.post_processing                   = sampling            


MPL.activate = true
MPL.zref = 90.0
MPL.shear_exp = 0.1
MPL.umax_factor = 1.2
MPL.bulk_velocity = 9.0
MPL.shearlayer_height = 1000.0
MPL.shearlayer_smear_thickness = 50.0
MPL.wind_speed = 8.0
MPL.wind_direction = 250.0
MPL.start_time = 0.0
MPL.degrees_per_second = 0.02
MPL.deltaT = 1.0
MPL.theta_cutoff_height = 300.0


# --- Sampling parameters ---
sampling.output_frequency                = 1                 
sampling.fields                          = velocity temperature

#---- sample defs ----
sampling.labels                          = p_hub               
sampling.p_hub.type                      = PlaneSampler        
sampling.p_hub.num_points                = 321 321 # 161 161             
sampling.p_hub.origin                    = -3200.0 -3200.0 0.0 
sampling.p_hub.axis1                     = 6400.0 0.0 0.0      
sampling.p_hub.axis2                     = 0.0 6400.0 0.0      
sampling.p_hub.normal                    = 0.0 0.0 1.0         
sampling.p_hub.offsets                   = 0.0 0.0 90.0    
     

#---- actuator defs ----
Actuator.type = UniformCtDisk
Actuator.UniformCtDisk.rotor_diameter = 126.0
Actuator.UniformCtDisk.hub_height = 90.0
Actuator.UniformCtDisk.thrust_coeff = 0.0 0.7 1.2
Actuator.UniformCtDisk.wind_speed = 0.0 10.0 12.0
Actuator.UniformCtDisk.epsilon = 10.0
Actuator.UniformCtDisk.density = 1.225
Actuator.UniformCtDisk.diameters_to_sample = 1.0
Actuator.UniformCtDisk.num_points_r = 20
Actuator.UniformCtDisk.num_points_t = 5



# Actuator.type                              = JoukowskyDisk       
Actuator.labels                            = T00 T01 T02 T03 T04 T05 T06 T07
Actuator.JoukowskyDisk.thrust_coeff        = 8.1672e-01 7.9044e-01 7.8393e-01 7.8624e-01 7.8824e-01 7.8942e-01 7.8902e-01 7.8740e-01 7.8503e-01 7.8237e-01 7.7955e-01 7.7583e-01 7.7583e-01 7.7583e-01 7.7583e-01 7.7583e-01 7.7583e-01 7.7583e-01 7.7583e-01 7.7583e-01 7.7583e-01 7.7583e-01 7.7583e-01 7.7583e-01 7.7583e-01 7.7583e-01 7.7583e-01 7.7583e-01 7.6922e-01 7.4270e-01 5.5949e-01 4.6163e-01 3.8786e-01 3.2901e-01 2.8093e-01 2.4114e-01 2.0795e-01 1.8010e-01 1.5663e-01 1.3679e-01 1.1995e-01 1.0562e-01 9.3384e-02 8.2908e-02 7.3910e-02 6.6159e-02 5.9463e-02 5.3662e-02 4.8622e-02 4.4230e-02
Actuator.JoukowskyDisk.wind_speed          = 3.0000e+00 3.5495e+00 4.0679e+00 4.5539e+00 5.0064e+00 5.4244e+00 5.8069e+00 6.1530e+00 6.4619e+00 6.7330e+00 6.9655e+00 7.1589e+00 7.3128e+00 7.4269e+00 7.5009e+00 7.5345e+00 7.5412e+00 7.5883e+00 7.6757e+00 7.8031e+00 7.9702e+00 8.1767e+00 8.4221e+00 8.7059e+00 9.0273e+00 9.3856e+00 9.7800e+00 1.0210e+01 1.0659e+01 1.0673e+01 1.1170e+01 1.1699e+01 1.2259e+01 1.2848e+01 1.3465e+01 1.4109e+01 1.4778e+01 1.5471e+01 1.6185e+01 1.6921e+01 1.7674e+01 1.8445e+01 1.9231e+01 2.0030e+01 2.0841e+01 2.1661e+01 2.2489e+01 2.3323e+01 2.4160e+01 2.5000e+01
Actuator.JoukowskyDisk.rpm                 = 5.0000e+00 5.0000e+00 5.0000e+00 5.0000e+00 5.0000e+00 5.0000e+00 5.0000e+00 5.0000e+00 5.0000e+00 5.0000e+00 5.0000e+00 5.0861e+00 5.1954e+00 5.2765e+00 5.3290e+00 5.3529e+00 5.3577e+00 5.3912e+00 5.4532e+00 5.5437e+00 5.6625e+00 5.8092e+00 5.9836e+00 6.1851e+00 6.4135e+00 6.6681e+00 6.9483e+00 7.2535e+00 7.4992e+00 7.4992e+00 7.4992e+00 7.4992e+00 7.4992e+00 7.4992e+00 7.4992e+00 7.4992e+00 7.4992e+00 7.4992e+00 7.4992e+00 7.4992e+00 7.4992e+00 7.4992e+00 7.4992e+00 7.4992e+00 7.4992e+00 7.4992e+00 7.4992e+00 7.4992e+00 7.4992e+00 7.4992e+00
Actuator.JoukowskyDisk.rotor_diameter      = 240.0
Actuator.JoukowskyDisk.hub_height          = 150.0
Actuator.JoukowskyDisk.output_frequency    = 100
Actuator.JoukowskyDisk.diameters_to_sample = 1.0                 
Actuator.JoukowskyDisk.num_points_r        = 40                  
Actuator.JoukowskyDisk.num_points_t        = 5                   
Actuator.JoukowskyDisk.num_blades          = 3                   
Actuator.JoukowskyDisk.use_tip_correction  = true                
Actuator.JoukowskyDisk.use_root_correction = true  
Actuator.JoukowskyDisk.epsilon             = 5.0                 
Actuator.JoukowskyDisk.vortex_core_size    = 24.0                

Actuator.UniformCtDisk.yaw = 270.0 # degrees (yaw is relative to north which defaults to {0,1,0})
# Actuator.UniformCtDisk.sample_yaw = 270.0 # set velocity sampling to be in the normal flow direction

Actuator.T00.base_position               = -669.705627 -2027.350647 0.0
# Actuator.T00.yaw                         = 270.0                   
Actuator.T01.base_position               = -1348.528137 -1348.528137 0.0             
# Actuator.T01.yaw                         = 270.0               
Actuator.T02.base_position               = -2027.350647 -669.705627 0.0
# Actuator.T02.yaw                         = 270.0           
Actuator.T03.base_position               = -160.588745 -839.411255 0.0
# Actuator.T03.yaw                         = 270.0               
Actuator.T04.base_position               = -839.411255 -160.588745 0.0
# Actuator.T04.yaw                         = 270.0               
Actuator.T05.base_position               = 1027.350647 -330.294373 0.0
# Actuator.T05.yaw                         = 270.0               
Actuator.T06.base_position               = 348.528137 348.528137 0.0
# Actuator.T06.yaw                         = 270.0               
Actuator.T07.base_position               = -330.294373 1027.350647 0.0
# Actuator.T07.yaw                         = 270.0                
                 
#== END AMR-WIND INPUT ==
