from setuptools import setup, find_packages

# Function to load dependencies from requirements.txt
def load_requirements(filename="requirements.txt"):
    with open(filename, "r") as file:
        return file.read().splitlines()

setup(
    name="PhotoVideoOrganizer",
    version="1.0.0",
    description="A tool for organizing photos and videos based on metadata",
    author="Your Name",
    packages=find_packages(),  # Automatically include all sub-packages
    install_requires=load_requirements(),  # Dynamically read dependencies
    entry_points={
        "console_scripts": [
            "organize=src.main:main",  # Entry point for the CLI tool
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",  # Specify the required Python version
)
