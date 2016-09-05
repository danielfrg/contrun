from setuptools import setup, find_packages
import versioneer

install_requires = []
with open('requirements.txt') as f:
    for line in f.readlines():
        req = line.strip()
        if not req or req.startswith(('-e', '#')):
            continue
        install_requires.append(req)

setup(name="contrun",
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description="Run any command continuously on file changes",
      install_requires=install_requires,
      url="https://github.com/danielfrg/contrun",
      maintainer="Daniel Rodriguez",
      maintainer_email="df.rodriguez143@gmail.com",
      license="Apache 2.0",
      packages=find_packages(),
      zip_safe=False,
      entry_points="""
        [console_scripts]
        contrun=contrun.cli:main
      """,)
