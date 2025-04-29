import netCDF4 as nc

def read_nc_file(file_path):
    try:
        # Open the NetCDF file
        nc_file = nc.Dataset(file_path, 'r')

        # Print the file dimensions
        print("Dimensions:")
        for dim_name, dim in nc_file.dimensions.items():
            print(f"\t{dim_name}: {len(dim)}")

        # Print the file variables
        print("\nVariables:")
        for var_name, var in nc_file.variables.items():
            print(f"\t{var_name}: {var.shape} {var.units if 'units' in var.ncattrs() else ''}")

        # Close the NetCDF file
        nc_file.close()
    except Exception as e:
        print(f"Error: {e}")

# Provide the path to your .nc file
file_path = "C:\Users\tommu\Documents\GRA_Code\flaskApp\fldData\field00024.nc"

# Call the function to read the .nc file
read_nc_file(file_path)
