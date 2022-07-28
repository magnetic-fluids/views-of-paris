import argparse
import numpy as np
import re
import sys
from paraview.simple import *
from pathlib import Path

class BadArgumentError(RuntimeError):
	pass

# parse arguments, of which we have two
parser = argparse.ArgumentParser()
parser.add_argument('input_dir', help='directory containing input VTK files', type=Path)
parser.add_argument('-s', '--step', help='plot specific steps', type=int, nargs='+')
args = parser.parse_args()

# check if we were actually passed a directory
if not args.input_dir.is_dir():
	raise BadArgumentError(f'input path should point to a directory')

# disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()
# get active view
main_view = GetActiveViewOrCreate('RenderView')

# read all volume-of-fluid files and organize by step
input_files = sorted(args.input_dir.glob('VOF*.vtk'))

# assuming all the files are present and formatted as VOFstep-process.vtk...
def file_to_idxs(file):
	return map(int, re.findall(r'\d+', file.name))

# the last file in the list should tell us the maximum step & source index
# (starting from zero)
[steps, processes] = file_to_idxs(input_files[-1])
steps += 1
processes += 1
print(f'steps={steps} processes={processes}')
# preallocate list of VTK sources
vof_sources = [[None for _ in range(processes)] for _ in range(steps)]

step_range = range(steps)
if args.step != None:
	for step in args.step:
		if step < 0 or step >= steps:
			raise BadArgumentError(f'step {step} out of range!')

	print(f'plotting steps {args.step} only')
	step_range = args.step

for step in step_range:
	for process in range(processes):
		vof_file = args.input_dir / ('VOF%05d-%05d.vtk' % (step, process))
		source = LegacyVTKReader(FileNames=[str(vof_file)])
		vof_sources[step][process] = source

# array to hold visible stuff by step so we can show/hide them
sources_by_step = [[] for _ in range(steps)]
# (for things that have a scalar bar they need shown)
scalar_bar_needed_by_step = [[] for _ in range(steps)]

# allocate list of droplets (the VTK datasets merged by step) and set up
# their rendering
for step in step_range:
	source_list = vof_sources[step][0:int(.75*processes)]
	droplet_group = GroupDatasets(Input=source_list)
	droplet = MergeBlocks(Input=droplet_group)
	cell_to_point = CellDatatoPointData(Input=droplet)
	#cell_to_point.CellDataArraytoprocess = ['VOF']

	# show the droplet as a countour view
	contour = Contour(Input=cell_to_point)
	contour.ContourBy = ['POINTS', 'VOF']
	contour.Isosurfaces = [.9, .3]
	contour_display = Show(contour, main_view)

	# set up a greenish colormap for fluid volume
	ColorBy(contour_display, ('POINTS', 'VOF'))
	VOF_color = GetColorTransferFunction('VOF')
	VOF_color.ApplyPreset('Linear Green (Gr4L)', True)
	VOF_color.AutomaticRescaleRangeMode = 'Never'
	VOF_color.RescaleTransferFunction(0, 1)
	#contour_display.Representation = 'Surface'

	# hang onto visible stuff from this step
	sources_by_step[step].extend([contour])
	scalar_bar_needed_by_step[step].extend([contour_display])

# read all magnetics files and organize by step
mag_sources = [[None for _ in range(processes)] for _ in range(steps)]

for step in step_range:
	for process in range(processes):
		mag_file = args.input_dir / ('mag%05d-%05d.vtk' % (step, process))
		source = LegacyVTKReader(FileNames=[str(mag_file)])
		mag_sources[step][process] = source

# merge magnetics data by step and render some fun stuff
for step in step_range:
	source_list = mag_sources[step]
	dataset_group = GroupDatasets(Input=source_list)
	potential = MergeBlocks(Input=dataset_group)

	# take the gradient of the magnetic potential and plot it
	field = Gradient(Input=potential)
	field.ScalarArray = ['CELLS', 'PHIMAG']
	field.ResultArrayName = 'Mag. Field'

	# plot field vectors
#	field_vecs = Glyph(Input=field, GlyphType='Arrow')
#	field_vecs.OrientationArray = ['CELLS', 'Mag. Field']
#	field_vecs.ScaleArray = ['CELLS', 'Mag. Field']
#	field_vecs.ScaleFactor = 6e-6
#	field_vecs.MaximumNumberOfSamplePoints = 200
#	field_vecs_display = Show(field_vecs, main_view)
#	ColorBy(field_vecs_display, None)
#	field_vecs_display.AmbientColor = [1, 1, 0]
#	field_vecs_display.DiffuseColor = [1, 1, 0]

	# plot magnetic field lines
	field_lines = StreamTracer(Input=field)
	field_lines.Vectors = ['CELLS', 'Mag. Field']
	field_lines.MaximumStreamlineLength = .08
	field_lines.SeedType.Point1 = [0, 0.025, 0]
	field_lines.SeedType.Point2 = [.04, 0.015, .04]
	field_lines.SeedType.Resolution = 99
	field_lines_display = Show(field_lines, main_view)
	ColorBy(field_lines_display, ('POINTS', 'Mag. Field', 'Magnitude'))
	field_lines_display.RescaleTransferFunctionToDataRange(True)

	# hang onto visible stuff from this step
	# have to save field lines so that we can enable the scalar bar properly
	sources_by_step[step].extend([field_lines])
	scalar_bar_needed_by_step[step].extend([field_lines_display])

# show/hide data in view
def show_step(all_steps, step):
	for source in all_steps[step]:
		Show(source, main_view)

	# show the scale bar for things that need it(because it gets hidden otherwise)
	for needs_bar in scalar_bar_needed_by_step[step]:
		needs_bar.SetScalarBarVisibility(main_view, True)

def hide_step(all_steps, step):
	for source in all_steps[step]:
		Hide(source, main_view)

# useful for normalizing list-vectors
def normalize(l, norm=1):
	return list(np.array(l) / np.linalg.norm(l) * norm)

# set up the camera
main_view.Update()
main_view.ResetCamera(False)
main_layout = GetLayout()
main_layout.SetSize(800, 800)
main_view.CameraPosition = normalize([0.5, 1, .4], .15)
main_view.CameraViewUp = normalize([0, 0, 1])
main_view.CameraViewAngle = 20

# hide everything to start with
for step in step_range:
	hide_step(sources_by_step, step)

# save some screenies
for step in step_range:
	show_step(sources_by_step, step)
	RenderAllViews()
	filename = 'screenshots/magnetic_drop_%05d.png' % (step)
	SaveScreenshot(filename, main_view)
	hide_step(sources_by_step, step)
