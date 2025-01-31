from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy

required_conan_version = ">=1.53.0"


class ZlibConan(ConanFile):
    name = "libpspvram"
    package_type = "static-library"
    # url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/elvisdukaj/libpspvram"
    license = "MIT"
    description = "Dynamic VRAM allocation manager for the PSP"
    topics = ("psp", "homebrew", "vram")

    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self) 

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self,
             pattern="LICENSE",
             src=self.source_folder,
             dst=self.package_folder)

    def package_info(self):
        self.cpp_info.components["vramalloc"].libs = ["pspvramalloc"]
        self.cpp_info.components["vram"].libs = ["pspvram"]
