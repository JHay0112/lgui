from setuptools import setup, find_packages

# Open readme
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name = 'lgui',
    packages = find_packages(include = [
        "lgui",
        "lgui.*"
    ]),
    version = "v0.1.0",
    description = "An IPython/Jupyter Interface for lcapy",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    author = "Jordan Hay",
    license = "MIT",
    url = "https://github.com/JHay0112/lgui",
    project_urls={
        "Bug Tracker": "https://github.com/JHay0112/jmath/lgui",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "numpy",
        "lcapy",
        "ipywidgets",
        "IPython",
        "ipycanvas"
    ],
    python_requires=">=3.10" # due to match statements
)