/*
	'frdbse.cpp' by Claude SIMON (http://zeusw.org/).

	'frdbse' is part of the Epeios framework.

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

#define FRDBSE__COMPILATION

#include "frdbse.h"

/******************************************************************************/
				  /* do not modify anything above this limit */
				  /*			  unless specified			 */
				  /*******************************************/

#include "stsfsm.h"

using namespace frdbse;

#define C( name ) case pt##name: return #name; break

const char *frdbse::GetLabel( project_type__ ProjectType )
{
	switch ( ProjectType ) {
	C( New );
	C( Predefined );
	C( User );
	default:
		ERRFwk();
		break;
	}

	return NULL;	// Pour �viter un 'warning'.
}

static stsfsm::automat ProjectAutomat_;

static void FillProjectAutomat_( void )
{
	ProjectAutomat_.Init();
	stsfsm::Fill( ProjectAutomat_, pt_amount, GetLabel );
}

project_type__ frdbse::GetProjectType( const str::string_ &Pattern )
{
	return stsfsm::GetId( Pattern, ProjectAutomat_, pt_Undefined, pt_amount );
}

#undef C

#define C( name ) case bt##name: return #name; break

const char *frdbse::GetLabel( backend_type__ BackendType )
{
	switch ( BackendType ) {
	C( Daemon );
	C( Embedded );
	C( Predefined );
	default:
		ERRFwk();
		break;
	}

	return NULL;	// Pour �viter un 'warning'.
}

static stsfsm::automat BackendAutomat_;

static void FillBackendAutomat_( void )
{
	BackendAutomat_.Init();
	stsfsm::Fill( BackendAutomat_, bt_amount, GetLabel );
}

backend_type__ frdbse::GetBackendType( const str::string_ &Pattern )
{
	return stsfsm::GetId( Pattern, BackendAutomat_, bt_Undefined, bt_amount );
}

static void FillAutomats_( void )
{
	FillProjectAutomat_();
	FillBackendAutomat_();
}

/* Although in theory this class is inaccessible to the different modules,
it is necessary to personalize it, or certain compiler would not work properly */

class frdbsepersonnalization
{
public:
	frdbsepersonnalization( void )
	{
		FillAutomats_();
		/* place here the actions concerning this library
		to be realized at the launching of the application  */
	}
	~frdbsepersonnalization( void )
	{
		/* place here the actions concerning this library
		to be realized at the ending of the application  */
	}
};


				  /********************************************/
				  /* do not modify anything belove this limit */
				  /*			  unless specified		   	  */
/******************************************************************************/

static frdbsepersonnalization Tutor;
