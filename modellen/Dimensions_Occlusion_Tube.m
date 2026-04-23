clear all
close all
clc
%% Define dimensions rotor/bearings... all in mm
ID_bearing = 8; 
OD_bearing = 22;
OD_Rotor = 56;
OD_Pegsupport = 10;
OD_Tube = 10;
ID_Tube = 5;
Occlusion = 0.1;
Rest_Tube = ID_Tube - Occlusion*ID_Tube 
%% Dimensions pump housing
Diameter_Housing_Clearance = OD_Rotor +2
Total_Radius_Rotor = OD_Rotor/2 - OD_Pegsupport/2 + OD_bearing/2
Diameter_Housing_Surface = Total_Radius_Rotor*2 + Rest_Tube*2
