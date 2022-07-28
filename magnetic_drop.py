import sys
import re
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
input_files = sorted(input_path.glob('VOF00000*.vtk'))

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
vtk_sources = [[None] * (processes)] * (steps)

for file in input_files:
	source = LegacyVTKReader(registrationName=file.name, FileNames=[str(file)])
	[step, process] = file_to_idxs(file)
	vtk_sources[step][process] = source

# allocate list of droplets (the VTK datasets merged by timestep) and set up
# their rendering
droplets = [None] * steps
for source_list in vtk_sources:
	droplet_group = GroupDatasets(Input=source_list)
	droplet = MergeBlocks(Input=droplet_group)
	cell_to_point = CellDatatoPointData(Input=droplet)
	#cell_to_point.CellDataArraytoprocess = ['VOF']

	# show the droplet as a countour view
	contour = Contour(Input=cell_to_point)
	contour.ContourBy = ['POINTS', 'VOF']
	contour.Isosurfaces = [.5]
	contour_display = Show(contour, main_view)
	ColorBy(contour_display, ('POINTS', 'VOF'))

# read all magnetics files and organize by timestep
input_files = sorted(input_path.glob('mag00000*.vtk'))

# assuming all the files are present and formatted as VOFstep-process.vtk...
def file_to_idxs(file):
	return map(int, re.findall(r'\d+', file.name))

[steps, processes] = file_to_idxs(input_files[-1])
print(f'{steps} steps, {processes} processes')
# preallocate list of sources
mag_sources = [[None] * (processes + 1)] * (steps + 1)

for file in input_files:
	source = LegacyVTKReader(registrationName=file.name, FileNames=[str(file)])
	display = GetDisplayProperties(source)
	[step, process] = file_to_idxs(file)
	mag_sources[step][process] = (source, display)
	Hide(source, main_view)

	# set up magnetics coloring
	display.SetRepresentationType('Wireframe')
	ColorBy(display, ('CELLS', 'PHIMAG'))
	display.RescaleTransferFunctionToDataRange(True, False)
	display.SetScalarBarVisibility(main_view, True)
	pHIMAGLUT = GetColorTransferFunction('PHIMAG')

	# get the gradient of the magnetic potential
	gradient = Gradient(registrationName=file.name + '_gradient', Input=source)
	gradient.ScalarArray = ['CELLS', 'PHIMAG']
	gradient_display = Show(gradient, main_view, 'StructuredGridRepresentation')
	Hide(gradient, main_view)

	# show a collection of field vectors
	field_vecs = Glyph(registrationName=file.name + '_field_vecs', Input=gradient, GlyphType='Arrow')
	field_vecs.GlyphTransform = 'Transform2'
	field_vecs.OrientationArray = ['CELLS', 'Gradient']
	field_vecs.ScaleArray = ['CELLS', 'Gradient']
	field_vecs.ScaleFactor = 5.7471208929013815e-06
	field_vecs.MaximumNumberOfSamplePoints = 200

	field_vecs_display = Show(field_vecs, main_view, 'GeometryRepresentation')
	field_vecs_display.SetScalarBarVisibility(main_view, True)

	field_lines = StreamTracer(registrationName=file.name + '_field_lines', Input=gradient, SeedType='Line')
	field_lines.Vectors = ['CELLS', 'Gradient']
	field_lines.MaximumStreamlineLength = 0.02

	# init the 'Line' selected for 'SeedType'
	#field_lines.SeedType.Point1 = [0.02, 0.02, 0.02]
	#field_lines.SeedType.Point2 = [0.04, 0.04, 0.04]
	field_lines.SeedType.Resolution = 200

	# show data in view
	field_lines_display = Show(field_lines, main_view, 'GeometryRepresentation')
	ColorBy(field_lines_display, ('POINTS', 'Gradient', 'Magnitude'))
	field_lines_display.RescaleTransferFunctionToDataRange(True, False)
	field_lines_display.SetScalarBarVisibility(main_view, True)

# show data in view
def show_timestep(source_list, timestep):
	for (source, display) in source_list[timestep]:
		Show(source, main_view)

#show_timestep(sources, 0)

# set up plot and save a screenie
main_view.Update()
main_view.ResetCamera(False)
main_layout = GetLayout()
main_layout.SetSize(1600, 1600)

# set up camera placement
main_view.CameraPosition = [.1, -.07, .05]
main_view.CameraViewUp = [0, 0, 1]
main_view.CameraViewAngle = 20

RenderAllViews()
SaveScreenshot("magnetic_drop.png", main_view)
