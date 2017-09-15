# *XPPq* changelog.

2017-09-15 :
- *xppqnjs*
    - Adaptation to changes in underlying libraries.
2017-09-13 :
- *xppqnjs*
    - Adding file for *Runkit* (`runkit.js`).

2017-09-12 :
- *xppqnjs*
  - Simplification in the hope it will help to fix some bugs.
  - Workaround for some bugs, because there are some incoherencies in *Node.js* (see comments in source files) !
  - Fixing bad translation of error messages.

2017-09-08 :
- *xppqnjs*
  - Adding `DONE` tag, corresponding to the reaching the end of the stream.
  - Fixing bad `stream.Readable.readable` event handling.

2017-08-31 :
- *XPPq* is now available as *Node.js* *addon*.

2016-09-30 :
- *AArch64* (*ARM* 64-bit) version available.

2015-10-11 :
- `fdr::datum__` -> `fdr::byte__`.

2015-06-04 :
- No changes in the software itself, but only in the content of the packages.

2015-05-28
- `locale.(h|cpp)` becomes `i18n(.h|.cpp)` to avoid confusion with the `locale.h` standard *C* header.

2015-05-27
- Creation, as replacement of *expp*.