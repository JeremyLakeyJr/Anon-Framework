from setuptools import setup, find_packages

setup(
    name='anon-framework',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'anon-framework = anon_framework.main:main',
        ],
    },
    install_requires=[
        'pysocks',
    ],
    python_requires='>=3.6',
    author='Anon-Framework Contributors',
    description='A cross-platform framework for enhancing user anonymity and privacy.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/anon-framework/anon-framework', # Replace with your actual URL
    license='MIT',
)
