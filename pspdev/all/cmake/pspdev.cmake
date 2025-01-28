if(DEFINED ENV{PSPDEV})
    SET(PSPDEV $ENV{PSPDEV})
else()
    message(FATAL_ERROR "The environment variable PSPDEV needs to be defined.")
endif()

SET(CMAKE_SYSTEM_NAME Generic)
SET(CMAKE_SYSTEM_VERSION 1)

SET(PLATFORM_PSP TRUE)
SET(PSP TRUE)

include("${PSPDEV}/psp/share/CreatePBP.cmake")
include("${PSPDEV}/psp/share/AddPrxModule.cmake")

message(STATUS "Conan toolchain: disabling CMAKE_POSITION_INDIPENDENT_CODE")
set(CMAKE_POSITION_INDEPENDENT_CODE OFF)
