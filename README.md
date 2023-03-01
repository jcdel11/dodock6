# dodock6 - Simple Docking Calculations with Dock6

Molecular docking is a powerful tool that allows us to analyze the orientation of any ligand or protein against some target, which is usually a protein.

There are several programs for docking calculations. I have personally used the program Dock6. This program takes 3 initial files: Our receptor in .mol2 format, our ligand or ligands in .mol2 format, and a receptor surface file in .dms format. mol2 files must have hydrogens and molecular charge.

## How the program works

The program performs certain questions. Answer each question according to the location of your files. I recommend making a folder ( ie " DOCK / " ) where you keep your files mol2 and dms. After you create your spheres (saved in a folder named "SHOWSPH") the next question is if you want to calculate the grid. Before doing this, you have to open all your sphere files (named like cluster_1, cluster_2, etc) and your box files (saved in a folder named "REC_BOX") in a molecular viewer like PyMol. Search the cluster and the box that fits well with your needs. Then run the program again and choose "N" in the question about sphere generation. When the question about grid calculation appears, choose "Y" and continue.
