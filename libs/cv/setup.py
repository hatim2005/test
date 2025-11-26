from setuptools import setup, find_packages

setup(
    name="color-cv",
    version="1.0.0",
    description="Computer Vision library for color correction",
    author="Color Correction Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.21.0",
        "opencv-python>=4.5.0",
        "opencv-contrib-python>=4.5.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
