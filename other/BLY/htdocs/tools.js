function string2Id(input) {
  // Si la chaîne commence par un chiffre, ajoute un underscore au début  
  // Remplacer les underscores par deux underscores  
  input = input.replace(/_/g, '__');

  if (/^\d/.test(input)) {
    input = '_' + input;
  }

  // Remplacer les caractères non alphanumériques (à l'exception de l'underscore)
  input = input.replace(/[^a-zA-Z0-9_]/g, (match) => {
      return '_' + match.charCodeAt(0).toString(16);
  });

  return input;
}

function stringOrInt(input) {
  const asInt = parseInt(input, 10);

  return isNaN(asInt) ? `"${input}"` : asInt;
}

// XML Blockly code compressed with 'Q_Compress'.
function unpackXMLCode(base64CompressedCode) {

  console.log(base64CompressedCode)
  // Décoder le base64  
  const binaryString = atob(base64CompressedCode);
  
  // Convertir la chaîne binaire en tableau d'octets  
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
  }

  // Décompresser les données  
  return pako.inflate(bytes, { to: 'string' });
}
