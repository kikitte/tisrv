from setuptools import setup, find_packages

setup(
    name='tisrv',
    description='A tile server implementing the OGC Tiles API Spec',
    author='kikitte',
    author_email='kikitte.lee@gmail.com',
    license='MIT',
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=[
        'fastapi>=0.75.0',
        'morecantile>=3.1.1',
        'asyncpg>=0.25.0',
        'python-dotenv>=0.19.2'
    ]
)
