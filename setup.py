from setuptools import setup, find_packages

setup(
    name="physis",
    version="0.1.0",
    author="Bereket Gebrehawerya Kahsay",
    author_email="onewolf1221@gmail.com",
    description="Engine design library for internal combustion engines",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bereket1221ai/physis",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)