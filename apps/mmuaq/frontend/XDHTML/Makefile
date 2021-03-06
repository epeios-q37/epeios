#	Copyright (C) 2016-2017 Claude SIMON (http://q37.info/contact/).
#
#	This file is part of MMUAq.
#
#	MMUAq is free software: you can redistribute it and/or
#	modify it under the terms of the GNU Affero General Public License
#	published by the Free Software Foundation, either version 3 of the
#	License, or (at your option) any later version.
#
#	MMUAq is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#	Affero General Public License for more details.
#
#	You should have received a copy of the GNU Affero General Public License
#	along with MMUAq. If not, see <http://www.gnu.org/licenses/>.

name = mmuaqxdh


# Epeios general debugging features
copt += -DE_DEBUG
# Required for multitasking
#copt += -DE_MT
# For using <setjmp.h> instead of C++ exceptions.
#copt += -DERR_JMPUSE
	
mods += ags aem bch bitbch bso 
mods += cio cpe crptgr cslio crt 
mods += ctn dir dte dtfbsc dtfptb 
mods += epsmsc err fdr flf flsq 
mods += flw flx ias idsq iof 
mods += iop lck lst lstbch lstcrt 
mods += lstctn mns mtk mtx ntvstr 
mods += que sdr stkbse stkbch stkctn 
mods += str strng tagsbs tol txf 
mods += tys uys utf xtf llio 
mods += bomhdl cdgb64 dlbrry fil fnm 
mods += lcl plgn plgncore rgstry stsfsm 
mods += xml xpp tht thtsub strmrg 
mods += csdrcc 
mods += fblcmd fblcst fblfep fblfph fblfrd 
mods += fblfrp fblovl fbltyp 
mods += sclargmnt sclmisc sclerror scllocale sclrgstry 
mods += sclxdhtml sclfrntnd 
mods += xdhcmn xdhdws 
mods += frdapi frdfrntnd frdrgstry 
mods += muafbc muainf 
mods += config login main prolog 
mods += agents agent folders Frame mail 
mods += mails 
mods += base core global instc registry 

pmods += pllio 

wmods += wllio 

##############################
# Common to all environment. #
##############################

# Generates debugging data.
#CXXFLAGS += -g

# General optimization.
CXXFLAGS += -O

# To use with gprof
#CXXFLAGS += -pg

###############################
	
copt += -DQ37_LIBRARY

win=win
win32=win32
win64=win64
IA_32=x86
AMD64=x64
Cygwin=Cygwin
MinGW=Msys
GNULinux=GNU/Linux
Linux=Linux
MacOS=Darwin
Android=Android
os=$(shell uname -o 2>/dev/null || uname -s)
mach=$(shell uname -m)
ifdef EPEIOS_SRC
 src += :..
 src += :../..
 src += :../../..
endif


##########################
# For Cygwin environment #
##########################

ifeq ("$(os)","$(Cygwin)")

# By default, vanilla Cygwin compiler ('g++') is used.
# Resulting application uses the Cygwin POSIX Layer.
# directly the MS CRT, see below.

# Use of the MinGW compiler under Cygwin. 
# To build native binary, i.e. with the MS CRT,
# without using the Cygwin/POSIX layer,
# Uncomment follwing line :
#target=$(win)

endif

##########################
		

#########################
# For MinGW environment #
#########################

ifeq ("$(os)", "$(MinGW)")
	co += -fpermissive
endif

#########################
		

#############################
# For GNU/Linux environment #
#############################

ifeq ("$(os)","$(GNULinux)")

endif

#############################
	

#########################
# For Linux environment #
#########################

ifeq ("$(os)","$(Linux)")

endif

#############################
	

##########################
# For MacOS environment #
##########################

ifeq ("$(os)","$(MacOS)")

endif

##########################
		
###################################
###################################
##### DON'T MODIFY BELOW !!! ######
###################################
###################################
			

##########################
# For Cygwin environment #
##########################

ifeq ("$(os)","$(Cygwin)")

	co += -std=gnu++11 -DUNICODE -D_FILE_OFFSET_BITS=64
	
	ifneq ("$(target)","$(Android)")
		libs += -lws2_32
		LDFLAGS += -static
	endif
	
	ifeq ("$(target)","$(win)")
		ifeq ("$(mach)","i686")
			override target=$(win32)
		else  # 'ifeq' on other line due to GNU 3.80 (Maemo on N900)
			ifeq ("$(mach)","x86_64")
				override target=$(win64)
			endif
		endif
	endif
	
	ifeq ("$(target)","$(IA_32)")
		override target=$(win32)
	else  # 'ifeq' on other line due to GNU 3.80 (Maemo on N900)
		ifeq ("$(target)","$(AMD64)")
			override target=$(win64)
		endif
	endif
	
	ifeq ("$(target)","$(win32)")
		CXX = i686-w64-mingw32-g++
		mods += $(wmods)
		lo += -municode -m32
		co += -m32
	else # 'ifeq' on other line due to GNU 3.80 (Maemo on N900)
		ifeq ("$(target)","$(win64)")
			CXX = x86_64-w64-mingw32-g++
			mods += $(wmods)
			lo += -municode -m64
			co += -m64
		else
			ifeq ("$(target)","$(Android)")
				CXX = C:/Users/csimon/AppData/Local/Android/sdk/ndk-bundle/toolchains/llvm/prebuilt/windows-x86_64/bin/clang++.exe
				mods += $(pmods)
				binary=lib$(name).so
				
				lo += -target i686-none-linux-android -gcc-toolchain C:/Users/csimon/AppData/Local/Android/sdk/ndk-bundle/toolchains/x86-4.9/prebuilt/windows-x86_64 --sysroot=C:/Users/csimon/AppData/Local/Android/sdk/ndk-bundle/platforms/android-14/arch-x86 -fPIC -g -DANDROID -ffunction-sections -funwind-tables -fstack-protector-strong -no-canonical-prefixes -Wa,--noexecstack -Wformat -Werror=format-security -fno-exceptions -fno-rtti -g -DANDROID -ffunction-sections -funwind-tables -fstack-protector-strong -no-canonical-prefixes -Wa,--noexecstack -Wformat -Werror=format-security -fno-exceptions -fno-rtti -fexceptions -std=c++11 -O0 -fno-limit-debug-info -O0 -fno-limit-debug-info  -Wl,--build-id -Wl,--warn-shared-textrel -Wl,--fatal-warnings -Wl,--no-undefined -Wl,-z,noexecstack -Qunused-arguments -Wl,-z,relro -Wl,-z,now -Wl,--build-id -Wl,--warn-shared-textrel -Wl,--fatal-warnings -Wl,--no-undefined -Wl,-z,noexecstack -Qunused-arguments -Wl,-z,relro -Wl,-z,now -shared
				
				co += -target i686-none-linux-android -gcc-toolchain C:/Users/csimon/AppData/Local/Android/sdk/ndk-bundle/toolchains/x86-4.9/prebuilt/windows-x86_64 --sysroot=C:/Users/csimon/AppData/Local/Android/sdk/ndk-bundle/platforms/android-14/arch-x86  -DXXX_DEBUG -Ih:/hg/epeios/stable -isystem C:/Users/csimon/AppData/Local/Android/sdk/ndk-bundle/sources/cxx-stl/gnu-libstdc++/4.9/include -isystem C:/Users/csimon/AppData/Local/Android/sdk/ndk-bundle/sources/cxx-stl/gnu-libstdc++/4.9/libs/x86/include -isystem C:/Users/csimon/AppData/Local/Android/sdk/ndk-bundle/sources/cxx-stl/gnu-libstdc++/4.9/include/backward -g -DANDROID -ffunction-sections -funwind-tables -fstack-protector-strong -no-canonical-prefixes -Wa,--noexecstack -Wformat -Werror=format-security -fno-rtti -fexceptions -std=c++11 -O0 -fno-limit-debug-info  -fPIC -MD
				
				libs += -ldl -landroid -llog -lm "C:/Users/csimon/AppData/Local/Android/sdk/ndk-bundle/sources/cxx-stl/gnu-libstdc++/4.9/libs/x86/libgnustl_static.a"
			else
				mods += $(pmods)
			endif
		endif
    
	endif
	
	ifneq ("$(target)","$(Android)")
		binary=$(name).dll
		lo += -Wl,--kill-at -shared
	endif


	dest=/cygdrive/h/bin/

endif

##########################
		

#########################
# For MinGW environment #
#########################

ifeq ("$(os)", "$(MinGW)")

	co += -DMSYS -std=gnu++11 -DUNICODE
	lo += -municode
	
	mods += $(wmods)

	LDFLAGS += -static

	ifeq ("$(target)","$(IA_32)")
		co += -m32
		lo += -m32
	else # 'ifeq' on other line due to GNU 3.80 (Maemo on N900).
		ifeq ("$(arch)","$(AMD64)")
			co += -m64
			lo += -m64
		endif
	endif

	binary=$(name).dll
	lo += -Wl,--kill-at -shared

	dest=/h/bin/
endif

#########################
		

#############################
# For GNU/Linux environment #
#############################

ifeq ("$(os)","$(GNULinux)")

	co += -std=gnu++11 -DUNICODE -D_FILE_OFFSET_BITS=64
	
	mods += $(pmods)
	
	libs += -lpthread -ldl -lrt

	ifeq ("$(target)","$(IA_32)")
		co += -m32
		lo += -m32
	else # 'ifeq' on other line due to GNU 3.80 (Maemo on N900).
		ifeq ("$(target)","$(AMD64)")
			co += -m64
			lo += -m64
		endif
	endif
	binary=lib$(name).so
	lo += -shared
	co += -fPIC

	dest=/home/csimon/bin/
endif

#############################
		

#########################
# For Linux environment #
#########################

ifeq ("$(os)","$(Linux)")

	co += -std=gnu++11 -DUNICODE -D_FILE_OFFSET_BITS=64
	
	mods += $(pmods)

	libs += -lpthread -ldl -lrt
	
	ifeq ("$(target)","$(IA_32)")
		co += -m32
		lo += -m32
	else # 'ifeq' on other line due to GNU 3.80 (Maemo on N900).
		ifeq ("$(target)","$(AMD64)")
			co += -m64
			lo += -m64
		endif
	endif
	binary=lib$(name).so
	lo += -shared
	co += -fPIC
endif

#############################
		

##########################
# For MacOS environment #
##########################

ifeq ("$(os)","$(MacOS)")

	co += -std=gnu++11 -DUNICODE -D_FILE_OFFSET_BITS=64
	
	mods += $(pmods)

	ifeq ("$(target)","$(IA_32)")
		co += -m32
		lo += -m32
	else # 'ifeq' on other line due to GNU 3.80 (Maemo on N900).
		ifeq ("$(target)","$(AMD64)")
			co += -m64
			lo += -m64
		endif
	endif
	binary=lib$(name).dylib
	lo += -dynamiclib

	dest=/Users/csimon/bin/
endif

##########################
		
all: $(binary)
	rm -rf *.o
ifeq ("$(target)","$(Android)")
	rm -rf *.d
endif

copt += -DVERSION=\""20170406"\"
copt += -DCOPYRIGHT_YEARS=\""2016-2017"\"
copt += -DIDENTIFIER=\""c8c33276-5e09-4f11-bd1b-3283b0ef0697"\"

ifndef EPEIOS_SRC
	src += :src:src/epeios
	out = ./
else
	src += :$(EPEIOS_SRC)
	out = $(dest)
endif

    
ox = o
ds = :

vpath %.cpp $(subst $(ds),:,$(src))
vpath %.mm $(subst $(ds),:,$(src))

srcd = $(subst $(ds), ,$(src))

co := -c $(co) $(copt) $(subst :, -I,$(src))
lo += -o $(binary) $(objs)

objs = $(name).$(ox) $(mods:=.$(ox))

$(binary): $(objs)
	$(CXX) $(lo) $(libs) $(LDFLAGS)
ifdef EPEIOS_SRC			
	mkdir -p $(out)
	cp $(binary) $(out)
endif

%.$(ox): %.cpp
	$(CXX) $(CPPFLAGS) $(co) $(CXXFLAGS) $<

clean:
	rm -rf *.o
ifeq ("$(target)","$(Android)")
	rm -rf *.d
endif


		