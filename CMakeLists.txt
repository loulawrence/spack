# WIX INSTALLER GENERATOR FOR SPACK ON WINDOWS
# 
cmake_minimum_required (VERSION 3.13)
project(spack_installer)
set(PYTHON_VERSION "3.9.0" CACHE STRING "Version of Python to build.")
set(SPACK_VERSION "0.16.0" CACHE STRING "Version of Spack to build.")
set(PY_DOWNLOAD_LINK "https://www.paraview.org/files/dependencies")
set(PY_FILENAME "Python-${PYTHON_VERSION}-win64.tar.xz")
configure_file("installer/spack_cmd.bat.in" "spack_cmd.bat")
file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/installer/spack-logo.ico"
        DESTINATION "${CMAKE_CURRENT_BINARY_DIR}")

# PYTHON DOWLOAD AND EXTRACTION-----------------------------------
file(DOWNLOAD "${PY_DOWNLOAD_LINK}/${PY_FILENAME}" 
	"${CMAKE_CURRENT_BINARY_DIR}/${PY_FILENAME}"
	STATUS download_status 
	EXPECTED_HASH "SHA256=f6aeebc6d1ff77418678ed5612b64ce61be6bc9ef3ab9c291ac557abb1783420"
)
list(GET download_status 0 res)
if(res)
	list(GET download_status 1 err)
	message(FATAL_ERROR "Failed to download ${PY_FILENAME}")
endif()
message(STATUS "Successfully downloaded ${PY_FILENAME}")

execute_process(COMMAND ${CMAKE_COMMAND} -E tar xfz "${CMAKE_CURRENT_BINARY_DIR}/${PY_FILENAME}"
				WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
				RESULT_VARIABLE res)
if(NOT res EQUAL 0)
	message(FATAL_ERROR "Extraction of ${PY_FILENAME} failed.")
endif()
message(STATUS "Extracted ${PY_FILENAME}.")


# INSTALLATION COMMANDS---------------------------------------------------
# Copy spack source to install directory
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/.github/" DESTINATION ".github")
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/bin/" DESTINATION "bin")
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/etc/" DESTINATION "etc")
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/installer/" DESTINATION "installer")
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/lib/" DESTINATION "lib")
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/share/" DESTINATION "share")
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/var/" DESTINATION "var")
install(FILES .codecov.yml 
			  .coveragerc 
			  .dockerignore 
			  .flake8 
			  .flake8_packages
			  .gitattributes
			  .gitignore
			  .mailmap
			  .readthedocs.yml 
			  CHANGELOG.md 
			  CMakeLists.txt 
			  COPYRIGHT 
			  LICENSE-APACHE 
			  LICENSE-MIT
			  NOTICE 
			  pytest.ini 
			  README.md
			  installer/spack-logo.ico
			  DESTINATION .)
install(DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/Python-${PYTHON_VERSION}-win64/" DESTINATION "Python-${PYTHON_VERSION}")

# CPACK Installer Instructions
set(CPACK_PACKAGE_NAME "Spack")
set(CPACK_PACKAGE_VENDOR "Lawrence Livermore National Laboratories")
set(CPACK_PACKAGE_VERSION_MAJOR "0")
set(CPACK_PACKAGE_VERSION_MINOR "16")
set(CPACK_PACKAGE_VERSION_PATCH "0")
set(CPACK_PACKAGE_DESCRIPTION "A flexible package manager designed to support multiple versions, configurations, platforms, and compilers.")
set(CPACK_PACKAGE_HOMEPAGE_URL "https://spack.io")
set(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}.${CPACK_PACKAGE_VERSION_PATCH}")
set(CPACK_PACKAGE_ICON "${CMAKE_CURRENT_SOURCE_DIR}/installer/spack-logo.ico")
set(CPACK_RESOURCE_FILE_README "${CMAKE_CURRENT_SOURCE_DIR}/README.md")
set(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/installer/LICENSE-APACHE.rtf")
set(CPACK_RESOURCE_FILE_WELCOME "${CMAKE_CURRENT_SOURCE_DIR}/NOTICE")
set(CPACK_GENERATOR "WIX")
set(CPACK_WIX_PRODUCT_ICON "${CMAKE_CURRENT_SOURCE_DIR}/installer/spack-logo.ico")
set(CPACK_WIX_UI_BANNER "${CMAKE_CURRENT_SOURCE_DIR}/installer/banner493x58.bmp")
set(CPACK_WIX_PATCH_FILE "${CMAKE_CURRENT_SOURCE_DIR}/installer/patch.xml")
set(CPACK_WIX_UPGRADE_GUID "B9DBDE20-C6C8-4644-AC39-6F5F4D5039CB")
set(CPACK_WIX_EXTRA_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/installer/spack.wxs")
include(CPack)