Ymir

Available backends:
- GACODE: https://github.com/gafusion/gacode
- Gkeyll: https://github.com/ammarhakim/gkeyll
- Hermes-3: https://github.com/boutproject/hermes-3

Dependencies:
- GACODE:
  - fftw: https://packages.spack.io/package.html?name=fftw
  - netcdf-fortran: https://packages.spack.io/package.html?name=netcdf-fortran
  - openblas: https://packages.spack.io/package.html?name=openblas
- Gkeyll:
  - MPI
  - lua-luajit: https://packages.spack.io/package.html?name=lua-luajit
  - openblas: https://packages.spack.io/package.html?name=openblas
  - superlu: https://packages.spack.io/package.html?name=superlu
- Hermes-3:
  - adios2: https://pypi.org/project/adios2/
  - boutdata: https://pypi.org/project/boutdata/
  - boututils: https://pypi.org/project/boututils/
  - fftw: https://packages.spack.io/package.html?name=fftw
  - netcdf-cxx4: https://packages.spack.io/package.html?name=netcdf-cxx4
  - py-cython: https://packages.spack.io/package.html?name=py-cython
  - xhermes: https://pypi.org/project/xhermes/
