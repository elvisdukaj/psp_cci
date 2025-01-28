import os
from pathlib import PurePosixPath
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, export_conandata_patches, apply_conandata_patches, copy
from conan.tools.layout import basic_layout


required_conan_version = ">=2"


class AllegrexConan(ConanFile):
    name = "pspdev"
    description = "Toolchain to target the Sony PSP console"
    url = ""
    homepage = "https://github.com/pspdev/pspdev"
    license = "MIT"
    package_type = "application"
    topics = ("gcc", "sony", "psp", "homebrew", "console")
    settings = "os", "arch"

    @property
    def _settings_os_supported(self):
        return self.conan_data["sources"][self.version].get(str(self.settings.os)) is not None

    @property
    def _settings_arch_supported(self):
        return self.conan_data["sources"][self.version].get(str(self.settings.os), {}).get(str(self.settings.arch)) is not None

    def validate(self):
        if not self._settings_os_supported:
            raise ConanInvalidConfiguration(f"os={self.settings.os} is not supported by {self.name} (no binaries are available)")
        if not self._settings_arch_supported:
            raise ConanInvalidConfiguration(f"os,arch={self.settings.os},{self.settings.arch} is not supported by {self.name} (no binaries are available)")

    def export_sources(self):
        export_conandata_patches(self)
        copy(self,
             pattern="*.cmake",
             src=os.path.join(self.recipe_folder, "cmake"),
             dst=os.path.join(self.export_sources_folder, "psp", "share"),
             keep_path=False
             )

    def layout(self):
        basic_layout(self)

    def source(self):
        pass

    def build(self):
        apply_conandata_patches(self)
        get(self,
            # url and sha256
            **self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)],
            destination=self.source_folder,
            strip_root=True
            )

    def package(self):
        copy(self,
             pattern="*",
             src=self.source_folder,
             dst=self.package_folder,
             excludes=["build"])

    def package_info(self):
        target = "psp"
        pspdev_folder = os.path.join(self.package_folder)


        self.cpp_info.components["sdk"].includedirs

        # self.cpp_info.components["sdk"]..includedirs = ["include", "psp/include", "psp/sdk/include"]
        # self.cpp_info.components["sdk"]..libdirs = ["lib", "psp/lib", "psp/sdk/lib"]
        self.cpp_info.bindirs = ["bin", "psp/bin"]

        # self.cpp_info.defines = ["PSP", "__PSP__", "_PSP_FW_VERSION=600"]
        # self.cpp_info.sharedlinkflags= ["-Wl,-zmax-page-size=128"]
        # self.cpp_info.exelinkflags = ["-Wl,-zmax-page-size=128"]

        cflags = f'-I{PurePosixPath(pspdev_folder, "include")} -I{PurePosixPath(pspdev_folder, target, "include")} -I{PurePosixPath(pspdev_folder, target, "sdk", "include")} -DPSP -D__PSP__ -D_PSP_FW_VERSION=600'
        ldflags = f'-L{PurePosixPath(pspdev_folder, "lib")} -L{PurePosixPath(pspdev_folder, target, "lib")} -L{PurePosixPath(pspdev_folder, target, "sdk", "lib")} -Wl,-zmax-page-size=128'

        self.buildenv_info.define_path("PSPDEV", pspdev_folder)

        #  this is not enough, I can kill that .....
        if not hasattr(self, "settings_target"):
            self.output.warning("This toolchain is meant only for cross-compiling!")
            return

        # interestingly I can reach that with
        # conan test --profile:build nsdk-default --profile:host default /Users/a4z/elux/conan/myrecipes/android-ndk/all/test_package android-ndk/r21d@
        if self.settings_target is None:
            self.output.warning("This toolchain is meant only for cross-compiling!")
            return

        # And if we are not building for Android, why bother at all
        if not self.settings_target.os == "PSP":
            self.output.warning(f"You've added {self.ref} as a build requirement, while os={self.settings_target.os} != Android")
            return

        self.conf_info.define_path("tools.build:sysroot", os.path.join(pspdev_folder, target))

        bin_folder = os.path.join(pspdev_folder, "bin")

        compiler_executable = {
                "c": os.path.join(bin_folder, f"{target}-gcc"),
                "cpp": os.path.join(bin_folder, f"{target}-g++")
                }
        self.conf_info.define("tools.build:compiler_executable", compiler_executable)

        self.conf_info.append_path("tools.cmake.cmaketoolchain:user_toolchain", os.path.join(pspdev_folder, "psp", "share", "pspdev.cmake"))
        self.conf_info.append_path("tools.cmake.cmaketoolchain:user_toolchain", os.path.join(pspdev_folder, "psp", "share", "AddPrxModule.cmake"))
        self.conf_info.append_path("tools.cmake.cmaketoolchain:user_toolchain", os.path.join(pspdev_folder, "psp", "share", "CreatePBP.cmake"))

        self.buildenv_info.define("CFLAGS", cflags)
        self.buildenv_info.define("CXXFLAGS", cflags)
        self.buildenv_info.define("ASMFLAGS", cflags)
        self.buildenv_info.define("LDFLAGS", ldflags) 

        self.buildenv_info.define_path("CC", os.path.join(bin_folder, f"{target}-gcc"))
        self.buildenv_info.define_path("CXX", os.path.join(bin_folder, f"{target}-g++"))
        self.buildenv_info.define_path("AS", os.path.join(bin_folder, f"{target}-g++"))
        self.buildenv_info.define_path("LD", os.path.join(bin_folder, f"{target}-g++"))

        self.buildenv_info.define_path("AR", os.path.join(bin_folder, f"{target}-ar"))
        self.buildenv_info.define_path("RANLIB", os.path.join(bin_folder, f"{target}-ranlib"))
        self.buildenv_info.define_path("READELF", os.path.join(bin_folder, f"{target}-readelf"))
        self.buildenv_info.define_path("OBJDUMP", os.path.join(bin_folder, f"{target}-objdump"))
        self.buildenv_info.define_path("OBJCOPY", os.path.join(bin_folder, f"{target}-objcopy"))
        self.buildenv_info.define_path("STRIP", os.path.join(bin_folder, f"{target}-strip"))

