from setuptools import setup, find_packages

# Function to load dependencies from requirements.txt
def load_requirements(filename="requirements.txt"):
    with open(filename, "r") as file:
        return file.read().splitlines()

setup(
    name="photo-organizer",
    version="1.0.0",
    description="A Python tool for organizing photos and videos by metadata into date-based folder structures",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="HecticEnergy",
    url="https://github.com/HecticEnergy/photo_sorter_py",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=load_requirements(),
    entry_points={
        "console_scripts": [
            "photo-organizer=photo_organizer.__main__:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics",
        "Topic :: System :: Archiving",
        "Topic :: Utilities",
    ],
    python_requires=">=3.9",
    keywords="photo video organizer metadata exif date sorting",
    project_urls={
        "Bug Reports": "https://github.com/HecticEnergy/photo_sorter_py/issues",
        "Source": "https://github.com/HecticEnergy/photo_sorter_py",
    },
)
