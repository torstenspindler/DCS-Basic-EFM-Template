set(TEST_SOURCES
  test_utility.cpp
)

add_executable(unit_tests ${TEST_SOURCES})

target_include_directories(unit_tests PRIVATE
  ${CMAKE_SOURCE_DIR}/Basic_EFM_Template
)

# No platform-specific Windows headers for tests; stdafx.h guards them with _WIN32

add_test(NAME unit_tests COMMAND unit_tests)
