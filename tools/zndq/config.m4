PHP_ARG_ENABLE(zndq, whether to enable ZNDq support, [ --enable-zndq   Enable ZNDq support])

src=.
epeios=../../stable

if test "$PHP_ZNDQ" = "yes"; then
  PHP_REQUIRE_CXX()
  AC_DEFINE(HAVE_ZNDQ, 1, [Whether you have ZNDq])
  PHP_NEW_EXTENSION(zndq, zndq.cpp "epeios/dlbrry.cpp" "epeios/plgn.cpp" "epeios/ags.cpp" "epeios/aem.cpp" "epeios/bch.cpp" "epeios/bitbch.cpp" "epeios/bomhdl.cpp" "epeios/bso.cpp" "epeios/cdgb64.cpp" "epeios/cio.cpp" "epeios/cpe.cpp" "epeios/crptgr.cpp" "epeios/cslio.cpp" "epeios/crt.cpp" "epeios/ctn.cpp" "epeios/dir.cpp" "epeios/dte.cpp" "epeios/dtfbsc.cpp" "epeios/dtfptb.cpp" "epeios/epsmsc.cpp" "epeios/err.cpp" "epeios/fdr.cpp" "epeios/fil.cpp" "epeios/flf.cpp" "epeios/flsq.cpp" "epeios/flw.cpp" "epeios/flx.cpp" "epeios/fnm.cpp" "epeios/ias.cpp" "epeios/idsq.cpp" "epeios/iof.cpp" "epeios/iop.cpp" "epeios/lcl.cpp" "epeios/lck.cpp" "epeios/lst.cpp" "epeios/lstbch.cpp" "epeios/lstcrt.cpp" "epeios/lstctn.cpp" "epeios/mns.cpp" "epeios/mtk.cpp" "epeios/mtx.cpp" "epeios/ntvstr.cpp" "epeios/que.cpp" "epeios/rgstry.cpp" "epeios/sdr.cpp" "epeios/stkbse.cpp" "epeios/stkbch.cpp" "epeios/stkcrt.cpp" "epeios/stkctn.cpp" "epeios/str.cpp" "epeios/strng.cpp" "epeios/stsfsm.cpp" "epeios/tagsbs.cpp" "epeios/tht.cpp" "epeios/tol.cpp" "epeios/txf.cpp" "epeios/tys.cpp" "epeios/uys.cpp" "epeios/utf.cpp" "epeios/xml.cpp" "epeios/xpp.cpp" "epeios/xtf.cpp" "epeios/llio.cpp" "epeios/sclargmnt.cpp" "epeios/sclmisc.cpp" "epeios/sclerror.cpp" "epeios/scllocale.cpp" "epeios/sclrgstry.cpp" "main.cpp" "registry.cpp" , $ext_shared,, [-std=gnu++11 -I/home/csimon/hg/epeios/stable -DVERSION=20171008] )
fi
