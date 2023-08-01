from setuptools import setup
from deeplogs import __version__

install_requires = [
    "matplotlib==3.7.2",
    "pandas==2.0.3",
    "plotly==5.15.0",
]

setup(
    name="deeplogs",
    version=__version__,
    url="https://github.com/guychahine/deeplogs",
    description="Simplified Python Logging and Progress Tracking",
    author="Guy Chahine",
    author_email="guychahine@gmail.com",
    packages=["deeplogs"],
    install_requires=install_requires,
    license="BSD",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: System :: Logging",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Science/Research",
    ],
    python_requires=">=3.10",
)