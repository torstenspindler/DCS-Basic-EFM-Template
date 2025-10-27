# CMake generated Testfile for 
# Source directory: /workspace/tests
# Build directory: /workspace/build/tests
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(unit_tests "/workspace/build/tests/unit_tests")
set_tests_properties(unit_tests PROPERTIES  _BACKTRACE_TRIPLES "/workspace/tests/CMakeLists.txt;9;add_test;/workspace/tests/CMakeLists.txt;0;")
add_test(api_tests "/workspace/build/tests/api_tests")
set_tests_properties(api_tests PROPERTIES  _BACKTRACE_TRIPLES "/workspace/tests/CMakeLists.txt;20;add_test;/workspace/tests/CMakeLists.txt;0;")
