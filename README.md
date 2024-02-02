# CBlib: Closed Branch library
*Authors*:
- Imanol Etxezarreta
- Ton De Marti Olius
- Josu Etxezarreta

## Description
This branch focuses in optimizing the classes and methods associated to these that conform the Closed Branch Decoder, implementing those in C++ and making them available to pythone source code of the decoder as an interface.

## Building
At this initial moment, the build script as a Makefile only supports linux platforms with g++ compiler. It generates a `build/` folder which holds the object files and the generated shared library in `build/lib/CBlib.so`. To build the shared library, the following steps can be followed:
```bash
git clone -b CBlib https://github.com/Tonidmo/CBDec.git
make
```
To be continued...