add_executable(unit_tests
  test_utility.cpp
)

target_include_directories(unit_tests PRIVATE
  ${CMAKE_SOURCE_DIR}/Basic_EFM_Template
)

add_test(NAME unit_tests COMMAND unit_tests)

add_executable(api_tests
  test_api.cpp
  ${CMAKE_SOURCE_DIR}/Basic_EFM_Template/Basic_EFM_Template.cpp
)

target_include_directories(api_tests PRIVATE
  ${CMAKE_SOURCE_DIR}/Basic_EFM_Template
)

add_test(NAME api_tests COMMAND api_tests)
