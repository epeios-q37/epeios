/*
	'xulfbs.cpp' by Claude SIMON (http://zeusw.org/).

	'xulfbs' is part of the Epeios framework.

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

#define XULFBS__COMPILATION

#include "xulfbs.h"

/******************************************************************************/
				  /* do not modify anything above this limit */
				  /*			  unless specified			 */
				  /*******************************************/

#include "xulftk.h"

using namespace xulfbs;

static void _RetrieveErrAndReport( xulftk::trunk___ &Trunk )
{
	err::buffer__ Buffer;

	Trunk.UI().LogAndPrompt( err::Message( Buffer ) );
}
 

void xulfbs::_Report(
	xulftk::trunk___ &Trunk,
	const char *Message )
{
	if ( Message != NULL )
		Trunk.UI().LogAndPrompt( Message );
	else {	// L'erreur a t dtecte dans un contexte o les informations ka concernant ne sont pas disponibles, d'o traitement ici.
		switch (  ERRType ) {
		case err::t_Abort:
			break;
		case err::t_Return:
			ERRFwk();
			break;
		default:
			_RetrieveErrAndReport( Trunk );
			break;
		}

		ERRRst();
	}
}

/* Although in theory this class is inaccessible to the different modules,
it is necessary to personalize it, or certain compiler would not work properly */

class xulfbspersonnalization
{
public:
	xulfbspersonnalization( void )
	{
		/* place here the actions concerning this library
		to be realized at the launching of the application  */
	}
	~xulfbspersonnalization( void )
	{
		/* place here the actions concerning this library
		to be realized at the ending of the application  */
	}
};


				  /********************************************/
				  /* do not modify anything belove this limit */
				  /*			  unless specified		   	  */
/******************************************************************************/

static xulfbspersonnalization Tutor;
