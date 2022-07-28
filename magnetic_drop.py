import sys
import re
import numpy as np
from pathlib import Path
from paraview.simple import *

# disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()
# get active view
main_view = GetActiveViewOrCreate('RenderView')

# we should have gotten an "out" directory as an argument
#if len(sys.argv) != 2:
#	sys.stderr.write(sys.argv[0] + ": pass path to out/ directory as argument")
#	exit()

# path to input files
input_path = Path.cwd() / 'magparis_vw/out/VTK' #Path(sys.argv[1]) / 'VTK'

# read all volume-of-fluid files and organize by timestep
input_files = sorted(input_path.glob('VOF*.vtk'))

# assuming all the files are present and formatted as VOFstep-process.vtk...
def file_to_idxs(file):
	return map(int, re.findall(r'\d+', file.name))

# the last file in the list should tell us the maximum timestep & source index
# (starting from zero)
[steps, processes] = file_to_idxs(input_files[-1])
steps += 1
processes += 1
print(f'steps={steps} processes={processes}')
# preallocate list of VTK sources
vof_sources = [[None for _ in range(processes)] for _ in range(steps)]

for file in input_files:
	source = LegacyVTKReader(registrationName=file.name, FileNames=[str(file)])
	[step, process] = file_to_idxs(file)
	vof_sources[step][process] = source

# array to hold visible stuff by timestep so we can show/hide them
sources_by_step = [[] for _ in range(steps)]

# allocate list of droplets (the VTK datasets merged by timestep) and set up
# their rendering
for timestep in range(steps):
	source_list = vof_sources[timestep]
	droplet_group = GroupDatasets(Input=source_list)
	droplet = MergeBlocks(Input=droplet_group)
	cell_to_point = CellDatatoPointData(Input=droplet)
	#cell_to_point.CellDataArraytoprocess = ['VOF']

	# show the droplet as a countour view
	contour = Contour(Input=cell_to_point)
	contour.ContourBy = ['POINTS', 'VOF']
	contour.Isosurfaces = [.5]
	contour_display = Show(contour, main_view)

	ColorBy(contour_display, None)
	contour_display.AmbientColor = [.44, .26, .25]
	contour_display.DiffuseColor = [.44, .26, .25]

	# hang onto visible stuff from this timestep
	sources_by_step[timestep].extend([contour])

# read all magnetics files and organize by timestep
input_files = sorted(input_path.glob('mag*.vtk'))
mag_sources = [[None for _ in range(processes)] for _ in range(steps)]

for file in input_files:
	source = LegacyVTKReader(registrationName=file.name, FileNames=[str(file)])
	[step, process] = file_to_idxs(file)
	mag_sources[step][process] = source

# merge magnetics data by timestep and render some fun stuff
magnetics_by_step = [[] for _ in range(steps)]
for timestep in range(steps):
	source_list = mag_sources[timestep]
	dataset_group = GroupDatasets(Input=source_list)
	potential = MergeBlocks(Input=dataset_group)

	# take the gradient of the magnetic potential and plot field vectors
	field = Gradient(Input=potential)
	field.ScalarArray = ['CELLS', 'PHIMAG']

	field_vecs = Glyph(Input=field, GlyphType='Arrow')
	field_vecs.OrientationArray = ['CELLS', 'Gradient']
	field_vecs.ScaleArray = ['CELLS', 'Gradient']
	field_vecs.ScaleFactor = 6e-6
	field_vecs.MaximumNumberOfSamplePoints = 200
	field_vecs_display = Show(field_vecs, main_view)
	ColorBy(field_vecs_display, None)
	field_vecs_display.AmbientColor = [1, 1, 0]
	field_vecs_display.DiffuseColor = [1, 1, 0]

	# plot magnetic field lines
	field_lines = StreamTracer(Input=field)
	field_lines.SeedType.Resolution = 200
	field_lines_display = Show(field_lines, main_view)
	ColorBy(field_lines_display, ('POINTS', 'Gradient', 'Magnitude'))
	field_lines_display.RescaleTransferFunctionToDataRange(True)
	field_lines_display.SetScalarBarVisibility(main_view, True)

	# hang onto visible stuff from this timestep
	sources_by_step[timestep].extend([field_vecs, field_lines])

# show/hide data in view
def show_timestep(all_steps, timestep):
	for source in all_steps[timestep]:
		Show(source, main_view)

def hide_timestep(all_steps, timestep):
	for source in all_steps[timestep]:
		Hide(source, main_view)

# useful for normalizing list-vectors
def normalize(l):
	return list(np.array(l) / np.linalg.norm(l))

# set up the camera
main_view.Update()
main_view.ResetCamera(False)
main_layout = GetLayout()
#main_layout.SetSize(800, 800)
main_view.CameraPosition = [.1, -.05, .09]
main_view.CameraViewUp = normalize([0, 0, 1])
main_view.CameraViewAngle = 20

# hide everything to start with
for timestep in range(steps):
	hide_timestep(sources_by_step, timestep)

# save some screenies
for timestep in range(steps):
	show_timestep(sources_by_step, timestep)
	RenderAllViews()
	filename = 'screenshots/magnetic_drop_%05d.png' % (timestep)
	SaveScreenshot(filename, main_view)
	hide_timestep(sources_by_step, timestep)
