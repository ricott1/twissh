import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hack-n-ssh-ricott1",
    version="0.0.1",
    author="Alessandro Ricottone",
    author_email="ricott2@gmail.com",
    description="Hack\'n\'ssh server exec",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ricott1/hack-n-ssh",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)