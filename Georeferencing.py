conda install -c conda-forge gdal

import streamlit as st
import gdal
import osr

st.title("Image Georeferencing")

# Define the input and output file paths
input_file = st.file_uploader("Upload input file")
output_file = st.text_input("Output file name", "output.tif")

# Define the corner coordinates in the order of Top Left, Top Right, Bottom Right, Bottom Left
x1 = st.number_input("Top Left X", value=0)
y1 = st.number_input("Top Left Y", value=0)
x2 = st.number_input("Top Right X", value=0)
y2 = st.number_input("Top Right Y", value=0)
x3 = st.number_input("Bottom Right X", value=0)
y3 = st.number_input("Bottom Right Y", value=0)
x4 = st.number_input("Bottom Left X", value=0)
y4 = st.number_input("Bottom Left Y", value=0)

if input_file and output_file:
    # Open the input image using GDAL
    dataset = gdal.Open(input_file, gdal.GA_Update)

    # Get the image's projection and geotransform
    projection = dataset.GetProjection()
    geotransform = dataset.GetGeoTransform()

    # Create a new spatial reference object based on the input image's projection
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromWkt(projection)

    # Create a new spatial reference object based on the EPSG code of the coordinate system you want to use
    new_spatial_ref = osr.SpatialReference()
    new_spatial_ref.ImportFromEPSG(4326)  # EPSG code for WGS84

    # Create a transformation object to convert the corner coordinates from the input image's projection to the new spatial reference
    transform = osr.CoordinateTransformation(spatial_ref, new_spatial_ref)

    # Transform the corner coordinates to the new spatial reference
    corner_coordinates = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    new_corner_coordinates = []
    for corner in corner_coordinates:
        x, y, z = transform.TransformPoint(corner[0], corner[1])
        new_corner_coordinates.append((x, y))

    # Update the image's geotransform with the new corner coordinates
    geotransform = (new_corner_coordinates[0][0], (new_corner_coordinates[1][0] - new_corner_coordinates[0][0]) / dataset.RasterXSize, 0,
                    new_corner_coordinates[0][1], 0, (new_corner_coordinates[3][1] - new_corner_coordinates[0][1]) / dataset.RasterYSize)

    dataset.SetGeoTransform(geotransform)
    dataset.SetProjection(new_spatial_ref.ExportToWkt())

    driver = gdal.GetDriverByName("GTiff")
    output_dataset = driver.CreateCopy(output_file, dataset)
    output_dataset = None

    dataset = None

    st.success("Image georeferenced!")
