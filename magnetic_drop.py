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
input_files = sorted(input_path.glob('VOF*.vtk'))

# assuming all the files are present and formatted as VOFstep-process.vtk...
def file_to_idxs(file):
	return map(int, re.findall(r'\d+', file.name))

[steps, processes] = file_to_idxs(input_files[-1])
print(f'{steps} steps, {processes} processes')
# preallocate list of sources
sources = [[None] * (processes + 1)] * (steps + 1)

for file in input_files:
	source = LegacyVTKReader(registrationName=file.name, FileNames=[str(file)])
	display = GetDisplayProperties(source)
	[step, process] = file_to_idxs(file)
	sources[step][process] = (source, display)

	cell_to_point = CellDatatoPointData(registrationName=file.name + '_cell_to_point', Input=source)
	cell_to_point.CellDataArraytoprocess = ['VOF']

	# create a display object, as it's necessary for the colormap
	cell_to_point_display = Show(cell_to_point, main_view, 'StructuredGridRepresentation')
	ColorBy(cell_to_point_display, ('POINTS', 'VOF'))
	cell_to_point_display.RescaleTransferFunctionToDataRange(True, False)
	cell_to_point_display.SetScalarBarVisibility(main_view, True)
	vOFLUT = GetColorTransferFunction('VOF')
	ColorBy(cell_to_point_display, None)
	HideScalarBarIfNotNeeded(vOFLUT, main_view)

	# create a contour display
	contour = Contour(registrationName=file.name + '_contour', Input=cell_to_point)
	contour.ContourBy = ['POINTS', 'VOF']
	contour.Isosurfaces = [0.5]
	contour.PointMergeMethod = 'Uniform Binning'

	contour_display = Show(contour, main_view, 'GeometryRepresentation')
	contour_display.Representation = 'Surface'
	contour_display.ColorArrayName = ['POINTS', 'VOF']
	contour_display.LookupTable = vOFLUT
	contour_display.SetScalarBarVisibility(main_view, True)

# show data in view
def show_timestep(source_list, timestep):
	for (source, display) in source_list[timestep]:
		Show(source, main_view)

show_timestep(sources, 0)

# set up plot and save a screenie
main_view.Update()
main_view.ResetCamera(False)
main_layout = GetLayout()
main_layout.SetSize(1602, 695)

# set up camera placement
main_view.CameraPosition = [.1, -.07, .05]
main_view.CameraViewUp = [0, 0, 1]
main_view.CameraViewAngle = 20

#RenderAllViews()
SaveScreenshot("magnetic_drop.png", main_view)
exit()

# create a new 'Legacy VTK Reader'
mag0002000000vtk = LegacyVTKReader(registrationName='mag00020-00000.vtk', FileNames=['/home/charles/CU/fluids_research/views-of-paris/magparis_vw/out/VTK/mag00020-00000.vtk'])

# create a new 'Legacy VTK Reader'
mag0002000001vtk = LegacyVTKReader(registrationName='mag00020-00001.vtk', FileNames=['/home/charles/CU/fluids_research/views-of-paris/magparis_vw/out/VTK/mag00020-00001.vtk'])

# create a new 'Legacy VTK Reader'
mag0002000002vtk = LegacyVTKReader(registrationName='mag00020-00002.vtk', FileNames=['/home/charles/CU/fluids_research/views-of-paris/magparis_vw/out/VTK/mag00020-00002.vtk'])

# create a new 'Legacy VTK Reader'
mag0002000003vtk = LegacyVTKReader(registrationName='mag00020-00003.vtk', FileNames=['/home/charles/CU/fluids_research/views-of-paris/magparis_vw/out/VTK/mag00020-00003.vtk'])

# create a new 'Legacy VTK Reader'
mag0002000004vtk = LegacyVTKReader(registrationName='mag00020-00004.vtk', FileNames=['/home/charles/CU/fluids_research/views-of-paris/magparis_vw/out/VTK/mag00020-00004.vtk'])

# create a new 'Legacy VTK Reader'
mag0002000005vtk = LegacyVTKReader(registrationName='mag00020-00005.vtk', FileNames=['/home/charles/CU/fluids_research/views-of-paris/magparis_vw/out/VTK/mag00020-00005.vtk'])

# create a new 'Legacy VTK Reader'
mag0002000006vtk = LegacyVTKReader(registrationName='mag00020-00006.vtk', FileNames=['/home/charles/CU/fluids_research/views-of-paris/magparis_vw/out/VTK/mag00020-00006.vtk'])

# create a new 'Legacy VTK Reader'
mag0002000007vtk = LegacyVTKReader(registrationName='mag00020-00007.vtk', FileNames=['/home/charles/CU/fluids_research/views-of-paris/magparis_vw/out/VTK/mag00020-00007.vtk'])

# show data in view
mag0002000007vtkDisplay = Show(mag0002000007vtk, renderView1, 'StructuredGridRepresentation')

# trace defaults for the display properties.
mag0002000007vtkDisplay.Representation = 'Outline'
mag0002000007vtkDisplay.ColorArrayName = ['CELLS', '']
mag0002000007vtkDisplay.SelectTCoordArray = 'None'
mag0002000007vtkDisplay.SelectNormalArray = 'None'
mag0002000007vtkDisplay.SelectTangentArray = 'None'
mag0002000007vtkDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
mag0002000007vtkDisplay.SelectOrientationVectors = 'None'
mag0002000007vtkDisplay.ScaleFactor = 0.002
mag0002000007vtkDisplay.SelectScaleArray = 'PHIMAG'
mag0002000007vtkDisplay.GlyphType = 'Arrow'
mag0002000007vtkDisplay.GlyphTableIndexArray = 'PHIMAG'
mag0002000007vtkDisplay.GaussianRadius = 0.0001
mag0002000007vtkDisplay.SetScaleArray = [None, '']
mag0002000007vtkDisplay.ScaleTransferFunction = 'PiecewiseFunction'
mag0002000007vtkDisplay.OpacityArray = [None, '']
mag0002000007vtkDisplay.OpacityTransferFunction = 'PiecewiseFunction'
mag0002000007vtkDisplay.DataAxesGrid = 'GridAxesRepresentation'
mag0002000007vtkDisplay.PolarAxes = 'PolarAxesRepresentation'
mag0002000007vtkDisplay.ScalarOpacityUnitDistance = 0.0010825317547305483

# show data in view
mag0002000000vtkDisplay = Show(mag0002000000vtk, renderView1, 'StructuredGridRepresentation')

# trace defaults for the display properties.
mag0002000000vtkDisplay.Representation = 'Outline'
mag0002000000vtkDisplay.ColorArrayName = ['CELLS', '']
mag0002000000vtkDisplay.SelectTCoordArray = 'None'
mag0002000000vtkDisplay.SelectNormalArray = 'None'
mag0002000000vtkDisplay.SelectTangentArray = 'None'
mag0002000000vtkDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
mag0002000000vtkDisplay.SelectOrientationVectors = 'None'
mag0002000000vtkDisplay.ScaleFactor = 0.002
mag0002000000vtkDisplay.SelectScaleArray = 'PHIMAG'
mag0002000000vtkDisplay.GlyphType = 'Arrow'
mag0002000000vtkDisplay.GlyphTableIndexArray = 'PHIMAG'
mag0002000000vtkDisplay.GaussianRadius = 0.0001
mag0002000000vtkDisplay.SetScaleArray = [None, '']
mag0002000000vtkDisplay.ScaleTransferFunction = 'PiecewiseFunction'
mag0002000000vtkDisplay.OpacityArray = [None, '']
mag0002000000vtkDisplay.OpacityTransferFunction = 'PiecewiseFunction'
mag0002000000vtkDisplay.DataAxesGrid = 'GridAxesRepresentation'
mag0002000000vtkDisplay.PolarAxes = 'PolarAxesRepresentation'
mag0002000000vtkDisplay.ScalarOpacityUnitDistance = 0.0010825317547305483

# show data in view
mag0002000001vtkDisplay = Show(mag0002000001vtk, renderView1, 'StructuredGridRepresentation')

# trace defaults for the display properties.
mag0002000001vtkDisplay.Representation = 'Outline'
mag0002000001vtkDisplay.ColorArrayName = ['CELLS', '']
mag0002000001vtkDisplay.SelectTCoordArray = 'None'
mag0002000001vtkDisplay.SelectNormalArray = 'None'
mag0002000001vtkDisplay.SelectTangentArray = 'None'
mag0002000001vtkDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
mag0002000001vtkDisplay.SelectOrientationVectors = 'None'
mag0002000001vtkDisplay.ScaleFactor = 0.002
mag0002000001vtkDisplay.SelectScaleArray = 'PHIMAG'
mag0002000001vtkDisplay.GlyphType = 'Arrow'
mag0002000001vtkDisplay.GlyphTableIndexArray = 'PHIMAG'
mag0002000001vtkDisplay.GaussianRadius = 0.0001
mag0002000001vtkDisplay.SetScaleArray = [None, '']
mag0002000001vtkDisplay.ScaleTransferFunction = 'PiecewiseFunction'
mag0002000001vtkDisplay.OpacityArray = [None, '']
mag0002000001vtkDisplay.OpacityTransferFunction = 'PiecewiseFunction'
mag0002000001vtkDisplay.DataAxesGrid = 'GridAxesRepresentation'
mag0002000001vtkDisplay.PolarAxes = 'PolarAxesRepresentation'
mag0002000001vtkDisplay.ScalarOpacityUnitDistance = 0.0010825317547305483

# show data in view
mag0002000002vtkDisplay = Show(mag0002000002vtk, renderView1, 'StructuredGridRepresentation')

# trace defaults for the display properties.
mag0002000002vtkDisplay.Representation = 'Outline'
mag0002000002vtkDisplay.ColorArrayName = ['CELLS', '']
mag0002000002vtkDisplay.SelectTCoordArray = 'None'
mag0002000002vtkDisplay.SelectNormalArray = 'None'
mag0002000002vtkDisplay.SelectTangentArray = 'None'
mag0002000002vtkDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
mag0002000002vtkDisplay.SelectOrientationVectors = 'None'
mag0002000002vtkDisplay.ScaleFactor = 0.002
mag0002000002vtkDisplay.SelectScaleArray = 'PHIMAG'
mag0002000002vtkDisplay.GlyphType = 'Arrow'
mag0002000002vtkDisplay.GlyphTableIndexArray = 'PHIMAG'
mag0002000002vtkDisplay.GaussianRadius = 0.0001
mag0002000002vtkDisplay.SetScaleArray = [None, '']
mag0002000002vtkDisplay.ScaleTransferFunction = 'PiecewiseFunction'
mag0002000002vtkDisplay.OpacityArray = [None, '']
mag0002000002vtkDisplay.OpacityTransferFunction = 'PiecewiseFunction'
mag0002000002vtkDisplay.DataAxesGrid = 'GridAxesRepresentation'
mag0002000002vtkDisplay.PolarAxes = 'PolarAxesRepresentation'
mag0002000002vtkDisplay.ScalarOpacityUnitDistance = 0.0010825317547305483

# show data in view
mag0002000006vtkDisplay = Show(mag0002000006vtk, renderView1, 'StructuredGridRepresentation')

# trace defaults for the display properties.
mag0002000006vtkDisplay.Representation = 'Outline'
mag0002000006vtkDisplay.ColorArrayName = ['CELLS', '']
mag0002000006vtkDisplay.SelectTCoordArray = 'None'
mag0002000006vtkDisplay.SelectNormalArray = 'None'
mag0002000006vtkDisplay.SelectTangentArray = 'None'
mag0002000006vtkDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
mag0002000006vtkDisplay.SelectOrientationVectors = 'None'
mag0002000006vtkDisplay.ScaleFactor = 0.002
mag0002000006vtkDisplay.SelectScaleArray = 'PHIMAG'
mag0002000006vtkDisplay.GlyphType = 'Arrow'
mag0002000006vtkDisplay.GlyphTableIndexArray = 'PHIMAG'
mag0002000006vtkDisplay.GaussianRadius = 0.0001
mag0002000006vtkDisplay.SetScaleArray = [None, '']
mag0002000006vtkDisplay.ScaleTransferFunction = 'PiecewiseFunction'
mag0002000006vtkDisplay.OpacityArray = [None, '']
mag0002000006vtkDisplay.OpacityTransferFunction = 'PiecewiseFunction'
mag0002000006vtkDisplay.DataAxesGrid = 'GridAxesRepresentation'
mag0002000006vtkDisplay.PolarAxes = 'PolarAxesRepresentation'
mag0002000006vtkDisplay.ScalarOpacityUnitDistance = 0.0010825317547305483

# show data in view
mag0002000003vtkDisplay = Show(mag0002000003vtk, renderView1, 'StructuredGridRepresentation')

# trace defaults for the display properties.
mag0002000003vtkDisplay.Representation = 'Outline'
mag0002000003vtkDisplay.ColorArrayName = ['CELLS', '']
mag0002000003vtkDisplay.SelectTCoordArray = 'None'
mag0002000003vtkDisplay.SelectNormalArray = 'None'
mag0002000003vtkDisplay.SelectTangentArray = 'None'
mag0002000003vtkDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
mag0002000003vtkDisplay.SelectOrientationVectors = 'None'
mag0002000003vtkDisplay.ScaleFactor = 0.002
mag0002000003vtkDisplay.SelectScaleArray = 'PHIMAG'
mag0002000003vtkDisplay.GlyphType = 'Arrow'
mag0002000003vtkDisplay.GlyphTableIndexArray = 'PHIMAG'
mag0002000003vtkDisplay.GaussianRadius = 0.0001
mag0002000003vtkDisplay.SetScaleArray = [None, '']
mag0002000003vtkDisplay.ScaleTransferFunction = 'PiecewiseFunction'
mag0002000003vtkDisplay.OpacityArray = [None, '']
mag0002000003vtkDisplay.OpacityTransferFunction = 'PiecewiseFunction'
mag0002000003vtkDisplay.DataAxesGrid = 'GridAxesRepresentation'
mag0002000003vtkDisplay.PolarAxes = 'PolarAxesRepresentation'
mag0002000003vtkDisplay.ScalarOpacityUnitDistance = 0.0010825317547305483

# show data in view
mag0002000005vtkDisplay = Show(mag0002000005vtk, renderView1, 'StructuredGridRepresentation')

# trace defaults for the display properties.
mag0002000005vtkDisplay.Representation = 'Outline'
mag0002000005vtkDisplay.ColorArrayName = ['CELLS', '']
mag0002000005vtkDisplay.SelectTCoordArray = 'None'
mag0002000005vtkDisplay.SelectNormalArray = 'None'
mag0002000005vtkDisplay.SelectTangentArray = 'None'
mag0002000005vtkDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
mag0002000005vtkDisplay.SelectOrientationVectors = 'None'
mag0002000005vtkDisplay.ScaleFactor = 0.002
mag0002000005vtkDisplay.SelectScaleArray = 'PHIMAG'
mag0002000005vtkDisplay.GlyphType = 'Arrow'
mag0002000005vtkDisplay.GlyphTableIndexArray = 'PHIMAG'
mag0002000005vtkDisplay.GaussianRadius = 0.0001
mag0002000005vtkDisplay.SetScaleArray = [None, '']
mag0002000005vtkDisplay.ScaleTransferFunction = 'PiecewiseFunction'
mag0002000005vtkDisplay.OpacityArray = [None, '']
mag0002000005vtkDisplay.OpacityTransferFunction = 'PiecewiseFunction'
mag0002000005vtkDisplay.DataAxesGrid = 'GridAxesRepresentation'
mag0002000005vtkDisplay.PolarAxes = 'PolarAxesRepresentation'
mag0002000005vtkDisplay.ScalarOpacityUnitDistance = 0.0010825317547305483

# show data in view
mag0002000004vtkDisplay = Show(mag0002000004vtk, renderView1, 'StructuredGridRepresentation')

# trace defaults for the display properties.
mag0002000004vtkDisplay.Representation = 'Outline'
mag0002000004vtkDisplay.ColorArrayName = ['CELLS', '']
mag0002000004vtkDisplay.SelectTCoordArray = 'None'
mag0002000004vtkDisplay.SelectNormalArray = 'None'
mag0002000004vtkDisplay.SelectTangentArray = 'None'
mag0002000004vtkDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
mag0002000004vtkDisplay.SelectOrientationVectors = 'None'
mag0002000004vtkDisplay.ScaleFactor = 0.002
mag0002000004vtkDisplay.SelectScaleArray = 'PHIMAG'
mag0002000004vtkDisplay.GlyphType = 'Arrow'
mag0002000004vtkDisplay.GlyphTableIndexArray = 'PHIMAG'
mag0002000004vtkDisplay.GaussianRadius = 0.0001
mag0002000004vtkDisplay.SetScaleArray = [None, '']
mag0002000004vtkDisplay.ScaleTransferFunction = 'PiecewiseFunction'
mag0002000004vtkDisplay.OpacityArray = [None, '']
mag0002000004vtkDisplay.OpacityTransferFunction = 'PiecewiseFunction'
mag0002000004vtkDisplay.DataAxesGrid = 'GridAxesRepresentation'
mag0002000004vtkDisplay.PolarAxes = 'PolarAxesRepresentation'
mag0002000004vtkDisplay.ScalarOpacityUnitDistance = 0.0010825317547305483

# update the view to ensure updated data information
renderView1.Update()

# change representation type
mag0002000007vtkDisplay.SetRepresentationType('Wireframe')

# set scalar coloring
ColorBy(mag0002000007vtkDisplay, ('CELLS', 'PHIMAG'))

# rescale color and/or opacity maps used to include current data range
mag0002000007vtkDisplay.RescaleTransferFunctionToDataRange(True, False)

# show color bar/color legend
mag0002000007vtkDisplay.SetScalarBarVisibility(renderView1, True)

# get color transfer function/color map for 'PHIMAG'
pHIMAGLUT = GetColorTransferFunction('PHIMAG')

# get opacity transfer function/opacity map for 'PHIMAG'
pHIMAGPWF = GetOpacityTransferFunction('PHIMAG')

# create a new 'Cell Data to Point Data'
cellDatatoPointData2 = CellDatatoPointData(registrationName='CellDatatoPointData2', Input=mag0002000007vtk)
cellDatatoPointData2.CellDataArraytoprocess = ['PHIMAG']

# show data in view
cellDatatoPointData2Display = Show(cellDatatoPointData2, renderView1, 'StructuredGridRepresentation')

# trace defaults for the display properties.
cellDatatoPointData2Display.Representation = 'Outline'
cellDatatoPointData2Display.ColorArrayName = ['POINTS', '']
cellDatatoPointData2Display.SelectTCoordArray = 'None'
cellDatatoPointData2Display.SelectNormalArray = 'None'
cellDatatoPointData2Display.SelectTangentArray = 'None'
cellDatatoPointData2Display.OSPRayScaleArray = 'PHIMAG'
cellDatatoPointData2Display.OSPRayScaleFunction = 'PiecewiseFunction'
cellDatatoPointData2Display.SelectOrientationVectors = 'None'
cellDatatoPointData2Display.ScaleFactor = 0.002
cellDatatoPointData2Display.SelectScaleArray = 'PHIMAG'
cellDatatoPointData2Display.GlyphType = 'Arrow'
cellDatatoPointData2Display.GlyphTableIndexArray = 'PHIMAG'
cellDatatoPointData2Display.GaussianRadius = 0.0001
cellDatatoPointData2Display.SetScaleArray = ['POINTS', 'PHIMAG']
cellDatatoPointData2Display.ScaleTransferFunction = 'PiecewiseFunction'
cellDatatoPointData2Display.OpacityArray = ['POINTS', 'PHIMAG']
cellDatatoPointData2Display.OpacityTransferFunction = 'PiecewiseFunction'
cellDatatoPointData2Display.DataAxesGrid = 'GridAxesRepresentation'
cellDatatoPointData2Display.PolarAxes = 'PolarAxesRepresentation'
cellDatatoPointData2Display.ScalarOpacityUnitDistance = 0.0010825317547305483

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
cellDatatoPointData2Display.ScaleTransferFunction.Points = [11.057499885559082, 0.0, 0.5, 0.0, 21.009000778198242, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
cellDatatoPointData2Display.OpacityTransferFunction.Points = [11.057499885559082, 0.0, 0.5, 0.0, 21.009000778198242, 1.0, 0.5, 0.0]

# hide data in view
Hide(mag0002000007vtk, renderView1)

# update the view to ensure updated data information
renderView1.Update()

# create a new 'Contour'
contour2 = Contour(registrationName='Contour2', Input=cellDatatoPointData2)
contour2.ContourBy = ['POINTS', 'PHIMAG']
contour2.Isosurfaces = [16.033250331878662]
contour2.PointMergeMethod = 'Uniform Binning'

# set active source
SetActiveSource(cellDatatoPointData2)

# destroy contour2
Delete(contour2)
del contour2

# set active source
SetActiveSource(mag0002000007vtk)

# hide data in view
Hide(cellDatatoPointData2, renderView1)

# show data in view
mag0002000007vtkDisplay = Show(mag0002000007vtk, renderView1, 'StructuredGridRepresentation')

# show color bar/color legend
mag0002000007vtkDisplay.SetScalarBarVisibility(renderView1, True)

# destroy cellDatatoPointData2
Delete(cellDatatoPointData2)
del cellDatatoPointData2

# create a new 'Glyph'
glyph1 = Glyph(registrationName='Glyph1', Input=mag0002000007vtk,
    GlyphType='Arrow')
glyph1.OrientationArray = ['POINTS', 'No orientation array']
glyph1.ScaleArray = ['CELLS', 'PHIMAG']
glyph1.ScaleFactor = 0.002
glyph1.GlyphTransform = 'Transform2'

# set active source
SetActiveSource(mag0002000007vtk)

# destroy glyph1
Delete(glyph1)
del glyph1

# create a new 'Gradient'
gradient1 = Gradient(registrationName='Gradient1', Input=mag0002000007vtk)
gradient1.ScalarArray = ['CELLS', 'PHIMAG']

# show data in view
gradient1Display = Show(gradient1, renderView1, 'StructuredGridRepresentation')

# trace defaults for the display properties.
gradient1Display.Representation = 'Outline'
gradient1Display.ColorArrayName = ['CELLS', 'PHIMAG']
gradient1Display.LookupTable = pHIMAGLUT
gradient1Display.SelectTCoordArray = 'None'
gradient1Display.SelectNormalArray = 'None'
gradient1Display.SelectTangentArray = 'None'
gradient1Display.OSPRayScaleFunction = 'PiecewiseFunction'
gradient1Display.SelectOrientationVectors = 'None'
gradient1Display.ScaleFactor = 0.002
gradient1Display.SelectScaleArray = 'PHIMAG'
gradient1Display.GlyphType = 'Arrow'
gradient1Display.GlyphTableIndexArray = 'PHIMAG'
gradient1Display.GaussianRadius = 0.0001
gradient1Display.SetScaleArray = [None, '']
gradient1Display.ScaleTransferFunction = 'PiecewiseFunction'
gradient1Display.OpacityArray = [None, '']
gradient1Display.OpacityTransferFunction = 'PiecewiseFunction'
gradient1Display.DataAxesGrid = 'GridAxesRepresentation'
gradient1Display.PolarAxes = 'PolarAxesRepresentation'
gradient1Display.ScalarOpacityFunction = pHIMAGPWF
gradient1Display.ScalarOpacityUnitDistance = 0.0010825317547305483

# hide data in view
Hide(mag0002000007vtk, renderView1)

# show color bar/color legend
gradient1Display.SetScalarBarVisibility(renderView1, True)

# update the view to ensure updated data information
renderView1.Update()

# create a new 'Glyph'
glyph1 = Glyph(registrationName='Glyph1', Input=gradient1,
    GlyphType='Arrow')
glyph1.OrientationArray = ['POINTS', 'No orientation array']
glyph1.ScaleArray = ['CELLS', 'PHIMAG']
glyph1.ScaleFactor = 0.002
glyph1.GlyphTransform = 'Transform2'

# Properties modified on glyph1
glyph1.OrientationArray = ['CELLS', 'Gradient']
glyph1.ScaleArray = ['CELLS', 'Gradient']
glyph1.ScaleFactor = 5.7471208929013815e-06

# show data in view
glyph1Display = Show(glyph1, renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
glyph1Display.Representation = 'Surface'
glyph1Display.ColorArrayName = ['POINTS', 'PHIMAG']
glyph1Display.LookupTable = pHIMAGLUT
glyph1Display.SelectTCoordArray = 'None'
glyph1Display.SelectNormalArray = 'None'
glyph1Display.SelectTangentArray = 'None'
glyph1Display.OSPRayScaleArray = 'PHIMAG'
glyph1Display.OSPRayScaleFunction = 'PiecewiseFunction'
glyph1Display.SelectOrientationVectors = 'Gradient'
glyph1Display.ScaleFactor = 0.0022091805934906007
glyph1Display.SelectScaleArray = 'PHIMAG'
glyph1Display.GlyphType = 'Arrow'
glyph1Display.GlyphTableIndexArray = 'PHIMAG'
glyph1Display.GaussianRadius = 0.00011045902967453003
glyph1Display.SetScaleArray = ['POINTS', 'PHIMAG']
glyph1Display.ScaleTransferFunction = 'PiecewiseFunction'
glyph1Display.OpacityArray = ['POINTS', 'PHIMAG']
glyph1Display.OpacityTransferFunction = 'PiecewiseFunction'
glyph1Display.DataAxesGrid = 'GridAxesRepresentation'
glyph1Display.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
glyph1Display.ScaleTransferFunction.Points = [11.057000160217285, 0.0, 0.5, 0.0, 21.009000778198242, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
glyph1Display.OpacityTransferFunction.Points = [11.057000160217285, 0.0, 0.5, 0.0, 21.009000778198242, 1.0, 0.5, 0.0]

# show color bar/color legend
glyph1Display.SetScalarBarVisibility(renderView1, True)

# update the view to ensure updated data information
renderView1.Update()

# Properties modified on glyph1
glyph1.MaximumNumberOfSamplePoints = 1000

# update the view to ensure updated data information
renderView1.Update()

# set active source
SetActiveSource(mag0002000007vtk)

# set active source
SetActiveSource(gradient1)

# create a new 'Stream Tracer'
streamTracer1 = StreamTracer(registrationName='StreamTracer1', Input=gradient1,
    SeedType='Line')
streamTracer1.Vectors = ['CELLS', 'Gradient']
streamTracer1.MaximumStreamlineLength = 0.02

# init the 'Line' selected for 'SeedType'
streamTracer1.SeedType.Point1 = [0.02, 0.02, 0.02]
streamTracer1.SeedType.Point2 = [0.04, 0.04, 0.04]

# show data in view
streamTracer1Display = Show(streamTracer1, renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
streamTracer1Display.Representation = 'Surface'
streamTracer1Display.ColorArrayName = [None, '']
streamTracer1Display.SelectTCoordArray = 'None'
streamTracer1Display.SelectNormalArray = 'None'
streamTracer1Display.SelectTangentArray = 'None'
streamTracer1Display.OSPRayScaleArray = 'AngularVelocity'
streamTracer1Display.OSPRayScaleFunction = 'PiecewiseFunction'
streamTracer1Display.SelectOrientationVectors = 'Normals'
streamTracer1Display.ScaleFactor = 0.0019999999552965165
streamTracer1Display.SelectScaleArray = 'AngularVelocity'
streamTracer1Display.GlyphType = 'Arrow'
streamTracer1Display.GlyphTableIndexArray = 'AngularVelocity'
streamTracer1Display.GaussianRadius = 9.999999776482583e-05
streamTracer1Display.SetScaleArray = ['POINTS', 'AngularVelocity']
streamTracer1Display.ScaleTransferFunction = 'PiecewiseFunction'
streamTracer1Display.OpacityArray = ['POINTS', 'AngularVelocity']
streamTracer1Display.OpacityTransferFunction = 'PiecewiseFunction'
streamTracer1Display.DataAxesGrid = 'GridAxesRepresentation'
streamTracer1Display.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
streamTracer1Display.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.1757813367477812e-38, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
streamTracer1Display.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.1757813367477812e-38, 1.0, 0.5, 0.0]

# update the view to ensure updated data information
renderView1.Update()

# hide data in view
Hide(glyph1, renderView1)

# update the view to ensure updated data information
renderView1.Update()

# set scalar coloring
ColorBy(streamTracer1Display, ('POINTS', 'Gradient', 'Magnitude'))

# rescale color and/or opacity maps used to include current data range
streamTracer1Display.RescaleTransferFunctionToDataRange(True, False)

# show color bar/color legend
streamTracer1Display.SetScalarBarVisibility(renderView1, True)

# get color transfer function/color map for 'Gradient'
gradientLUT = GetColorTransferFunction('Gradient')

# get opacity transfer function/opacity map for 'Gradient'
gradientPWF = GetOpacityTransferFunction('Gradient')

