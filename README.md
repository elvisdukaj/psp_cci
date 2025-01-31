# Description

This repository aims to make easier to develop for the PSP console using the Conan Package Manager.

# Packages

This repo contains the following packages:

- pspdev: this is the main toolchain and the OS include and libraries
- libpspvram: library for memory allocation.
- pspgl: OpenGL implementation on top of the psp sdk
- sdl: a slightly modified version of SDL2 so it can find the above packages

The goal is to put this packages upstream to the conan-center-index so it's not
necessary to build manually the following packages.

# Note

This is still a draft and a lot of work is still needed. The next steps will be:

- [ ] add pspdev packages for Linux and Windows and Macos arm
- [ ] testing

# Configuration

## Install Conan 

For installing conan you can use the system package manger:

- debuan: `sudo apt install conan`
- Macos: `brew install conan`
- Windows: `winget install --Id JFrog.Conan`

Or via Python:
- pip install conan
- pipenv install conan

## Configure Conan  

We need to create a new os type in the Conan configuration. In the conan home directory
(usually located in `~/.conan2`) create a new `settings_user.yml` like below:

```yaml
os:
  PSP:
```

This add a new os in the conan settings.

# Build

**Note** w the build works only on Macos x86_64.

```
# install the pspdev toolchain and sdk
conan create pspdev/all --version v20250101 --build missing

# install the OpenGL port
conan create pspgl/all --version v20250101 --profile ./psp --build missing

# install the psp virtual memory library
conan create libpspvram/all --version v20250101 --profile ./psp --build missing

# install the port of SDK to use the above libraries
conan create sdl/all --version 2.30.9 --profile ./psp --build missing

```
 



# Examples

The following is a simple SDL2 application using a cmake project.


## conanfile.txt

```
[requires]
sdl/2.30.9

[generators]
CMakeDeps
CMakeToolchain

[layout]
cmake_layout
```

## CMakeLists.txt

```CMake
cmake_minimum_required(VERSION 3.16)

project(square)

add_executable(${PROJECT_NAME} main.c)

find_package(SDL2 REQUIRED CONFIG)


target_link_libraries(${PROJECT_NAME} PRIVATE SDL2::SDL2main)

if(PSP)
    # This function will generate the EBOOT.PBP that can be deployed on the PSP or used with an emulator
    create_pbp_file(
        TARGET ${PROJECT_NAME}
        ICON_PATH NULL
        BACKGROUND_PATH NULL
        PREVIEW_PATH NULL
        TITLE ${PROJECT_NAME}
    )
endif()
```

## main.c


```C
#include <SDL2/SDL.h>

int main(int argc, char *argv[])
{
    SDL_Init(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER);

    SDL_Window * window = SDL_CreateWindow(
        "window",
        SDL_WINDOWPOS_UNDEFINED,
        SDL_WINDOWPOS_UNDEFINED,
        480,
        272,
        0
    );
    SDL_Renderer * renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);

    SDL_Rect square = {216, 96, 34, 64};

    int running = 1;
    SDL_Event event;
    while (running) {
        if (SDL_PollEvent(&event)) {
            switch (event.type) {
                case SDL_QUIT:
                    running = 0;
                    break;
                case SDL_CONTROLLERDEVICEADDED:
                    SDL_GameControllerOpen(event.cdevice.which);
                    break;
                case SDL_CONTROLLERBUTTONDOWN:
                    if(event.cbutton.button == SDL_CONTROLLER_BUTTON_START)
                        running = 0;
                    break;
            }
        }

        // Clear the screen
        SDL_RenderClear(renderer);

        // Draw a red square
        SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255);
        SDL_RenderFillRect(renderer, &square);

        // Draw everything on a white background
        SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
        SDL_RenderPresent(renderer);
    }

    return 0;
}
```

## Building 

For building you need the same profile [psp](psp) profile.

```
conan build . --profile psp
```

## Running

Download the [PPSSPP](https://www.ppsspp.org/) emulator and load the `EBOOT.PBP` file generated after the build (in `build/psp-mips-gcc-14.1/Release`) 
