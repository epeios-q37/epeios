# *ZNDq* changelog

## 2018-08-07
- using `zend_long` (which can have a length of 32 or 64 bits) instead of `bso::s64`,

## 2018-04-28
- handling the fact as, in *CGI* mode, the same script is called several times, but initialization and registering must only occur the first time,
- handling the fact that *zndq* can be used simultaneously by different extension,

## 2018-04-09

- adaptation to changes in underlying modules,

## 2018-01-17:

- `init(...)` receives now the location where the locale and configuration will be found as parameter,
- handling array of strings,

## 2017-12-20:

- the wrapper can now be loaded more than once; two *addon*s based on this wrapper can now be used together,

## 2017-10-29:

- adding *Stream* handling,
- fixing `varargs` handling,
- changing naming to match *PHP* rules.