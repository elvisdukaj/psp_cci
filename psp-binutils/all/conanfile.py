import os
import re
import typing
import unittest

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path

required_conan_version = ">=1.54.0"

# This recipe includes a selftest to test conversion of os/arch to triplets (and vice verse)
# Run it using `python -m unittest conanfile.py`


class BinutilsConan(ConanFile):
    name = "psp-binutils"
    description = "The GNU Binutils are a collection of binary tools."
    package_type = "application"
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "https://www.gnu.org/software/binutils"
    topics = ("gnu", "ld", "linker", "as", "assembler", "objcopy", "objdump")
    settings = "os", "arch", "compiler", "build_type"

    _target_os = "psp"
    _target_arch = "mips"

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _settings_target(self):
        return getattr(self, "settings_target", None) or self.settings

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("This recipe does not support building binutils by this compiler")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type="str"):
                self.tool_requires("msys2/cci.latest")
        self.tool_requires("bison/3.8.2")
        self.tool_requires("flex/2.6.4")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("gmp/6.3.0")
        self.requires("mpfr/4.2.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _dependency_package_folder(self, dep):
        return unix_path(self, self.dependencies[dep].package_folder)

    def generate(self):
        ve = VirtualBuildEnv(self)
        env = ve.environment()
        env.define_path("PREFIX", self.package_folder)
        ve.generate()

        sysroot = unix_path(self, os.path.join(self._target_os))

        tc = AutotoolsToolchain(self)
        tc.configure_args.append(f"--target={self._target_os}")
        tc.configure_args.append(f'--with-sysroot={sysroot}')
        tc.configure_args.append("--enable-plugins")
        tc.configure_args.append("--disable-initfini-array")
        tc.configure_args.append("--with-python=no") 
        tc.configure_args.append("--disable-werror")
        tc.configure_args.append(f'--with-gmp={self._dependency_package_folder("gmp")}')
        tc.configure_args.append(f'--with-mpfr={self._dependency_package_folder("mpfr")}')
        tc.configure_args.append(f'--with-zlib={self._dependency_package_folder("zlib")}')
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"), recursive=True)
        copy(
            self,
            pattern="COPYING*",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
            keep_path=False,
        )

    def package_info(self):
        target_bindir = os.path.join(self.package_folder, self._target_os, "bin")
        self.cpp_info.bindirs = ["bin", target_bindir]

