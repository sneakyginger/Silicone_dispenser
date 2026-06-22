clear all
close all
clc
%% Define fixed dimensions rotor/bearings... all in mm
ID_bearing = 8; 
OD_bearing = 22;
OD_Rotor = 56;
OD_Pegsupport = 10;
%%%TUBE PARAMETERS - TO BE CHANGED%%%
OD_Tube = 10; %outer diameter of the tube
ID_Tube = 5; %inner diameter of the tube
Occlusion = 10/100; %occlusion factor as a percentage
Rest_Tube = (OD_Tube - ID_Tube)*(1- Occlusion) %Remaining needed clearance for the tube
%% Dimensions pump housing (only to be changed in cad when changing rotor dimensions)
Diameter_Housing_Clearance = OD_Rotor +2; %max 1mm clearance between housing and rotor because m4 screws need to sit at fixed distance
Total_Radius_Rotor = OD_Rotor/2 - OD_Pegsupport/2 + OD_bearing/2; %from center of rotor to end of bearing surface
Diameter_InnerRing_Top = OD_Rotor +4; %2mm clearance between inner ring of top plate and rotor, good fit/overlap with open bearing surface to ensure tube stays in place; but not too tight to have rubbing

%%%%RESULTING DIMENSIONS TO CHANGE IN CAD FOR DIFFERENT TUBE PARAMETERS%%%%
Diameter_Housing_Surface = Total_Radius_Rotor*2 + Rest_Tube*2 %Change This value in the CAD design (pump housing bottom) to accomodate for different occlusions and tubes
Pinch_Groove = OD_Tube - 3 %Change this width in the CAD design (pump housing bottom) to accomodate for different tubes
Diameter_OuterRing_Top = Diameter_Housing_Surface-1 %Change this diameter in CAD design (pump housing top) for different tubes

