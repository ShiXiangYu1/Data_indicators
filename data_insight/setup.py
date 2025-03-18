from setuptools import setup, find_packages

setup(
    name="data_insight",
    version="0.1.0",
    description="数据指标解读系统，用于自动化数据解读和洞察生成",
    author="AI数据分析团队",
    author_email="ai_team@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "scikit-learn>=1.0.0",
        "langchain>=0.0.260",
        "openai>=0.27.0",
        "python-dotenv>=1.0.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
) 