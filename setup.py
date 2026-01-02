from setuptools import setup, find_packages
import os


def read_readme():
    """读取README.md作为长描述"""
    here = os.path.abspath(os.path.dirname(__file__))
    try:
        with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "大学物理实验数据处理库"


setup(
    name="phyexp",
    version="0.1.0",  # 版本号，可根据实际情况修改
    author="Log-Dog012",  # 从LICENSE推测的作者
    author_email="",  # 可补充作者邮箱
    description="大学物理实验数据处理工具库",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://gitee.com/Log-Dog012/phyexp",  # 项目仓库地址
    packages=find_packages(),
    install_requires=[
        "numpy>=1.18.0",
        "matplotlib>=3.3.0",
        "pint>=0.18",
        "uncertainties>=3.1.6",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.6",  # 最低Python版本要求
    license="MIT",
)
