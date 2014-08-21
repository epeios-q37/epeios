/*
	'sclwebkit.cpp' by Claude SIMON (http://zeusw.org/).

	'sclwebkit' is part of the Epeios framework.

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

#define SCLWEBKIT__COMPILATION

#include "sclwebkit.h"

/******************************************************************************/
				  /* do not modify anything above this limit */
				  /*			  unless specified			 */
				  /*******************************************/

#include "flf.h"
#include "sclmisc.h"

using namespace sclwebkit;

#ifdef CPE_WIN
# define FUNCTION_SPEC __declspec(dllexport)
#else
#define FUNCTION_SPEC
# endif

void sclwebkit::Load(
	const rgstry::entry___ &FileName,
	str::string_ &String )
{
	sclmisc::Load( FileName, sclrgstry::GetRegistry(), String );
}

#define DEF( name, function ) extern "C" FUNCTION_SPEC function name

DEF( WKCLLBCK_LAUNCH_FUNCTION_NAME, wkcllbck::launch );

wkcllbck::downstream_callback__ *WKCLLBCKLaunch( const wkcllbck::shared_data__ &Data )
{
	return sclwebkit::SCLWEBKITLaunch( Data.Callback() );
}

/* Although in theory this class is inaccessible to the different modules,
it is necessary to personalize it, or certain compiler would not work properly */

class sclwebkitpersonnalization
{
public:
	sclwebkitpersonnalization( void )
	{
		/* place here the actions concerning this library
		to be realized at the launching of the application  */
	}
	~sclwebkitpersonnalization( void )
	{
		/* place here the actions concerning this library
		to be realized at the ending of the application  */
	}
};


				  /********************************************/
				  /* do not modify anything belove this limit */
				  /*			  unless specified		   	  */
/******************************************************************************/

static sclwebkitpersonnalization Tutor;
