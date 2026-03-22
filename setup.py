from setuptools import setup, find_packages

setup(
    name="agent-swarm-lite",
    version="0.1.0",
    description="Lightweight Python framework for multi-agent orchestration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Mukunda Katta",
    author_email="mukunda.vjcs6@gmail.com",
    url="https://github.com/MukundaKatta/agent-swarm-lite",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "pydantic>=2.0",
        "httpx>=0.25",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
