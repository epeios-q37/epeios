/*
	'ags.cpp' by Claude SIMON (http://zeusw.org/).

	'ags' is part of the Epeios framework.

    The Epeios framework is free software: you can redistribute it and/or
	modify it under the terms of the GNU General Public License as published
	by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The Epeios framework is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with The Epeios framework.  If not, see <http://www.gnu.org/licenses/>.
*/

#define AGS__COMPILATION

#include "ags.h"

/******************************************************************************/
				  /* do not modify anything above this limit */
				  /*			  unless specified			 */
				  /*******************************************/

using namespace ags;

void aggregated_storage_driver__::_Free( void )
{
	if ( _Descriptor != AGS_UNDEFINED_DESCRIPTOR )
		_AStorage->Free( _Descriptor );
}

void aggregated_storage_driver__::SDRAllocate( sdr::size__ Size )
{
	_Descriptor = _AStorage->Reallocate( _Descriptor, Size );
}


sdr::size__ aggregated_storage_driver__::SDRSize( void ) const
{
	if ( _Descriptor != AGS_UNDEFINED_DESCRIPTOR )
		return _AStorage->Size( _Descriptor );
	else
		return 0;
}

void aggregated_storage_driver__::SDRRecall(
	sdr::row_t__ Position,
	sdr::size__ Amount,
	sdr::datum__ *Buffer )
{
	_AStorage->Read( _Descriptor, Position, Amount, Buffer );
}
// lit � partir de 'Position' et place dans 'Tampon' 'Nombre' octets;
void aggregated_storage_driver__::SDRStore(
	const sdr::datum__ *Buffer,
	sdr::size__ Amount,
	sdr::row_t__ Position )
{
	_AStorage->Write( Buffer, Amount, _Descriptor, Position );
}


void ags::aggregated_storage_::DisplayStructure( txf::text_oflow__ &Flow ) const
{
	sdr::row_t__ Row = 0;
	header__ Header;

	status__ PStatus = s_Undefined;

	if ( _Size() != 0 )
		PStatus = _TailFragmentStatus();

	while ( Row < _Size() ) {
		_Display( Row, PStatus, Flow );

		_Get( Row, Header );
		PStatus = Status( Header );

		Row += _GetFragmentSize( Row );

		Flow << txf::tab;

	}

	Flow << '(' << Storage.Size() << ')' << txf::nl;
}


/* Although in theory this class is inaccessible to the different modules,
it is necessary to personalize it, or certain compiler would not work properly */

class agspersonnalization
{
public:
	agspersonnalization( void )
	{
		if ( sizeof( header__ ) != AGS__HEADER_SIZE )
			ERRChk();
		/* place here the actions concerning this library
		to be realized at the launching of the application  */
	}
	~agspersonnalization( void )
	{
		/* place here the actions concerning this library
		to be realized at the ending of the application  */
	}
};

				  /********************************************/
				  /* do not modify anything belove this limit */
				  /*			  unless specified		   	  */
/******************************************************************************/

static agspersonnalization Tutor;
