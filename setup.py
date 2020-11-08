import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pthat-drizztguen77",
    version="0.9.0",
    author="Curtis White",
    author_email="drizztguen77@gmail.com",
    description="A package containing the API for the PTHat by CNC Design Limited",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/drizztguen77/PTHat",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.6',
)
