/*
	'ndbdct' library by Claude SIMON (csimon at zeusw dot org)
	Requires the 'ndbdct' header file ('ndbdct.h').
	Copyright (C) 2004 Claude SIMON.

	This file is part of the Epeios (http://zeusw.org/epeios/) project.

	This library is free software; you can redistribute it and/or
	modify it under the terms of the GNU General Public License
	as published by the Free Software Foundation; either version 2
	of the License, or (at your option) any later version.
 
	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; if not, go to http://www.fsf.org/
	or write to the:
  
         	         Free Software Foundation, Inc.,
           59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
*/



//	$Id: ndbdct.cpp,v 1.24 2013/04/15 10:50:52 csimon Exp $

#define NDBDCT__COMPILATION

#include "ndbdct.h"

class ndbdcttutor
: public ttr_tutor
{
public:
	ndbdcttutor( void )
	: ttr_tutor( NDBDCT_NAME )
	{
#ifdef NDBDCT_DBG
		Version = NDBDCT_VERSION "\b\bD $";
#else
		Version = NDBDCT_VERSION;
#endif
		Owner = NDBDCT_OWNER;
		Date = "$Date: 2013/04/15 10:50:52 $";
	}
	virtual ~ndbdcttutor( void ){}
};

/******************************************************************************/
				  /* do not modify anything above this limit */
				  /*			  unless specified			 */
				  /*******************************************/
/*$BEGIN$*/

#include "flf.h"

using namespace ndbdct;

#define AVAILABLES_FILE_NAME_EXTENSION	".eda"
#define CONTENT_FILE_NAME_EXTENSION		".edc"
#define ENTRIES_FILE_NAME_EXTENSION		".ede"
#define LIST_FILE_NAME_EXTENSION		".edl"

static inline void Save_(
	sdr::row__ Row,
	flw::oflow__ &Flow )
{
	dtfptb::FPut( *Row, Flow );
}

static inline void Save_(
	const available__ &Available,
	flw::oflow__ &Flow )
{
	dtfptb::FPut( *Available.Row, Flow );
	dtfptb::FPut( Available.RawSize, Flow );
}

template <typename item> static void Save_(
	const stk::E_BSTACK_( item ) &Bunch,
	flw::oflow__ &Flow )
{
	stk::row__ Row = Bunch.First();

	while ( Row != E_NIL ) {
		Save_( Bunch( Row ), Flow );

		Row = Bunch.Next( Row );
	}
}

template <typename item> static void Save_(
	const stk::E_BSTACK_( item ) &Bunch,
	const fnm::name___ &FileName )
{
ERRProlog
	flf::file_oflow___ Flow;
ERRBegin
	Flow.Init( FileName );

	Save_( Bunch, Flow );
ERRErr
ERREnd
ERREpilog
}

template <typename item> static void Save_(
	const stk::E_BSTACK_( item ) &Bunch,
	const str::string_ &BaseFileName,
	const char *Extension,
	time_t ReferenceTimeStamp )
{
ERRProlog
	str::string FileName;
ERRBegin
	FileName.Init( BaseFileName );
	FileName.Append( Extension );

	if ( !fil::Exists( FileName )
		 || ( fil::GetLastModificationTime( FileName ) <= ReferenceTimeStamp ) )
			Save_( Bunch, FileName );

	while ( ReferenceTimeStamp >= fil::GetLastModificationTime( FileName ) ) {
		tol::EpochTime( true );
		fil::Touch( FileName );
	}
ERRErr
ERREnd
ERREpilog
}

void ndbdct::files_hook___::_SaveAvailables( void ) const
{
	Save_( _Content->Availables, _BaseFileName, AVAILABLES_FILE_NAME_EXTENSION, GetUnderlyingFilesLastModificationTime() );
}

static inline void Load_(
	flw::iflow__ &Flow,
	sdr::row__ &Row )
{
	dtfptb::FGet( Flow, *Row );
}
	
static inline void Load_(
	flw::iflow__ &Flow,
	available__ &Available )
{
	dtfptb::FGet( Flow, Available.Row );
	dtfptb::FGet( Flow, Available.RawSize );
}
	

template <typename item> static void Load_(
	flw::iflow__ &Flow,
	stk::E_BSTACK_( item ) &Bunch )
{
	item Item;

	while ( !Flow.EndOfFlow() ) {
		Load_( Flow, Item );
		Bunch.Append( Item );
	}
}

template <typename item> static bso::bool__ Load_(
	const char *FileName,
	stk::E_BSTACK_( item ) &Bunch,
	time_t ReferenceTimeStamp )
{
	bso::bool__ Success = false;
ERRProlog
	flf::file_iflow___ Flow;
ERRBegin
	if ( Flow.Init( FileName, err::hUserDefined ) == tol::rSuccess ) {
		if ( fil::GetLastModificationTime( FileName ) <= ReferenceTimeStamp )
			ERRReturn;

		Load_( Flow, Bunch );

		Flow.reset();

		Success = true;
	}
ERRErr
ERREnd
ERREpilog
	return Success;
}

const char *BuildFileName_(
	const str::string_ &BaseFileName,
	const char *Extension,
	TOL_CBUFFER___ &Buffer )
{
ERRProlog
	str::string FileName;
ERRBegin
	FileName.Init( BaseFileName );
	FileName.Append( Extension );
	FileName.Convert( Buffer );
ERRErr
ERREnd
ERREpilog
	return Buffer;
}


template <typename item> static bso::bool__ Load_(
	const str::string_ &BaseFileName,
	stk::E_BSTACK_( item ) &Bunch,
	item TestValue,
	const char *Extension,
	time_t TimeStamp )
{
	bso::bool__ Success = false;
ERRProlog
	TOL_CBUFFER___ Buffer;
ERRBegin
	Success = Load_( BuildFileName_( BaseFileName, Extension, Buffer ), Bunch, TestValue, TimeStamp );
ERRErr
ERREnd
ERREpilog
	return Success;
}

static bso::bool__ LoadAvailables_(
	const str::string_ &BaseFileName,
	availables_ &Availables,
	time_t ReferenceTimeStamp )
{
	bso::bool__ Success = false;
ERRProlog
	TOL_CBUFFER___ Buffer;
ERRBegin
	Success = Load_( BuildFileName_( BaseFileName, AVAILABLES_FILE_NAME_EXTENSION, Buffer ), Availables, ReferenceTimeStamp );
ERRErr
ERREnd
ERREpilog
	return Success;
}

bso::bool__ ndbdct::files_hook___::_LoadAvailables( void )
{
	return LoadAvailables_( _BaseFileName, _Content->Availables, GetUnderlyingFilesLastModificationTime() );
}

void ndbdct::files_hook___::Init(
	const str::string_ &BaseFileName,
	fil::mode__ Mode,
	fls::id__ ID )
{
ERRProlog
	str::string ContentFileName;
	TOL_CBUFFER___ ContentFileNameBuffer;
	str::string EntriesBunchFileName;
	TOL_CBUFFER___ EntriesBunchFileNameBuffer;
	str::string EntriesListFileName;
	TOL_CBUFFER___ EntriesListFileNameBuffer;
ERRBegin
	reset();

	ContentFileName.Init( BaseFileName );
	ContentFileName.Append( CONTENT_FILE_NAME_EXTENSION );
	_Storage.Init( ContentFileName.Convert( ContentFileNameBuffer ), Mode, true, ID );

	EntriesBunchFileName.Init( BaseFileName );
	EntriesBunchFileName.Append( ENTRIES_FILE_NAME_EXTENSION );

	EntriesListFileName.Init( BaseFileName );
	EntriesListFileName.Append( LIST_FILE_NAME_EXTENSION );

	_Entries.Init( EntriesBunchFileName.Convert( EntriesBunchFileNameBuffer) , EntriesListFileName.Convert( EntriesListFileNameBuffer ), Mode, true, ID );

	_BaseFileName.Init( BaseFileName );
	_Mode = Mode;
ERRErr
ERREnd
ERREpilog
}

bso::bool__ Test_(
	const str::string_ &BaseFileName,
	const char *Extension,
	time_t TimeStamp )
{
	bso::bool__ Success = false;
ERRProlog
	TOL_CBUFFER___ Buffer;
	const char *FileName = NULL;
ERRBegin
	FileName = BuildFileName_( BaseFileName, Extension, Buffer );

	if ( !fil::Exists( FileName ) )
		ERRReturn;

	if ( fil::GetLastModificationTime( FileName ) <= TimeStamp )
		ERRReturn;

	Success = true;
ERRErr
ERREnd
ERREpilog
	return Success;
}

void ndbdct::files_hook___::_ErasePhysically( void )
{
ERRProlog
ERRBegin
	_Storage.Drop();
	_Entries.Drop();

	ndbbsc::DropFile( _BaseFileName, AVAILABLES_FILE_NAME_EXTENSION );
ERRErr
ERREnd
ERREpilog
}

uys::state__ ndbdct::Plug(
	dynamic_content_ &Content,
	files_hook___ &Hook )
{
	uys::state__ State = tys::Plug( Content.Storage.Memory, Hook.StorageFilesHook() );

	if ( uys::IsError( State ) ) {
		Hook.reset();
		return State;
	}

	if ( lstbch::Plug( Content.Entries, Hook.EntriesFilesHook() ) != State ) {
		Hook.reset();
		return uys::sInconsistent;
	}

	Hook.Set( Content );

	Content.S_.Unallocated = Hook.StorageFilesHook().Size();

	if ( uys::Exists( State ) )
		if ( !Test_( Hook.BaseFileName(), AVAILABLES_FILE_NAME_EXTENSION, Hook.GetUnderlyingFilesLastModificationTime() ) ) {
			Hook.reset();
			State = uys::sInconsistent;
		}

	return State;
}


/* Although in theory this class is inaccessible to the different modules,
it is necessary to personalize it, or certain compiler would not work properly */

class ndbdctpersonnalization
: public ndbdcttutor
{
public:
	ndbdctpersonnalization( void )
	{
		/* place here the actions concerning this library
		to be realized at the launching of the application  */
	}
	~ndbdctpersonnalization( void )
	{
		/* place here the actions concerning this library
		to be realized at the ending of the application  */
	}
};


/*$END$*/
				  /********************************************/
				  /* do not modify anything belove this limit */
				  /*			  unless specified		   	  */
/******************************************************************************/

// 'static' by GNU C++.

static ndbdctpersonnalization Tutor;

ttr_tutor &NDBDCTTutor = Tutor;
