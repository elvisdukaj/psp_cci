from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, export_conandata_patches, apply_conandata_patches 
from conan.tools.layout import basic_layout


required_conan_version = ">=2"

class OpenGXConan(ConanFile):
    name = "pspgl"
    description = "OpenGL-ESish library for PSP"
    # url = "https://github.com/devkitPro/opengx"
    homepage = "https://github.com/elvisdukaj/pspgl"
    license = 'BSD 3-Clause "New" or "Revised"'
    package_type = "static-library"
    topics = ("psp", "opengles", "opengl")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "static-library"



    def build_requirements(self):
        self.tool_requires("pspdev/v20250101")
        self.tool_requires("make/4.4.1")

    def validate(self):
        valid_os = ["PSP"]
        if str(self.settings.os) not in valid_os:
            raise ConanInvalidConfiguration(f"{self.name} {self.version} is only supported for the following operating systems: {valid_os}")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        basic_layout(self)

    def generate(self):
        ve = VirtualBuildEnv(self)
        env = ve.environment()
        env.define_path("PREFIX", self.package_folder)
        ve.generate()

    def build(self):
        apply_conandata_patches(self)
        self.run("make -j", cwd=self.source_folder)

    def package(self):
        self.run("make install", cwd=self.source_folder)


    def package_info(self):
        supported_os = ["PSP"]
        if self.settings.os not in supported_os:
            self.output.warning(f"{self.settings.os} not supported. Supported os are {supported_os}")

        self.cpp_info.libs = ["GL", "GLU", "glut"]
        self.cpp_info.set_property("cmake_file_name", "OpenGL")
        self.cpp_info.set_property("cmake_target_name", "OpenGL::GL")

