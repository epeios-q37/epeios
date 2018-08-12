<?php
/*
	Copyright (C) 2018 Claude SIMON (http://q37.info/contact/).

	This file is part of XDHq.

	WDHq is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

	XDHq is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with XDHq If not, see <http://www.gnu.org/licenses/>.
*/

function getAtlas() {
	if (getenv("EPEIOS_SRC") === false)
		$zndq_path = realpath(dirname(__FILE__)) . '/';
	else {
		switch (strtoupper(substr(php_uname('s') , 0, 3))) {
		case "WIN":
			$epeios_path = "h:\\hg\\epeios\\";
		break;
		case "LIN":
			$epeios_path = "/home/csimon/hg/epeios/";
		break;
		case "DAR":
			$epeios_path = "/Users/csimon/hg/epeios/";
		break;
		default:
			echo "Unknown OS !!!\n";
			break;
		}

		$zndq_path = $epeios_path . "tools/xdhq/Atlas/ZND/";
	}

	require( $zndq_path . "Atlas.php");
}

getAtlas();

class DOM extends AtlasDOM {
	public $exclude = NULL;
	public $id = -1;
	public $todos = [
		[
			'completed' => true,
			'label' => "Note 1"
		],
		[
			'completed' => false,
			'label' => "Note 2"
		]
	];
	public function itemsLeft() {
		$i = count( $this->todos );
		$count = 0;

		while( $i-- )
			if ( !$this->todos[$i]['completed'])
				$count++;

		return $count;
	}
}

function push( $todo, $id, &$tree ) {
	$tree .= "<Todo";
//	$tree->pushTag( 'Todo' );

	$tree .= " id=\"" . $id . "\"";
//	$tree->putAttribute ('id', $id );

	if ( $todo['completed']) {
		$tree .= " completed=\"true\"";
//		$tree->putAttribute( 'completed', 'true' );
	} else {
		$tree .= " completed=\"false\"";

//		$tree->putAttribute( 'completed', 'false');
	}

	$tree .= ">";
	$tree .= htmlspecialchars( $todo['label'] );
//	$tree->putValue( $todo['label']);

	$tree .= "</Todo>\n";
//	$tree->popTag();
}

function displayCount( $dom, $count ) {
	$text = "";

	switch ( $count ) {
	case 0:
		break;
	case 1:
		$text = "1 item left";
		break;
	default:
		$text = $count . " items left";
		break;
	}

	$dom->setContent( "Count", $text );
}

function handleCount( $dom ) {
	$count = $dom->itemsLeft();

	if ( $count != count( $dom->todos ) )
		$dom->disableElement( "HideClearCompleted");
	else
		$dom->enableElement( "HideClearCompleted");

	displayCount( $dom, $count );
}

function displayTodos( $dom ) {
	$tree = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<XDHTML>\n<Todos>\n";
	$i = 0;
	$count = count( $dom->todos );

//	$tree->pushTag( "Todos");

	while( $i < $count ) {
		push( $dom->todos[$i], $i, $tree );

		$i++;
	}

	$tree .= "</Todos>\n</XDHTML>";
//	$tree->popTag();

	$dom->setLayoutXSL( "Todos", $tree, "Todos.xsl" );
	handleCount( $dom );
}

function submitNew( $dom ) {
	$content = $dom->getContent( "Input");
	$dom->setContent( "Input", "" );

	if ( trim( $content ) != "" ) {
		array_unshift( $dom->todos, [
			'completed' => false,
			'label' => $content
		] );
		displayTodos( $dom );
	}
}

function submitModification( $dom) {
	$id = $dom->id;
	$dom->id = -1;

	$content = $dom->getContent( "Input." . $id );
	$dom->setContent( "Input." . $id, "" );

	if ( trim( $content) != "" ) {
		$dom->todos[$id]['label'] = $content;

		$dom->setContent( "Label." . $id, $content );

		$dom->removeClasses( [
			'View.' . $id => "hide",
			'Todo.' . $id => "editing"
			] );
	} else {
		array_splice( $dom->todos, $id, 1 );
		displayTodos( $dom );
	}
}

function toggle( $dom, $id ) {
	$i = intval( $id );

	$dom->todos[$i]['completed'] = !$dom->todos[$i]['completed'];

	$dom->toggleClass( "Todo." . $id, "completed" );
	$dom->toggleClass( "Todo." . $id, "active" );

	handleCount( $dom );
}

function all( $dom ) {
	$dom->exclude = null;

	$dom->addClass( "All", "selected");
	$dom->removeClasses( [
		'Active' => "selected",
		'Completed' => "selected" 
	]);

	$dom->disableElements( ["HideActive", "HideCompleted"]);
}

function active( $dom ) {
	$dom->exclude = true;

	$dom->addClass( "Active", "selected");
	$dom->removeClasses( [
		'All' => "selected",
		'Completed' => "selected" 
	]);

	$dom->disableElement( "HideActive");
	$dom->enableElement( "HideCompleted");

}

function completed( $dom ) {
	$dom->exclude = false;

	$dom->addClass( "Completed", "selected");
	$dom->removeClasses( [
		'All' => "selected" ,
		'Active' => "selected"
	]);

	$dom->enableElement( "HideActive");
	$dom->disableElement( "HideCompleted");
}

function clear( $dom ) {
	$i = 0;
	$count = count( $dom->todos );

	while ( $i < $count ) {
		if ( $dom->todos[$i]['completed']) {
			array_splice( $dom->todos, $i, 1 );
			$count--;
		} else
			$i++;
	}

	displayTodos( $dom );
}

function edit( $dom, $id ) {
	$content = $dom->getContent( $id );
	$dom->id = intval( $content);

	$dom->addClasses( [
		"View." . $content => "hide",
		$id => "editing"
	] );

	$dom->setContent( "Input." . $content, $dom->todos[$dom->id]['label']);
	$dom->focus( "Input." . $content );
}

function cancel( $dom ) {
	$id = $dom->id;
	$dom->id = -1;

	$dom->setContent(  "Input." . $id, "" );
	$dom->removeClasses( [
		'View.' . $id => 'hide',
		'Todo.' . $id => 'editing'
	]);
}

function main() {
	$type = null;

	if ( Atlas::isDev() )
		Atlas::launch( "Connect", null, "TodoMVC" );
	else
		Atlas::launch( "Connect", null, "." );

	$dom = new DOM();

	while ( true ) {
		switch( $dom->getAction( $id ) ) {
		case "Connect":
			$dom->headUp( Atlas::readAsset( "HeadDEMO.html" ) );
			$dom->setLayout( "", Atlas::readAsset( "Main.html" ) );
			$dom->focus( "Input" );
			$dom->disableElements( ["HideActive", "HideCompleted"]);
			displayTodos( $dom );
			break;
		case "Submit":
			if ( $dom->id == -1 )
				submitNew( $dom );
			else
				submitModification( $dom );
			break;
		case "Destroy":
			array_splice( $dom->todos, intval( $dom->getContent( $id ) ), 1 );
			displayTodos( $dom );
			break;
		case "Toggle":
			toggle( $dom, $id );
			break;
		case "All":
			all( $dom );
			break;
		case "Active":
			active( $dom );
			break;
		case "Completed":
			completed( $dom );
			break;
		case "Clear":
			clear( $dom );
			break;
		case "Edit":
			edit( $dom, $id );
			break;
		case "Cancel":
			cancel( $dom );
			break;
		default:
			die( "???" );
			break;
		}
	}
}

main();
?>
