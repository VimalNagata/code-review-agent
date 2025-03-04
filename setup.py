from setuptools import setup, find_packages

setup(
    name="code_review_agent",
    version="0.1.0",
    description="An agent that reviews code and generates integration tests",
    author="Vimal Nagata",
    author_email="vimalnagata@example.com",
    packages=find_packages(),
    install_requires=[
        "pytest>=7.0.0",
        "requests>=2.25.0",
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "accelerate>=0.20.0"
    ],
    entry_points={
        'console_scripts': [
            'code-review-agent=src.agent:main',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance"
    ],
)