/*
	Copyright (C) 2015-2016 Claude SIMON (http://q37.info/contact/).

	This file is part of 'orgnzq' software.

    'orgnzq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'orgnzq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'orgnzq'.  If not, see <http://www.gnu.org/licenses/>.
*/

// 'text' plugin.

#include "ogzinf.h"

#include "sclmisc.h"
#include "sclplugin.h"

#include "cmnplgn.h"

#define PLUGIN_NAME	"Date"

typedef cmnplgn::sPlugin sPlugin_;

class sPlugin
: public sPlugin_
{
protected:
	virtual void FRDCLLBCKToXML(
		const str::dString &Input,
		str::dString &Output ) override
	{
		Output = Input;
	}
public:
	bso::sBool SCLPLUGINInitialize( plgn::sAbstract *Abstract )
	{
		if ( Abstract != NULL )
			qRGnr();

		Init();

		return true;
	}
};

SCLPLUGIN_DEF( sPlugin );

const char *sclmisc::SCLMISCTargetName = PLUGIN_NAME;
const char *sclmisc::SCLMISCProductName = OGZINF_MC_AFFIX;

void sclplugin::SCLPLUGINPluginIdentifier( str::dString &Identifier )
{
	Identifier.Append( IDENTIFIER );
}

void sclplugin::SCLPLUGINPluginDetails( str::dString &Details )
{
	Details.Append( PLUGIN_NAME " V" VERSION " - Build " __DATE__ " " __TIME__ " (" );
	Details.Append( cpe::GetDescription() );
	Details.Append( ')' );
}
