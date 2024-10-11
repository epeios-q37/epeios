/*
	Copyright (C) 2021 Claude SIMON (http://q37.info/contact/).

	This file is part of the 'ucuqm' tool.

    'ucuqm' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'ucuqm' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'ucuqm'.  If not, see <http://www.gnu.org/licenses/>.
*/


#include "registry.h"

#include "sclm.h"

using namespace registry;

#define D(name)  rEntry registry::parameter::name(#name, sclr::Parameters)

D(HostService);
D(Token);
D(Id);
D(In);
D(Expression);
D(NewProxy);
D(NewToken);
D(VirtualToken);
D(VirtualTokenId);

#undef D

namespace definition_ {
  rgstry::rEntry Scripts_("Scripts", sclr::Definitions);
  namespace scripts_ {
    rgstry::rEntry LooseScript_("Script", Scripts_);
  }
}

rEntry registry::definition::scripts::TaggedScript(RGSTRY_TAGGING_ATTRIBUTE("Label"), definition_::scripts_::LooseScript_);
rEntry registry::definition::scripts::TaggedScriptExpression("@Expression", registry::definition::scripts::TaggedScript);

const str::dString &registry::GetScript(
  const str::dString &Label,
  str::dString &Script)
{
  return sclm::MGetValue(rgstry::rTEntry(definition::scripts::TaggedScript, Label), Script);
}

const str::dString &registry::GetScriptExpression(
  const str::dString &Label,
  str::dString &Expression)
{
  sclm::OGetValue(rgstry::rTEntry(definition::scripts::TaggedScriptExpression, Label), Expression);

  return Expression;
}
