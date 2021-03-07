import setuptools

with open("README.md", "r", encoding="utf-8") as fp:
    long_description = fp.read()

setuptools.setup(
    name="redcapp",
    version="1.0.0",
    author="Will Fatherley",
    author_email="wefatherley@gmail.com",
    description="Exposes the REDCap API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wefatherley/redcapp",
    project_urls={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
