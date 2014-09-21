/*
	'sclfrntnd.h' by Claude SIMON (http://zeusw.org/).

	'sclfrntnd' is part of the Epeios framework.

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

#ifndef SCLFRNTND__INC
# define SCLFRNTND__INC

# define SCLFRNTND_NAME		"SCLFRNTND"

# if defined( E_DEBUG ) && !defined( SCLFRNTND_NODBG )
#  define SCLFRNTND_DBG
# endif

/******************************************************************************/
				  /* do not modify anything above this limit */
				  /*			  unless specified			 */
				  /*******************************************/

// SoCLe FRoNTeND

# include "frdkrn.h"

# include "err.h"
# include "flw.h"
# include "xml.h"

namespace sclfrntnd {
	void Report(
		frdkrn::kernel___ &Kernel,
		const char *Message );

	void Notify(
		frdkrn::kernel___ &Kernel,
		const char *Message );

	void GetPredefinedProjects( xml::writer_ &Writer );

	void GetPredefinedBackends( xml::writer_ &Writer );

	const str::string_ &GetProjectFileName(
		const str::string_ &Id,
		str::string_ &FileName );
}

				  /********************************************/
				  /* do not modify anything belove this limit */
				  /*			  unless specified		   	  */
/******************************************************************************/

#endif
