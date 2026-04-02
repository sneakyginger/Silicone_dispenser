clear all
close all
clc
%%
Tube_diameter = 0.003; %m
Surface_tube = pi*(Tube_diameter/2)^2 %m²
motor_arm_radius = 0.03;%m
step_size = 1.8*(2*pi/360) %rad
Tmin = 0.2; %Nm
Tmax = 0.5; %Nm
Tube_Length = 2; %m
viscosity = 15000 * 10^-3; %Pa.s
density = 1030; %kg/m³
%% Flows
minimum_displaced_V = motor_arm_radius*Surface_tube*10^6 %ml/step
minimum_dislpaced_m = minimum_displaced_V*1.03
motor_speed_max = 1000;%RPM

%% Torques

%Friction force if dispensing 100g/min, assuming linear scale between Tmax
%and Tmin and assuming density ~= 1.g/ml
RPS = ((1000/2700)*100)/60
Q = 0.1/(60*1000) %m³/s
V_avg = Q/Surface_tube %m/s
Re = density*V_avg*Tube_diameter/viscosity;
Pressure_Drop = (128*viscosity*Tube_Length*Q/(pi*Tube_diameter^4))/10^6; %MPa
Required_Force = Pressure_Drop * Surface_tube
Required_Torque = Required_Force*motor_arm_radius

