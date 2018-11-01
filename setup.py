import setuptools, os

# with open("README.md", "r") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="molmod",
    version="0.0.2",
    author="Andriy Zhugayevych",
    description="Manager for QC calculations",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    license = 'GPL',
    keywords='Density Functional Theory Crystal modeling',
    packages=setuptools.find_packages(),
    install_requires=['numpy', 'paramiko'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
)
