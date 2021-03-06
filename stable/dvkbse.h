/*
	Copyright (C) 1999 Claude SIMON (http://q37.info/contact/).

	This file is part of the Epeios framework.

	The Epeios framework is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

	The Epeios framework is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with the Epeios framework.  If not, see <http://www.gnu.org/licenses/>
*/

//	$Id: dvkbse.h,v 1.1 2012/12/04 16:05:43 csimon Exp $

#ifndef DVKBSE_INC_
#define DVKBSE_INC_

#define DVKBSE_NAME		"DVKBSE"

#define	DVKBSE_VERSION	"$Revision: 1.1 $"

#define DVKBSE_OWNER		"Claude SIMON"

#if defined( E_DEBUG ) && !defined( DVKBSE_NODBG )
#define DVKBSE_DBG
#endif

/* Begin of automatic documentation generation part. */

//V $Revision: 1.1 $
//C Claude SIMON (csimon at zeusw dot org)
//R $Date: 2012/12/04 16:05:43 $

/* End of automatic documentation generation part. */

/* Addendum to the automatic documentation generation part. */
//D DalViK BaSE. 
/* End addendum to automatic documentation generation part. */

/*$BEGIN$*/

# include "cpe.h"

# ifdef CPE_C_MSC
#  error "Non compilable avec VC++. Uitliser un environnement de compilation ddi  Dalvik (Android)'."
#endif


# include "err.h"
# include "flw.h"
# include "str.h"


# include "jvabse.h"

# include "android/log.h"

namespace dvkbse {
	inline  void Log(
		android_LogPriority Priority,
		const char *Tag,
		const char *Text )
	{
		if ( ( Text != NULL ) && ( *Text ) )
			__android_log_write( Priority, Tag, Text );
	}

	inline  void Log(
		android_LogPriority Priority,
		const char *Tag,
		const str::string_ &Text )
	{
	qRH
		STR_BUFFER___ Buffer;
	qRB
		Log( Priority, Tag, Text.Convert( Buffer ) );
	qRR
	qRT
	qRE
	}

	jclass GetRidClass(
		const char *PackageName,
		JNIEnv *Env );

	jclass GetRidClass(
		jstring JPackageName,
		JNIEnv *Env );

	jclass GetRlayoutClass(
		const char *PackageName,
		JNIEnv *Env );

	jclass GetRlayoutClass(
		jstring JPackageName,
		JNIEnv *Env );

	jclass GetRrawClass(
		jstring JPackageName,
		JNIEnv *Env );

	jclass GetRrawClass(
		const char *PackageName,
		JNIEnv *Env );

	jobject GetRawResourceInputStream(
		const char *Name,
		jclass Raw,
		JNIEnv *Env,
		jobject Activity );

	jobject GetRawResourceInputStream(
		const char *Name,
		const char *PackageName,
		JNIEnv *Env,
		jobject Activity );

	jobject GetRawResourceInputStream(
		const char *Name,
		jstring JPackageName,
		JNIEnv *Env,
		jobject Activity );

	inline jint GetRidToken(
		const char *Name,
		const char *PackageName,
		JNIEnv *Env )
	{
		return jvabse::GetStaticIntField(  Env, dvkbse::GetRidClass( PackageName, Env ), Name );
	}

	inline jint GetRlayoutToken(
		const char *Name,
		const char *PackageName,
		JNIEnv *Env )
	{
		return jvabse::GetStaticIntField(  Env, dvkbse::GetRlayoutClass( PackageName, Env ), Name );
	}

	inline void SetContentView(
		jint Id,
		jobject Activity,
		JNIEnv *Env )
	{
		Env->CallVoidMethod(
			Activity,
			jvabse::GetMethodID( Env, Activity, "setContentView", "(I)V" ),
			Id );
	}

	inline void SetContentView(
		const char *Name,
		const char *PackageName,
		jobject Activity,
		JNIEnv *Env )
	{
		SetContentView( GetRlayoutToken( Name, PackageName, Env ), Activity, Env );
	}

	inline jobject GetView(
		const jint Id,
		jobject Activity,
		JNIEnv *Env )
	{
		jobject View = Env->CallNonvirtualObjectMethod(
			Activity,
			jvabse::GetClass( Env, Activity ),
			jvabse::GetMethodID( Env, Activity, "findViewById", "(I)Landroid/view/View;" ),
			Id );

		if ( View == NULL )
			qRFwk();

		return View;
	}

	inline jobject GetView(
		const char *Name,
		const char *PackageName,
		jobject Activity,
		JNIEnv *Env )
	{
		return GetView( GetRidToken( Name, PackageName, Env ), Activity, Env );
	}
}

# define DVKBSE__L( Tag, Type, Priority )\
	inline void Log##Type( const char *Text )\
	{\
		dvkbse::Log( Priority, Tag, Text );\
	}\
	inline void Log##Type( const str::string_ &Text )\
	{\
		dvkbse::Log( Priority, Tag, Text );\
	}

# define DVKBSE_EXPOSE_LOG_FUNCTIONS( Tag )\
	DVKBSE__L( Tag, I, ANDROID_LOG_INFO )\
	DVKBSE__L( Tag, D, ANDROID_LOG_DEBUG )\
	DVKBSE__L( Tag, W, ANDROID_LOG_WARN )\
	DVKBSE__L( Tag, E, ANDROID_LOG_ERROR )\
	DVKBSE__L( Tag, F, ANDROID_LOG_FATAL )\
	

// Peut seulement tre utilis aprs un 'DVKBSE_EXPOSE_LOG_FUNCTIONS'.
# define DVKBSE_LOC	LogD( __LOC__ );


/*$END$*/
#endif
