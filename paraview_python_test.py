import numpy as np
import os
import glob

#### import the simple module from the paraview
from paraview.simple import *

#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# uncomment following to set a specific view size
# renderView1.ViewSize = [2751, 1034]


#find all vof vtk files
os.chdir('Kor_chi_03_h1500_128/out/VTK')
vof_files = glob.glob('VOF*')

#determine the number of timesteps and the number of processes (vtk files per timestep)
num_proc = 0
num_tstep = 0
for ii in range(len(vof_files)):
    num_tstep = max([num_tstep, int(vof_files[ii][3:8])])
    num_proc = max([num_proc, int(vof_files[ii][9:14])])

num_tstep = num_tstep + 1
num_proc = num_proc + 1

print(num_tstep)
print(num_proc)

vtk_files = [[0]*num_proc]*num_tstep
groupDatasets = []
mergeBlocks = []
find_blob_threshold = []
connectivity = []
mergeBlocksDisplay = []
cell_corner_interp = []
cell_corner_interp_display = []


#Loop over timesteps, processes to merge vtk files, perform connectivity labeling, and output COM and MOI of each blob
for ii in range(num_tstep):
    for jj in range(num_proc):
        tstep = format(ii, '05')
        proc = format(jj, '05')
        vtk_string = 'VOF'+tstep+'-'+proc+'.vtk'
        vtk_files[ii][jj] = LegacyVTKReader(FileNames=[vtk_string])

    # create a new 'Group Datasets'
    groupDatasets.append(GroupDatasets(Input=vtk_files[ii]))

    # create a new 'Merge Blocks'
    mergeBlocks.append(MergeBlocks(Input=groupDatasets[ii]))

    # show data in view
    mergeBlocksDisplay.append(Show(mergeBlocks[ii], renderView1))

    # trace defaults for the display properties.
    mergeBlocksDisplay[ii].Representation = 'Surface'

    # show color bar/color legend
    mergeBlocksDisplay[ii].SetScalarBarVisibility(renderView1, False)

    # hide data in view
    Hide(mergeBlocks[ii], renderView1)


    #Convert Cell Data to point data to get accurate representation of VOF values at corners
    cell_corner_interp.append(CellDatatoPointData(Input=mergeBlocks[ii]))
    cell_corner_interp[ii].PassCellData = 1
    # show data in view
    cell_corner_interp_display.append(Show(cell_corner_interp[ii], renderView1))

    # trace defaults for the display properties.
    cell_corner_interp_display[ii].Representation = 'Surface'

    # show color bar/color legend
    cell_corner_interp_display[ii].SetScalarBarVisibility(renderView1, False)

    # hide data in view
    Hide(cell_corner_interp_display[ii], renderView1)

    # update the view to ensure updated data information
    renderView1.Update()


    # create a new 'Threshold' get VOF points greater than zero
    find_blob_threshold.append(Threshold(Input=cell_corner_interp[ii]))

    # Properties modified on threshold1
    find_blob_threshold[ii].Scalars = ['CELLS', 'VOF']
    find_blob_threshold[ii].ThresholdRange = [1.0, 1.0]

    # create a new 'Connectivity' perform connectivity labeling algorithm
    connectivity.append(Connectivity(Input=find_blob_threshold[ii]))

    #get number of blobs
    Num_Blobs = int(connectivity[ii].PointData.GetArray("RegionId").GetRange()[1] + 1)

    threshold = []
    cell_centers = []
    volume = []
    coords_center = []
    coords_corner = []

    #split clusters and get volume and cell center coordinates for each cluster
    for kk in range(Num_Blobs):
        # create a new 'Threshold'
        threshold.append(Threshold(Input=connectivity[ii]))
        # Properties modified on threshold1
        threshold[kk].Scalars = ['POINTS', 'RegionId']
        threshold[kk].ThresholdRange = [float(kk), float(kk)]
        volume.append(PythonCalculator(Input=threshold[kk]))
        volume[kk].Expression = 'volume(inputs[0])'
        volume[kk].ArrayAssociation = 'Point Data'
        volume[kk].ArrayName = 'volume'
        cell_centers.append(CellCenters(Input=volume[kk]))
        coords_center.append(Calculator(Input=cell_centers[kk]))
        coords_center[kk].ResultArrayName = 'coords'
        coords_center[kk].Function = 'coords'
        coords_corner.append(Calculator(Input=threshold[kk]))
        coords_corner[kk].ResultArrayName = 'coords'
        coords_corner[kk].Function = 'coords'


        #fetch point center data from paraview backend
        point_data_center = paraview.servermanager.Fetch(coords_center[kk])

        #fetch point corner data from paraview backend
        point_data_corner = paraview.servermanager.Fetch(coords_corner[kk])

        #get number of points in cluster
        numPoints = point_data_center.GetNumberOfPoints()


        #calculate weighted coordinate array using geometric mean and arithmetic mean
        import vtk as vtk
        weighted_coords_array_geometric = np.zeros((numPoints, 3))
        weighted_coords_array_arithmetic = np.zeros((numPoints, 3))
        for oo in range(numPoints):
            idList = vtk.vtkIdList()
            point_data_corner.GetCellPoints(oo,idList)
            cvof_sum = 0
            if point_data_center.GetPointData().GetArray('VOF').GetValue(oo) == 1.0:
                weighted_coords_array_geometric[oo,:] = np.asarray(point_data_center.GetPointData().GetArray('coords').GetTuple(oo))
                weighted_coords_array_arithmetic[oo,:] = np.asarray(point_data_center.GetPointData().GetArray('coords').GetTuple(oo))
            else:
                for pp in range(8):
                    id_temp = idList.GetId(pp)
                    cvof_temp = point_data_corner.GetPointData().GetArray('VOF').GetValue(id_temp)
                    cvof_sum = cvof_sum + cvof_temp
                    weighted_coords_array_arithmetic[oo,:] = weighted_coords_array_arithmetic[oo,:] + cvof_temp*np.asarray(point_data_corner.GetPointData().GetArray('coords').GetTuple(id_temp))
                    weighted_coords_array_geometric[oo,:] = weighted_coords_array_geometric[oo,:] + cvof_temp*np.log(np.asarray(point_data_corner.GetPointData().GetArray('coords').GetTuple(id_temp)))
                weighted_coords_array_geometric[oo,:] = np.exp(weighted_coords_array_geometric[oo,:]/cvof_sum)
                weighted_coords_array_arithmetic[oo,:] = weighted_coords_array_arithmetic[oo,:]/cvof_sum


        #calculate center of mass for each cluster
        vol_sum = 0;
        COM_center = np.zeros(3)
        COM_geometric = np.zeros(3)
        COM_arithmetic = np.zeros(3)


        for ll in range(numPoints):
            cvof = point_data_center.GetPointData().GetArray('VOF').GetValue(ll)
            vol_cell = point_data_center.GetPointData().GetArray('volume').GetValue(ll)
            vol = cvof*vol_cell
            vol_sum = vol_sum + vol
            COM_center = COM_center +  vol*np.asarray(point_data_center.GetPointData().GetArray('coords').GetTuple(ll))
            COM_geometric = COM_geometric +  vol*weighted_coords_array_geometric[ll,:]
            COM_arithmetic = COM_arithmetic +  vol*weighted_coords_array_arithmetic[ll,:]

        COM_center = COM_center/vol_sum
        COM_geometric = COM_geometric/vol_sum
        COM_arithmetic = COM_arithmetic/vol_sum

        #calculate MOI of each cluster using center of mass as point of reference
        I_center = np.zeros(6)
        I_geometric = np.zeros(6)
        I_arithmetic = np.zeros(6)

        for mm in range(numPoints):
            cvof =  point_data_center.GetPointData().GetArray('VOF').GetValue(mm)
            vol_cell = point_data_center.GetPointData().GetArray('volume').GetValue(mm)

            #center
            r = np.asarray(point_data_center.GetPointData().GetArray('coords').GetTuple(mm))-COM_center
            I_center[0] = I_center[0] + cvof*(r[1]**2+r[2]**2)*vol_cell #Ixx
            I_center[1] = I_center[1] + cvof*(r[0]**2+r[2]**2)*vol_cell #Iyy
            I_center[2] = I_center[2] + cvof*(r[0]**2+r[1]**2)*vol_cell #Izz
            I_center[3] = I_center[3] - cvof*r[0]*r[1]*vol_cell #Ixy
            I_center[4] = I_center[4] - cvof*r[0]*r[2]*vol_cell #Ixz
            I_center[5] = I_center[5] - cvof*r[1]*r[2]*vol_cell #Iyz

            #geometric
            r = weighted_coords_array_geometric[mm,:]-COM_geometric
            I_geometric[0] = I_geometric[0] + cvof*(r[1]**2+r[2]**2)*vol_cell #Ixx
            I_geometric[1] = I_geometric[1] + cvof*(r[0]**2+r[2]**2)*vol_cell #Iyy
            I_geometric[2] = I_geometric[2] + cvof*(r[0]**2+r[1]**2)*vol_cell #Izz
            I_geometric[3] = I_geometric[3] - cvof*r[0]*r[1]*vol_cell #Ixy
            I_geometric[4] = I_geometric[4] - cvof*r[0]*r[2]*vol_cell #Ixz
            I_geometric[5] = I_geometric[5] - cvof*r[1]*r[2]*vol_cell #Iyz

            #arithmetic
            r = weighted_coords_array_arithmetic[mm,:]-COM_geometric
            I_arithmetic[0] = I_arithmetic[0] + cvof*(r[1]**2+r[2]**2)*vol_cell #Ixx
            I_arithmetic[1] = I_arithmetic[1] + cvof*(r[0]**2+r[2]**2)*vol_cell #Iyy
            I_arithmetic[2] = I_arithmetic[2] + cvof*(r[0]**2+r[1]**2)*vol_cell #Izz
            I_arithmetic[3] = I_arithmetic[3] - cvof*r[0]*r[1]*vol_cell #Ixy
            I_arithmetic[4] = I_arithmetic[4] - cvof*r[0]*r[2]*vol_cell #Ixz
            I_arithmetic[5] = I_arithmetic[5] - cvof*r[1]*r[2]*vol_cell #Iyz


        if ii == 0 and kk == 0:
            output_array_center = np.concatenate((np.array([ii]), np.array([kk]), COM_center, I_center), axis = None)
            output_array_arithmetic = np.concatenate((np.array([ii]), np.array([kk]), COM_arithmetic, I_arithmetic), axis = None)
            output_array_geometric = np.concatenate((np.array([ii]), np.array([kk]), COM_geometric, I_geometric), axis = None)
        else:
            output_array_center = np.vstack((output_array_center, np.array(np.concatenate((np.array([ii]), np.array([kk]), COM_center, I_center), axis = None))))
            output_array_arithmetic = np.vstack((output_array_arithmetic, np.array(np.concatenate((np.array([ii]), np.array([kk]), COM_arithmetic, I_arithmetic), axis = None))))
            output_array_geometric = np.vstack((output_array_geometric, np.array(np.concatenate((np.array([ii]), np.array([kk]), COM_geometric, I_geometric), axis = None))))

print(output_array_arithmetic)

#print(output_array_center)
#print(output_array_arithmetic)
#print(output_array_geometric)

#np.savetxt('output_center.csv', output_array_center, delimiter = ',', header = 'tstep,blob,COM_x,COM_y,COM_z,Ixx,Iyy,Izz,Ixy,Ixz,Iyz')
np.savetxt('output_stats.csv', output_array_arithmetic, delimiter = ',', header = 'tstep,blob,COM_x,COM_y,COM_z,Ixx,Iyy,Izz,Ixy,Ixz,Iyz')
#np.savetxt('output_geometric.csv', output_array_geometric, delimiter = ',', header = 'tstep,blob,COM_x,COM_y,COM_z,Ixx,Iyy,Izz,Ixy,Ixz,Iyz')
