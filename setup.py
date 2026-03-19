from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-auto-operator",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered mouse and keyboard automation system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai-auto-operator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyautogui>=0.9.54",
        "pynput>=1.7.6",
        "Pillow>=10.0.0",
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "pytesseract>=0.3.10",
        "easyocr>=1.7.0",
        "openai>=1.3.0",
        "anthropic>=0.8.0",
        "PyYAML>=6.0.1",
        "python-dotenv>=1.0.0",
        "click>=8.1.7",
        "colorama>=0.4.6",
        "loguru>=0.7.0",
    ],
    entry_points={
        "console_scripts": [
            "ai-auto=main:cli",
        ],
    },
)