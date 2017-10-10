from setuptools import setup, find_packages

classifiers = [
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: BSD License",
    "Topic :: Games/Entertainment",
    "Topic :: System :: Emulators"
]

setup(name="mgba-gamedata",
      version="0.0.1",
      use_2to3=True,
      author="Vicki Pfau",
      author_email="vi@endrift.com",
      url="http://github.com/mgba-emu/gamedata/",
      packages=find_packages(),
      setup_requires=['pytest-runner'],
      install_requires=['venusian', 'cached-property'],
      tests_require=['pytest', 'pytest-flake8'],
      license="BSD",
      classifiers=classifiers
      )
