cmake_minimum_required(VERSION 3.16)
project(BasicEFMTests LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Only build tests; we do not attempt to build the Windows DLL here
enable_testing()
add_subdirectory(tests)
