# # test_psipy_units.py

# import astropy.units as u
# import numpy as np
# from psipy.tracing import FortranTracer

# class DummyModel:
#     def get_bvec(self, r, lat, lon):
#         # Convert r, lat, lon to floats
#         r_val = r.to(u.m).value
#         lat_val = lat.to(u.rad).value
#         lon_val = lon.to(u.rad).value
#         # Return a dummy constant field
#         return np.array([1, 2, 3]) * u.nT

#     @property
#     def r_min(self):
#         return 1 * u.m

#     @property
#     def r_max(self):
#         return 1e6 * u.m

# tracer = FortranTracer(max_steps=1000)
# model = DummyModel()

# # Single test line
# r0 = 50 * u.m
# lat0 = 0 * u.rad
# lon0 = 0 * u.rad

# try:
#     lines = tracer.trace(model, r=[r0], lat=[lat0], lon=[lon0])
#     print("Success! Traced lines:", lines)
# except Exception as e:
#     print("Error in test_psipy_units:", e)






# test_psipy_units_minimal.py
import numpy as np
import astropy.units as u
from psipy.tracing import FortranTracer

# Very basic model
class DummyModel:
    def get_bvec(self, r, lat, lon):
        # Return a dummy field
        return np.array([1,2,3]) * u.nT
    
    @property
    def r_min(self):
        return 1 * u.m
    
    @property
    def r_max(self):
        return 1e6 * u.m

model = DummyModel()
tracer = FortranTracer(max_steps=1000)

# Arrays of length 2
r_list = [10*u.m, 20*u.m]
lat_list = [0*u.rad, 0.1*u.rad]
lon_list = [0*u.rad, 0.2*u.rad]

try:
    flines = tracer.trace(model, r=r_list, lat=lat_list, lon=lon_list)
    print("Success! flines=", flines)
except Exception as e:
    print("Error in minimal test:", e)
