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

function pack(originalString) {
  const compressed = pako.deflate(originalString, { to: 'string' });
  
  let binaryString = '';

  for (let i = 0; i < compressed.length; i++) {
      binaryString += String.fromCharCode(compressed[i]);
  }
  
  return encodeURIComponent(btoa(binaryString));
}

function unpack(packedCode) {
  const binaryString = atob(decodeURIComponent(packedCode));
  
  const len = binaryString.length;
  const bytes = new Uint8Array(len);

  for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
  }

  return pako.inflate(bytes, { to: 'string' });
}
