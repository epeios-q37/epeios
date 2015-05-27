/*
	Copyright (C) 2000-2015 Claude SIMON (http://q37.info/contact/).

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

#define MMM__COMPILATION

#include "mmm.h"


using namespace mmm;

static void Display_(
	row__ Position,
	txf::text_oflow__ &Flow )
{
	if ( Position == NONE )
		Flow << "NONE";
	else
		Flow << *Position;
}

void mmm::multimemory_::DisplayStructure( txf::text_oflow__ &Flow ) const
{
	bso::ulong__ UsedFragmentTotalSize = 0, UsedFragmentDataSize = 0, FreeFragmentSize = 0;

	Flow << "Size : " << _Size() << txf::tab;
	Flow << "FreeFragment : ";
	Display_( S_.FreeFragment, Flow );
	Flow << txf::tab;

	Flow << "Tailing free fragment position : ";
	Display_( S_.TailingFreeFragmentPosition, Flow );
	
	Flow << txf::nl;

	Flow << "Pos." << txf::tab << "  State" << txf::tab << "Size" << txf::tab << "Next" << txf::tab << "DataS" << txf::tab << txf::tab << "PF" << txf::tab << "NF/L" << txf::nl;

	if ( _Size() != 0 ) {
		row__ Position = 0;
		mdr::datum__ Header[MMM_HEADER_MAX_LENGTH];

		while ( Position != NONE ) {
			Flow << *Position << txf::tab << ": ";

			_GetHeader( Position, Header );

			if ( _IsFragmentUsed( Header ) ) {
				Flow << "USED" << txf::tab << _GetUsedFragmentTotalSize( Header ) << txf::tab << ( *Position + _GetUsedFragmentTotalSize( Header ) ) << txf::tab << _GetUsedFragmentDataSize( Header ) << txf::tab << txf::tab;

				UsedFragmentTotalSize += _GetUsedFragmentTotalSize( Header );
				UsedFragmentDataSize += _GetUsedFragmentDataSize( Header );

				if ( _IsUsedFragmentFreeFlagSet( Header ) )
					Flow << *_GetFreeFragmentPosition( Position );
				else
					Flow << "NONE";

				Flow << txf::tab;

				if ( _IsUsedFragmentLinkFlagSet( Header ) )
					Flow << *_GetUsedFragmentLink( Position, Header );
				else
					Flow << "NONE";

				Position = _GetUsedFragmentNextFragmentPosition( Position, Header );
			} else if ( _IsFragmentFree( Header ) ) {
				if ( _IsFreeFragmentOrphan( Header ) ) {
					Flow << "Orph." << txf::tab << _GetFreeFragmentSize( Header ) << txf::tab << ( *Position + _GetFreeFragmentSize( Header ) ) << txf::tab;
				} else {
					Flow << "Free" << txf::tab << _GetFreeFragmentSize( Header ) << txf::tab << ( *Position + _GetFreeFragmentSize( Header ) ) << txf::tab << txf::tab << txf::tab;
					Display_( _GetFreeFragmentPreviousFreeFragmentPosition( Header ), Flow );
					Flow << txf::tab;
					Display_( _GetFreeFragmentNextFreeFragmentPosition( Header ), Flow );
				}

				FreeFragmentSize += _GetFreeFragmentSize( Header );

				Position = _GetFreeFragmentNextFragmentPosition( Position, Header );
			} else
				ERRc();

			Flow << txf::nl;

			if ( Position == _Size() )
				Position = NONE;
			else if ( *Position > _Size() )
				ERRc();

		}

		Flow << "DS : " << UsedFragmentDataSize << txf::tab << "OH : " << ( 100 * ( UsedFragmentTotalSize - UsedFragmentDataSize ) ) / UsedFragmentDataSize << '%' << txf::tab << "FS : " << FreeFragmentSize << txf::tab << "R : " << ( 100 * FreeFragmentSize ) / UsedFragmentDataSize << '%' << txf::nl; 
	}
}

void mmm::multimemory_file_manager___::_WriteFreeFragmentPositions( void )
{
ERRProlog
	flf::file_oflow___ OFlow;
ERRBegin
	OFlow.Init( _FreeFragmentPositionFileName );

	flw::Put( _Multimemory->S_.FreeFragment, OFlow );
	flw::Put( _Multimemory->S_.TailingFreeFragmentPosition, OFlow );
ERRErr
ERREnd
ERREpilog
}

