import setuptools

version = "0.13.4"

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="atlastk",
    version=version,
    author="Claude SIMON",
#    author_email="author@example.com",
    description="World's lightest toolkit to quickly and easily add a GUI to your Python programs and bring them online. ",
    keywords="GUI, web, Atlas toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://atlastk.org",
    packages=setuptools.find_packages(),
    classifiers=[
      "Environment :: Web Environment",
      "Development Status :: 5 - Production/Stable",
      "Intended Audience :: Developers",
      "Intended Audience :: Education",
      "Intended Audience :: Other Audience",
      "License :: OSI Approved :: MIT License ",
      "Operating System :: OS Independent",
      "Programming Language :: Python :: 3",
      "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
      "Topic :: Software Development :: User Interfaces"
    ]
)
