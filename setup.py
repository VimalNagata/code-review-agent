from setuptools import setup, find_packages

setup(
    name="code_review_agent",
    version="0.1.0",
    description="An agent that reviews code and generates integration tests",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "pytest>=7.0.0",
        "requests>=2.25.0",
    ],
    entry_points={
        'console_scripts': [
            'code-review-agent=src.agent:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)