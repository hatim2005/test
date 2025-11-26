from setuptools import setup, find_packages

setup(
    name="color-ml",
    version="1.0.0",
    description="Machine Learning library for advanced color correction",
    author="Color Correction Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.21.0",
        "opencv-python>=4.5.0",
        "torch>=2.0.0",
        "torchvision>=0.15.0",
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
