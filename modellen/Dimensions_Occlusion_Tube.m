clear all
close all
clc
%% Define dimensions rotor/bearings... all in mm
ID_bearing = 8; 
OD_bearing = 22;
OD_Rotor = 56;
OD_Pegsupport = 10;
%Tube Parameters
OD_Tube = 10;
ID_Tube = 5;
Occlusion = 0.1;
Rest_Tube = ID_Tube - Occlusion*ID_Tube 
%% Dimensions pump housing
Diameter_Housing_Clearance = OD_Rotor +2 %max 1mm clearance between housing and rotor because m4 screws need to sit at fixed distance
Total_Radius_Rotor = OD_Rotor/2 - OD_Pegsupport/2 + OD_bearing/2 %from center of rotor to end of bearing surface
Diameter_Housing_Surface = Total_Radius_Rotor*2 + Rest_Tube*2 %Change This value in the design to accomodate for different occlusions and tubes
Diameter_OuterRing_Top = Diameter_Housing_Surface-1 %1mm clearance for top plate to ensure good fit+To keep tube in place (not creeping up)
Diameter_InnerRing_Top = OD_Rotor +4 %2mm clearance between inner ring of top plate and rotor, good fit/overlap with open bearing surface to ensure tube stays in place; but not too tight to have rubbing

