/*
	Copyright (C) 1999-2017 Claude SIMON (http://q37.info/contact/).

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

#define XDHUJR__COMPILATION

#include "xdhujr.h"

#include "sclrgstry.h"

using namespace xdhujr;

using rgstry::entry___;

entry___ xdhujr::CustomItems( "CustomItems", sclrgstry::Definitions );

entry___ xdhujr::custom_item::AttributeNames("AttributeNames", CustomItems );
entry___ xdhujr::custom_item::attribute_name::Widget( "Widget", AttributeNames );
entry___ xdhujr::custom_item::attribute_name::Result( "Result", AttributeNames );
/*
entry___ xdhujr::custom_item::attribute_name::OnEvent( "OnEvent", AttributeNames );
entry___ xdhujr::custom_item::attribute_name::OnEvents( "OnEvents", AttributeNames );
entry___ xdhujr::custom_item::attribute_name::Cast( "Cast", AttributeNames );
entry___ xdhujr::custom_item::attribute_name::Casts( "Casts", AttributeNames );
*/


entry___ xdhujr::Scripts( "Scripts", sclrgstry::Definitions );

static entry___ PropertyScripts_( "Property", xdhujr::Scripts );
entry___ xdhujr::script::property::Setter( "Setter", PropertyScripts_ );
entry___ xdhujr::script::property::Getter( "Getter", PropertyScripts_ );

static entry___ AttributeScripts_( "Attribute", xdhujr::Scripts );
entry___ xdhujr::script::attribute::Setter( "Setter", AttributeScripts_ );
entry___ xdhujr::script::attribute::Getter( "Getter", AttributeScripts_ );
entry___ xdhujr::script::attribute::Remover( "Remover", AttributeScripts_ );

static entry___ ContentScripts_( "Content", xdhujr::Scripts );
entry___ xdhujr::script::content::Setter( "Setter", ContentScripts_ );
entry___ xdhujr::script::content::Getter( "Getter", ContentScripts_ );

entry___ xdhujr::script::ElementFiller( "ElementFiller", xdhujr::Scripts );
entry___ xdhujr::script::DocumentFiller( "DocumentFiller", xdhujr::Scripts );
entry___ xdhujr::script::CastingsFiller( "CastingsFiller", xdhujr::Scripts );

entry___ xdhujr::script::DraggableSetter( "DraggableSetter", xdhujr::Scripts );
entry___ xdhujr::script::DroppableSetter( "DroppableSetter", xdhujr::Scripts );

static entry___ DialogScripts_( "Dialog", xdhujr::Scripts );
entry___ xdhujr::script::dialog::Alert( "Alert", DialogScripts_ );
entry___ xdhujr::script::dialog::Confirm( "Confirm", DialogScripts_ );

static entry___ WidgetScripts_( "Widget", xdhujr::Scripts );
entry___ xdhujr::script::widget::ContentRetriever( "ContentRetriever", WidgetScripts_ );
entry___ xdhujr::script::widget::Focuser( "Focuser", WidgetScripts_ );
entry___ xdhujr::script::widget::Selector( "Selector", WidgetScripts_ );

entry___ xdhujr::script::Log( "Log", xdhujr::Scripts );
entry___ xdhujr::script::Focuser( "Focuser", Scripts );
entry___ xdhujr::script::Selector( "Selector", Scripts );
entry___ xdhujr::script::EventHandlersSetter( "EventHandlersSetter", Scripts );
entry___ xdhujr::script::CastsSetter( "CastsSetter", Scripts );
entry___ xdhujr::script::WidgetsInstantiator( "WidgetsInstantiator",Scripts );


