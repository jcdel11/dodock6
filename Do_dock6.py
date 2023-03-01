#! /usr/bin/env python

##########################################################

#Do_Dock6 it's a program that make all the step after the
#generation of de DMS file in a simple a guided manner. 

#Usage: ./Do_dock6.py
#Answer the questions and ENJOY!

##########################################################

import re
import os
import readline, glob

def complete(text, state):
    return (glob.glob(text+'*')+[None])[state]

def sphgen(file_name):
	### Generar un archivo SPH con las esferas a       ###
	### partir de un archivo DMS, calculado en Chimera ###
	print "<<< Generating %s.sph file >>>" % file_name
	in_sph = open("INSPH", "w")
	in_sph.write("%s.dms\n" % file_name)
	in_sph.write("R\n")
	in_sph.write("X\n")
	in_sph.write("0.0\n")
	in_sph.write("4.0\n")
	in_sph.write("1.4\n")
	in_sph.write("%s.sph" % file_name)
	in_sph.close()
	comando = "sphgen"
	os.system(comando)

def do_showsph(file_name):
	### Mostrar las esferas generadas en un archivo PDB ###
	print "<<< Generating %s cluster PDB files >>>" % file_name
	sph_file = open("%s.sph" % file_name, "r")
	text = sph_file.readlines()
	os.mkdir("SHOWSPH")
	counter = 0
	for line in text:
		if "cluster" in line:
			terms = line.split(" ")
			if "0" in terms[5]:
				pass
			else:
				os.chdir("SHOWSPH")
				counter = counter + 1
				show = open("sph_cluster_%s.in" % counter, "w")
				show.write("../%s.sph\n" % file_name)
				show.write("%s\n" % counter)
				show.write("N\n")
				show.write("cluster%s.pdb" % counter)
				show.close()
				comando = "showsphere < sph_cluster_%s.in" % counter
				os.system(comando)
				os.system("rm -rf sph_cluster_%s.in" % counter)
				os.chdir("../")

def split_sph(file_name):
	print "<<< Spliting SPH file >>>"
	sph_file = open("%s.sph" % file_name, "r")
	text = sph_file.read()
	sph_file.seek(0)
	lines = sph_file.readlines()
	sph_file.close()
	paragraphs = re.split("cluster    ...  number of spheres in cluster   ...\n", text)
	os.mkdir("SPH_SPLITED")
	os.mkdir("REC_BOX")
	counter = 0

	for l in lines:
		if "cluster" in l:
			terms = l.split(" ")
			if "0" in terms[5]:
				pass
			else:
				counter = counter + 1
				os.chdir("SPH_SPLITED")
				sel_sph = open("sel_sph_%s.sph" % counter, "w")
				sel_sph.write(l)
				sel_sph.write(paragraphs[counter])
				sel_sph.close()
				os.chdir("../")

				os.chdir("REC_BOX")
				in_box = open("box_%s.in" % counter, "w")
				in_box.write("Y\n")
				in_box.write("10\n")
				in_box.write("../SPH_SPLITED/sel_sph_%s.sph\n" % counter)
				in_box.write("%s\n" % counter)
				in_box.write("rec_box_%s.pdb" % counter)
				in_box.close()
				comando = "showbox < box_%s.in" % counter
				os.system(comando)
				os.chdir("../")

	os.chdir("REC_BOX")
	os.system("rm box*")
	os.chdir("../")

def grid(receptor_path, box_path):

	rec_name = receptor_path.split("/")[-1][:-5]
	box_name = box_path.split("/")[-1][:-4].split("_")[-1]
	in_name = "grid_%s_%s.in" % (rec_name, box_name)
	out_name = "grid_%s_%s.out" % (rec_name, box_name)

	in_grid = open("%s" % in_name, "w")
	grid_text = """compute_grids                  yes                  
grid_spacing                   0.3                     
output_molecule                no              
contact_score                  yes                 
contact_cutoff_distance        4.5

energy_score                   yes               
energy_cutoff_distance         9999       

atom_model                     all                  
attractive_exponent            6               
repulsive_exponent             12               
distance_dielectric            yes              
dielectric_factor              4                    

bump_filter                    yes                  
bump_overlap                   0.75             

receptor_file                  %s          
box_file                       %s       
vdw_definition_file            /mnt/hgfs/Documents/dock6/parameters/vdw_AMBER_parm99.defn   
score_grid_prefix              grid
""" % (receptor_path, box_path)
	
	in_grid.write(grid_text)
	in_grid.close()

	comando = "grid -i %s -o %s" % (in_name, out_name)
	os.system(comando)

def do_dock6_rigid(file_name, ligand_path, sph_path, grid_path):

	ligand_name = ligand_path.split("/")[-1][:-5]
	in_name = "dock_%s_%s.in" % (file_name, ligand_name)
	out_name = "dock_%s_%s.out" % (file_name, ligand_name)
	in_dock = open("%s" % in_name, "w")

	dock_text = """ligand_atom_file                                             %s
limit_max_ligands                                            no
skip_molecule                                                no
read_mol_solvation                                           no
calculate_rmsd                                               no
use_database_filter                                          no
orient_ligand                                                yes
automated_matching                                           yes
receptor_site_file                                           %s
max_orientations                                             1000
critical_points                                              no
chemical_matching                                            no
use_ligand_spheres                                           no
use_internal_energy                                          yes
internal_energy_rep_exp                                      12
flexible_ligand                                              no
bump_filter                                                  no
score_molecules                                              yes
contact_score_primary                                        no
contact_score_secondary                                      no
grid_score_primary                                           yes
grid_score_secondary                                         no
grid_score_rep_rad_scale                                     1
grid_score_vdw_scale                                         1
grid_score_es_scale                                          1
grid_score_grid_prefix                                       %s
multigrid_score_secondary                                    no
dock3.5_score_secondary                                      no
continuous_score_secondary                                   no
descriptor_score_secondary                                   no
gbsa_zou_score_secondary                                     no
gbsa_hawkins_score_secondary                                 no
SASA_descriptor_score_secondary                              no
amber_score_secondary                                        no
minimize_ligand                                              yes
simplex_max_iterations                                       1000
simplex_tors_premin_iterations                               0
simplex_max_cycles                                           1
simplex_score_converge                                       0.1
simplex_cycle_converge                                       1.0
simplex_trans_step                                           1.0
simplex_rot_step                                             0.1
simplex_tors_step                                            10.0
simplex_random_seed                                          0
simplex_restraint_min                                        no
atom_model                                                   all
vdw_defn_file                                                /mnt/hgfs/Documents/dock6/parameters/vdw_AMBER_parm99.defn
flex_defn_file                                               /mnt/hgfs/Documents/dock6/parameters/flex.defn
flex_drive_file                                              /mnt/hgfs/Documents/dock6/parameters/flex_drive.tbl
ligand_outfile_prefix                                        rigid
write_orientations                                           yes
num_scored_conformers                                        1
rank_ligands                                                 no
""" % (ligand_path, sph_path, grid_path)
	
	in_dock.write(dock_text)
	in_dock.close()

	comando = "dock6 -i %s -o %s" % (in_name, out_name)
	os.system(comando)

def do_dock6_flexible(file_name, ligand_path, sph_path, grid_path):

	ligand_name = ligand_path.split("/")[-1][:-5]
	in_name = "dock_%s_%s.in" % (file_name, ligand_name)
	out_name = "dock_%s_%s.out" % (file_name, ligand_name)
	in_dock = open("%s" % in_name, "w")

	dock_text = """ligand_atom_file                                             %s
limit_max_ligands                                            no
skip_molecule                                                no
read_mol_solvation                                           no
calculate_rmsd                                               no
use_database_filter                                          no
orient_ligand                                                yes
automated_matching                                           yes
receptor_site_file                                           %s
max_orientations                                             1000
critical_points                                              no
chemical_matching                                            no
use_ligand_spheres                                           no
use_internal_energy                                          yes
internal_energy_rep_exp                                      12
flexible_ligand                                              yes
user_specified_anchor                                        no
limit_max_anchors                                            no
min_anchor_size                                              40
pruning_use_clustering                                       yes
pruning_max_orients                                          100
pruning_clustering_cutoff                                    100
pruning_conformer_score_cutoff                               25.0
use_clash_overlap                                            no
write_growth_tree                                            no
bump_filter                                                  no
score_molecules                                              yes
contact_score_primary                                        no
contact_score_secondary                                      no
grid_score_primary                                           yes
grid_score_secondary                                         no
grid_score_rep_rad_scale                                     1
grid_score_vdw_scale                                         1
grid_score_es_scale                                          1
grid_score_grid_prefix                                       %s
multigrid_score_secondary                                    no
dock3.5_score_secondary                                      no
continuous_score_secondary                                   no
descriptor_score_secondary                                   no
gbsa_zou_score_secondary                                     no
gbsa_hawkins_score_secondary                                 no
SASA_descriptor_score_secondary                              no
amber_score_secondary                                        no
minimize_ligand                                              yes
minimize_anchor                                              yes
minimize_flexible_growth                                     yes
use_advanced_simplex_parameters                              no
simplex_max_cycles                                           1
simplex_score_converge                                       0.1
simplex_cycle_converge                                       1.0
simplex_trans_step                                           1.0
simplex_rot_step                                             0.1
simplex_tors_step                                            10.0
simplex_anchor_max_iterations                                500
simplex_grow_max_iterations                                  500
simplex_grow_tors_premin_iterations                          0
simplex_random_seed                                          0
simplex_restraint_min                                        no
atom_model                                                   all
vdw_defn_file                                                /mnt/hgfs/Documents/dock6/parameters/vdw_AMBER_parm99.defn
flex_defn_file                                               /mnt/hgfs/Documents/dock6/parameters/flex.defn
flex_drive_file                                              /mnt/hgfs/Documents/dock6/parameters/flex_drive.tbl
ligand_outfile_prefix                                        flexible
write_orientations                                           no
num_scored_conformers                                        1
rank_ligands                                                 no
""" % (ligand_path, sph_path, grid_path)
	
	in_dock.write(dock_text)
	in_dock.close()

	comando = "dock6 -i %s -o %s" % (in_name, out_name)
	os.system(comando)

if __name__ == '__main__':

	file_name = raw_input("Name of your file without extension:")

	sph_ask = raw_input("Do you want create spheres? (Y/N):")
	if sph_ask == "Y":
		create_sph = sphgen(file_name)
		sph2pdb = do_showsph(file_name)
		split_sph = split_sph(file_name)
	else:
		pass

	readline.set_completer_delims(' \t\n;') # Las dos primeras lineas deben ir antes de llamar a la funcion complete, para completar en raw_input
	readline.parse_and_bind("tab: complete")
	readline.set_completer(complete)

	grid_ask = raw_input("Do wou want to perform a Grid calculation? (Y/N):")
	if grid_ask == "Y":
		print "<<< Grid Calculation >>>"
		receptor_path = raw_input("What is the full path for your receptor file in mol2 format?:")
		box_path = raw_input("What box would you use? (full path):")
		print "..."
		do_grid = grid(receptor_path, box_path)
	else:
		pass

	dock_ask = raw_input("Do you want to perform a Docking calculation (Y/N):")
	if dock_ask == "Y":
		ligand_path = raw_input("What is the full path for your ligand(s) file in mol2 format?:")
		sph_path = raw_input("Where is your sph file? (full path):")
		grid_path = raw_input("Where are your grid files? (i.e /path/to/grid/prefix_of_your_files):")
		dock_q = raw_input("Do you want to perform a rigid or flexible calculation (R/F):")
		if dock_q == "R":
			print "<<< Rigid docking calculation has started ... >>>"
			dock = do_dock6_rigid(file_name, ligand_path, sph_path, grid_path)
		else:
			print "<<< Flexible docking calculation has started ... >>>"
			dock = do_dock6_flexible(file_name, ligand_path, sph_path, grid_path)
	else:
		print "OK"
		pass
